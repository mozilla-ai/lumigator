from pydantic import BaseModel


class SummarizerArgs(BaseModel):
    name: str  # model name, but model is protected namespace in pydantic
    tokenizer: str
    task: str
    description: str
