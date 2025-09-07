import pandas as pd
import numpy as np
from predict import make_prediction

def run_prediction_example():
    """Ejemplo de cómo invocar la función de predicción con ingeniería de características."""

    MLFLOW_RUN_ID = "6d89f239864f4250b73b377615e77b4e"

    input_data = {
        'Municipio': 'PEREIRA',
        'Estacion': 'U.T.P.',
        'Año': 2025,
        'Mes': 10,
        'Dia': 15,
        'DiaSemana': 'Wednesday'
    }

    fecha = pd.to_datetime(f"{input_data['Año']}-{input_data['Mes']}-{input_data['Dia']}")

    input_data['dia_del_anio'] = fecha.dayofyear
    input_data['semana_del_anio'] = fecha.isocalendar().week
    input_data['es_fin_de_semana'] = 1 if fecha.weekday() >= 5 else 0
    input_data['mes_sin'] = np.sin(2 * np.pi * input_data['Mes'] / 12)
    input_data['mes_cos'] = np.cos(2 * np.pi * input_data['Mes'] / 12)
    input_data['dia_sin'] = np.sin(2 * np.pi * input_data['Dia'] / 31)
    input_data['dia_cos'] = np.cos(2 * np.pi * input_data['Dia'] / 31)
    
    sample_data = pd.DataFrame([input_data])

    print(f"Realizando predicción con el modelo del Run ID: {MLFLOW_RUN_ID}")
    result = make_prediction(input_data=sample_data, run_id=MLFLOW_RUN_ID)

    if result["errors"]:
        print(f"Ocurrió un error: {result['errors']}")
    else:
        prediccion = result['predictions'][0]
        print("---" * 10)
        print(f"Resultado de la predicción: {prediccion:.4f}")
        print("---" * 10)

if __name__ == "__main__":
    run_prediction_example()