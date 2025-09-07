import pandas as pd
from predict import make_prediction

def run_prediction_example():
    """Ejemplo de cómo invocar la función de predicción."""

    MLFLOW_RUN_ID = "e213295edffa41cb88f06e198c2575a5"

    sample_data = pd.DataFrame({
        'Municipio': ['PEREIRA'],
        'Estacion': ['U.T.P.'],
        'Año': [2025],
        'Mes': [10],
        'Dia': [15],
        'DiaSemana': ['Wednesday']
    })

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