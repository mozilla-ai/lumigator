from pydantic import BaseModel

class Key(BaseModel):
    key_value: str
    description: str = ""