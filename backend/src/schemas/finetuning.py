from pydantic import BaseModel


class CreateFinetuningJob(BaseModel):
    name: str
