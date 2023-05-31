from typing import Optional, List
from pydantic import BaseModel, validator

class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    username: Optional[str]
    language_code: Optional[str]

class Chat(BaseModel):
    id: int
    first_name: Optional[str]
    username: Optional[str]
    type: str
    
    @validator('id')
    def id_should_be_str(cls, v):
        return str(v)

class Voice(BaseModel):
    duration: int
    mime_type: Optional[str]
    file_id: str
    file_unique_id: str
    file_size: Optional[int]

class Message(BaseModel):
    message_id: int
    from_: Optional[User] = None
    chat: Chat
    date: int
    text: Optional[str] = None
    voice: Optional[Voice] = None

    class Config:
        fields = {
            'from_': 'from'
        }

class Update(BaseModel):
    update_id: int
    message: Message

class GetUpdatesResponse(BaseModel):
    ok: bool
    result: List[Update]
