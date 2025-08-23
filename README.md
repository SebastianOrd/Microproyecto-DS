# 🌍 Proyección de Calidad de Aire en Risaralda

Este repositorio contiene el código, datos y documentación del microproyecto **“Proyección de calidad de aire utilizando partículas PM10 en Risaralda, Colombia”**, desarrollado como parte del curso de Desarrollo de Soluciones de la maestria MAIA de la Universidad de los Andes

---

## Resumen

La calidad del aire es un factor determinante para la salud y el bienestar de las personas. En el departamento de Risaralda (Colombia), el material particulado **PM10** es uno de los principales contaminantes, asociado a problemas respiratorios y cardiovasculares.  

Este proyecto utiliza **datos históricos (2007–2023)** de monitoreo de calidad del aire, proporcionados por la **Corporación Autónoma Regional de Risaralda**, para proyectar concentraciones futuras de PM10.  

El propósito es **anticipar escenarios de riesgo** y ofrecer insumos para la gestión ambiental y la toma de decisiones.

---

## Objetivos

### Objetivo general
Desarrollar una aplicación que permita identificar las posibles tendencias del comportamiento de la calidad del aire en Risaralda.

### Objetivos específicos
- Entrenar un **modelo de aprendizaje automático** que estime concentraciones futuras de PM10.  
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

├── data
│   ├── raw/                # Datos originales (controlados con DVC, no en Git)

---
## Requisitos

- Python 3.9.6
- Git
- DVC (con soporte para S3)
- AWS CLI configurado

##  Instalación y uso

Proyecto probado en Python 3.12

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/TU_USUARIO/Microproyecto-DS.git
   cd Microproyecto-DS

   
2.	Crear y activar entorno virtual:   
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

3.	Obtener los datos desde el remoto S3 (DVC):
    dvc pull