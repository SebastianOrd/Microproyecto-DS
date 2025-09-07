from typing import Any, List, Optional

from pydantic import BaseModel,Field
#from model.processing.validation import DataInputSchema

class DataInputSchema(BaseModel):
    Municipio: Optional[str]
    Estacion: Optional[str]
    Año: Optional[int]
    Mes: Optional[int]
    Dia: Optional[int]
    DiaSemana: Optional[str]

# Esquema de los resultados de predicción
class PredictionResults(BaseModel):
    errors: Optional[Any]
    predictions: Optional[List[float]]

# Esquema para inputs múltiples
class MultipleDataInputs(BaseModel):
    inputs: List[DataInputSchema]

    class Config:
        schema_extra = {
            "example": {
                "inputs": [
                    {
                        "Municipio": "PEREIRA",
                        "Estacion": "U.T.P.",
                        "Año": 2025,
                        "Mes": 10,
                        "Dia": 15,
                        "DiaSemana": "Wednesday"
                    }
                ]
            }
        }
