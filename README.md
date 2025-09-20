# 🌍 Proyección de Calidad de Aire en Risaralda

Este repositorio contiene el código, datos y documentación del microproyecto **“Proyección de calidad de aire utilizando partículas PM10 y PM2.5 en Risaralda, Colombia”**, desarrollado como parte del curso de Desarrollo de Soluciones de la maestria MAIA de la Universidad de los Andes

---

## Resumen

La calidad del aire es un factor determinante para la salud y el bienestar de las personas. En el departamento de Risaralda (Colombia), los material particulados **PM10 y PM2.5** son unos de los principales contaminantes, asociados a problemas respiratorios y cardiovasculares.  

Este proyecto utiliza **datos históricos (2007–2023)** de monitoreo de calidad del aire, proporcionados por la **Corporación Autónoma Regional de Risaralda**, para proyectar concentraciones futuras de PM10 y PM2.5.  

El propósito es **anticipar escenarios de riesgo** y ofrecer insumos para la gestión ambiental y la toma de decisiones.

---

## Objetivos

### Objetivo general
Desarrollar una aplicación que permita identificar las posibles tendencias del comportamiento de la calidad del aire en Risaralda.

### Objetivos específicos
- Entrenar un **modelo de aprendizaje automático** que estime concentraciones futuras de PM10 y PM2.5.  
- Implementar una aplicación interactiva para seleccionar rangos de fechas y visualizar proyecciones.  
- Generar documentación y repositorio abierto con datos procesados, scripts y resultados.  

---

## Equipo de trabajo

- Brayan Sthefen Gomez Salamanca
- Juan Sebastian Ordoñez Acuña 
- Maria Alejandra Rojas Garzon  
- Hainer Jair Torrenegra Jimenez

Afiliación: Universidad de los Andes  
Licencia de datos: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)  

---

## Estructura del repositorio

```
Microproyecto-DS/
├── .circleci/
│   └── config.yml               # Configuración de CI/CD con CircleCI
├── .dvc/                        # Metadata de DVC
├── .tox/                        # Entornos tox
├── .venv/                       # Virtualenv (ignorado en git)
│
├── app/                         # Dashboard con Streamlit
│   ├── app_streamlit.py
│   ├── Dockerfile               # Dockerfile específico del dashboard
│   └── requirements_dashboard.txt
│
├── app_api/                     # API con FastAPI
│   ├── main.py
│   └── api_requirements.txt
│
├── build/                       # Builds temporales (wheel, sdist)
├── dist/                        # Distribuciones empaquetadas (.tar.gz, .whl)
│
├── data/
│   ├── raw/                     # Datos originales (solo lectura)
│   ├── processed/               # Datos enriquecidos/intermedios
│
├── notebooks/
│   ├── 01_eda.ipynb             # EDA principal con gráficas + resúmenes
│   ├──compare_models_mlflow.py  #Grid de comparacion de diferentes modelos en MLflow
│   ├──XGB vs ELASTIC.py         #Comparacion especifica de modelos en Mlflow
│
├── src/
│   ├── eda.py                   # Script principal en python
│   └── calidad_aire/            # Paquete con pipelines de entrenamiento
│       ├── train_pipeline.py
│       ├── processing/
│       └── config/
│
├── reports/
│   ├── figures/                 # Imágenes exportadas
│   ├── resumen_por_municipio.csv
│   └── resumen_por_estacion.csv
│
├── docs/
│   ├── Entrega_1.docx           # Documento de la primera entrega
│   └── Entraga_2.docx           # Documento de la segunda entrega
│
├── .dvcignore
├── .env                         # Variables de entorno (no subir a git)
├── .gitignore
├── Dockerfile                   # Dockerfile raíz (API por defecto)
├── MANIFEST.in
├── model_requirements.txt       # Dependencias específicas para entrenamiento
├── requirements.txt             # Dependencias mínimas generales
├── README.md                    # Descripción del proyecto
├── setup.py                     # Script de instalación
└── tox.ini                      # Configuración de tox
```

---
## Requisitos

- Python 3.13.7
- Git
- DVC (con soporte para S3 y credenciales de conexion)
- AWS CLI configurado

##  Instalación y uso

Proyecto probado en Python 3.13.7

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/TU_USUARIO/Microproyecto-DS.git
   cd Microproyecto-DS

   
2.	Crear y activar entorno virtual:
    ```   
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.	Obtener los datos desde el remoto S3 (DVC):
    ```
    dvc pull
    ```

4. para trabajar con jupyternotebook en el entorno virtual
    ```
    python -m ipykernel install --user --name=venv --display-name "Python (venv)"
    jupyter notebook
    ```
