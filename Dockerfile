FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# 1) Deps del MODELO
COPY model_requirements.txt /app/model_requirements.txt
RUN python -m pip install --upgrade pip && pip install -r /app/model_requirements.txt

# 2) Copia el wheel ANTES de instalar api_requirements
COPY dist/ /app/dist/
# (Opcional) falla temprano si no llegó el wheel
RUN test -f /app/dist/calidad_aire_model-0.2.0-py3-none-any.whl || (echo "Falta el wheel en /app/dist" && ls -R /app/dist && exit 1)

# 3) Instala deps de la API 
COPY api_requirements.txt /app/api_requirements.txt
RUN pip install -r /app/api_requirements.txt

# 4) Resto del código y modelo local (si aplica)
COPY . /app
ENV MODEL_URI="file:/app/dist"
EXPOSE 8001
CMD ["uvicorn","app_api.main:app","--host","0.0.0.0","--port","8001"]