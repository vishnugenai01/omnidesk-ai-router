from pydantic import BaseModel


class AskRequest(BaseModel):
    messages: list[dict]