from pydantic import BaseModel


class ClassifyRequest(BaseModel):
    text: str
    lang: str = 'fr'
    token: str

class GeneralEqst(BaseModel):
    text: str
    token: str

