from pydantic import BaseModel


class Leitura(BaseModel):
    timestamp: str
    temperatura: float
    umidade: float