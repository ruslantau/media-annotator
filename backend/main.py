import json
import urllib.request
import wave
import zipfile
import shutil
from pathlib import Path
from typing import List

import uvicorn
import pandas as pd
from fastapi import FastAPI, Request, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from vosk import Model, KaldiRecognizer
from utils import get_models_table, ProjectManager

BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR.parent / 'data'
MODELS_DIR = DATA_DIR / "models"
UPLOADS_DIR = DATA_DIR / "uploads"

for path in [UPLOADS_DIR, MODELS_DIR]:
    path.mkdir(exist_ok=True, parents=True)

app = FastAPI()
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
project_manager = ProjectManager(DATA_DIR / 'projects.json')


@app.get("/")
async def get_all_urls():
    url_list = [{"path": route.path, "name": route.name} for route in app.routes]
    return url_list


@app.get("/projects")
@app.get("/projects/{id}")
async def projects(id: str = None) -> JSONResponse:
    project_manager.read()
    if id is None:
        return JSONResponse(content=list(project_manager.projects_dict.values()))
    else:
        return JSONResponse(content=project_manager.projects_dict[id])


@app.delete("/projects/{id}")
async def projects(id: str = None) -> JSONResponse:
    project_manager.read()
    project_manager.remove_project(id)
    project_uploads_dir = UPLOADS_DIR / id
    shutil.rmtree(project_uploads_dir)
    return JSONResponse(content='Project successfully removed.', status_code=200)


@app.put("/projects/{id}")
async def update_annotations(id: str, new_data: Request) -> JSONResponse:
    data_json = await new_data.json()
    project_manager.read()
    project = project_manager.projects_dict[id]
    project['name'] = data_json['name']
    project_manager.update_project(project)
    return JSONResponse(content='Data was updated.', status_code=200)


@app.put("/projects/{id}/annotations")
async def update_annotations(id: str, new_data: Request) -> JSONResponse:
    data_json = await new_data.json()
    project_manager.read()
    project = project_manager.projects_dict[id]
    project['data'] = data_json
    project_manager.update_project(project)
    return JSONResponse(content='Data was updated.', status_code=200)


@app.get("/annotate")
async def annotate(input_file_path: str, model_dir_name: str):
    model_dir_path = MODELS_DIR / model_dir_name
    model_zip_path = model_dir_path.with_suffix(model_dir_path.suffix + '.zip')
    input_file_path = UPLOADS_DIR / input_file_path

    print(input_file_path, model_dir_name)
    if not model_dir_path.exists():
        if not model_zip_path.exists():
            try:
                base_url = 'https://alphacephei.com/vosk/models/'
                print(base_url + model_zip_path.name)
                urllib.request.urlretrieve(base_url + model_zip_path.name, model_zip_path)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Model could not be loaded. \nERROR: {e}")
        try:
            with zipfile.ZipFile(model_zip_path, 'r') as zip_ref:
                zip_ref.extractall(MODELS_DIR)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Can't unzip model files. \nERROR: {e}")
    if not input_file_path.exists():
        raise HTTPException(status_code=404, detail="Input files not found.")

    wf = wave.open(input_file_path.as_posix(), "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        exit(1)

    model = Model(model_dir_path.as_posix())
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        rec.AcceptWaveform(data)

    result_json = json.loads(rec.FinalResult())

    sentence_length_in_seconds = 10
    between_sentences_delay_threshold = [0.08, 100]
    words_df = pd.DataFrame(result_json['result'])
    words_df['duration'] = words_df['end'] - words_df['start']
    words_df['sentence_id'] = words_df['duration'].cumsum()
    words_df['sentence_id'] = (words_df['sentence_id'] // sentence_length_in_seconds).astype(int)
    words_df['delay'] = words_df['start'].shift(-1) - words_df['end']
    words_df['i'] = words_df['delay'].between(left=between_sentences_delay_threshold[0], right=between_sentences_delay_threshold[1])

    sentences_df = words_df.groupby('sentence_id').agg({'word': ' '.join,
                                                        'start': min,
                                                        'end': max,
                                                        'duration': sum,
                                                        'conf': pd.Series.mean,
                                                        }).rename(columns={'word': 'sentence'})
    sentences_df['data'] = sentences_df[['sentence', 'conf']].apply(lambda row: {'text': row['sentence'],
                                                                               'conf': row['conf']}, axis=1)
    sentences_df = sentences_df.drop(columns=['sentence'])
    sentences_df['color'] = 'rgba(0,255,0,0.1)'
    sentences_df['id'] = 'region_' + sentences_df.index.astype(str)
    return sentences_df.to_dict(orient='records')


@app.get("/models")
def get_models_list():
    models_df = get_models_table()
    models_df = models_df.reset_index()
    models_df = models_df.rename(columns={'Model': 'value', 'index': 'key'})
    models_df['title'] = models_df['value'] + ' | Size:' + models_df['Size']

    result_list = []
    for language, group_df in models_df.groupby('Language'):
        # group_df['scopedSlots'] = [{"title": "title"}] * len(group_df)
        row = dict(title=language,
                   value=language,
                   key=language,
                   selectable=False,
                   children=json.loads(group_df.to_json(orient='records')))
        result_list.append(row)

    return result_list


@app.get("/uploads/{filepath}", response_class=FileResponse)
def get_uploaded_file(filepath: str):
    path = UPLOADS_DIR / filepath
    return FileResponse(path)


@app.post("/uploads")
async def upload_files(files: List[UploadFile] = File(...), metadata: str = Form(...)):
    new_id = project_manager.max_project_id + 1
    project = dict(id=new_id,
                   name=f"Project {new_id}",
                   data=[])

    metadata = json.loads(metadata)
    project_uploads_dir = UPLOADS_DIR / str(new_id)
    for i, file in enumerate(files):
        contents = await file.read()
        file_path = project_uploads_dir / metadata['paths'][i]
        file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, 'wb') as f:
            f.write(contents)
        project['data'].append({'file_path': file_path.as_posix(),
                                'annotations': [],
                                'file_url': metadata['paths'][i]
                                })

    try:
        project_manager.add_project(project)
    except Exception as e:
        project_manager.remove_project(new_id)
        shutil.rmtree(project_uploads_dir)
        raise HTTPException(status_code=500, detail=f"Project creating failed. \nERROR: {e}")

    return project


if __name__ == "__main__":
    uvicorn.run("__main__:app",
                host="localhost",
                port=8000,
                reload=True,
                workers=2
                )
