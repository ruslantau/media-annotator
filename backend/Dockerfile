FROM mambaorg/micromamba:1.4.2

EXPOSE 8000

COPY --chown=$MAMBA_USER:$MAMBA_USER backend /home/backend
WORKDIR /home/backend

RUN micromamba install -y -n base -f environment.yaml && \
    micromamba clean --all --yes

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]