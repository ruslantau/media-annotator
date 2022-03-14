# media-annotator
Web-based annotation tool for media data.

Currently, only `.wav` `.mp3` files supported.

For auto annotation will be used the first channel of `.mp3`.

![](./img/mediaView.png)

## TODO
- extend the list of supported formats (`mp3,mp4,flac,avi,etc.`)
- feature to exporting annotations as `.csv`
- feature to exporting audio regions as audio files as `archive.zip`

## Installation
Clone repository, create python environment using conda manager and activate it

    git clone https://github.com/ruslantau/media-annotator
    cd annotator
    conda env create -f backend/environment.yaml
    conda activate annotator

Run FastAPI backend

    python backend/main.py

Run Nuxt frontend and open http://localhost:3000/projects

    npm run build --prefix frontend && npm run start --prefix frontend
