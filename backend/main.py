from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json

DATA_DIR = Path("../data")
UPLOADS_DIR = DATA_DIR / "uploads"
PROJECTS_DIR = DATA_DIR / "projects"
for path in [UPLOADS_DIR, PROJECTS_DIR]:
    path.mkdir(exist_ok=True, parents=True)

app = FastAPI()
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def get_all_urls():
    url_list = [{"path": route.path, "name": route.name} for route in app.routes]
    return url_list


@app.get("/projects")
@app.get("/projects/{id}")
async def projects(id: int = None):
    if (PROJECTS_DIR / 'projects.json').exists():
        with open(PROJECTS_DIR / 'projects.json', mode='r', encoding='utf-8') as f:
            projects = f.read()
    else:
        projects = []

    if id is None:
        return projects
    else:
        return projects

@app.get("/uploads/{filepath}", response_class=FileResponse)
def get_uploaded_file(filepath: str):
    path = UPLOADS_DIR / filepath
    return FileResponse(path)
