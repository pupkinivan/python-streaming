from pydantic import BaseModel


class ChatRequestDto(BaseModel):
    user_id: str
    message: str