# Repositorio del codigo y datos

## Repositorio GIT

Con el objetivo de tener un adecuado manejo de versiones se creo un repositorio en github, tambien se creo un repositorio DVC con amazon S3 para llevar el control de versiones de los datos.

el enlace del repositorio creado es: https://github.com/SebastianOrd/Microproyecto-DS

![](../reports/figures/repositorio.png) 

se ha definido una estructura para el repositorio de la siguiente manera:

```
├──data/
│   ├── raw/              # Datos originales (solo lectura)
│   ├── processed/        # Datos enriquecidos/intermedios
├── notebooks/            #Todos los ipynb que se desarrollen
├── src/                  #Codigo modularizado en python
├── reports/              #informes y entregables
│   ├── figures/          # Imágenes usadas en los documentos
├── .gitignore
├── requirements.txt      # Dependencias requeridas
└── README.md             # resumen del proyecto y su uso
```
se trabajara de tal manera que cada integrante del grupo creara una rama para realizar las tareas asignadas todos tienen permisos para crear y hacer commits en las ramas pero no para hacerlo en el main para esto el responsable del repositorio se encargara de realizar la respectiva revision de los cambios y de realizar el merge.

la idea es que cada integrante del grupo cree un entorno virtual en su maquina local e instale todos los "requirements.txt" para asi poder desarrollar en colaboracion

## Repositorio DVC

Con el objetivo de tener un adecuado manejo de los datos, se ha creado un "bucket" de S3 en aws
![](../reports/figures/dvc_init.png) 

cada integrante debera descargarse el repositorio de github en donde se encuencta la carpeta .dvc con el archivo .config, debera configurar el awsCLI para poder acceder a los datos y hacer un pull para tenerlos localmente




