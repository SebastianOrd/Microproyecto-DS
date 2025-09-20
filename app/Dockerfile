# syntax=docker/dockerfile:1
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /srv/app

# Instala dependencias del dashboard (archivo dentro de /app)
COPY requirements_dashboard.txt /tmp/requirements.txt
RUN pip install --upgrade pip -v \
 && pip install --no-cache-dir -r /tmp/requirements.txt

# Copiamos solo lo necesario para el dashboard

COPY . /srv/app/

# Streamlit respetará PORT que inyecte Railway / el run local
ENV PORT=8501
EXPOSE 8501

# La URL de la API la pasaremos por env en runtime (API_URL)
CMD ["sh", "-c", "streamlit run app/app_streamlit.py --server.address 0.0.0.0 --server.port ${PORT}"]