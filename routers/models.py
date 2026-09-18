from pydantic import BaseModel

class AskRequest(BaseModel):

    question: str
    history: list =[]
    user_id: str
    messages: list[dict]
