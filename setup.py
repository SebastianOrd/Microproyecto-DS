from setuptools import find_packages, setup

setup(
    name="calidad_aire_model",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    author="Arx",
    description="Paquete para el entrenamiento del modelo de calidad del aire.",
    python_requires=">=3.9",
)