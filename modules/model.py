from pydantic import BaseModel, validator

from database import get_db
from io import BytesIO

from .utils import audio_file_to_str

class User(BaseModel):
    id: int = None
    chat_id: str

    @classmethod
    def get_or_create(cls, chat_id):
        db = get_db()
        data = db.select('users', {'chat_id': chat_id})
        if len(data):
            return cls(**data[0])
        else:
            user_id = db.insert_dict('users', {'chat_id': chat_id}, 'id')
            return cls(id=user_id, chat_id=chat_id)

    def reached_limit(self):
        # TODO: implement
        return False

class MessageLogHistory(BaseModel):
    id: int = None
    chat_id: str
    update_id: int
    prompt_tokens: int
    response_tokens: int


class MessageContent(BaseModel):
    id: int = None
    message_id: int
    prompt: str
    response: str
    audio: str = None # base64 encoded audio file

    @validator('audio', pre=True)
    def encode_audio(cls, v):
        if isinstance(v, BytesIO):
            return audio_file_to_str(v)
        return v


class Message(BaseModel):
    log_history: MessageLogHistory
    content: MessageContent

    @classmethod
    def create(
        cls,
        chat_id: str,
        update_id: int,
        prompt_tokens: int,
        prompt: str,
        response_tokens: int,
        response: str,
        voice_file: BytesIO
    ):
        db = get_db()
        log_history=MessageLogHistory(
            chat_id=chat_id,
            update_id=update_id,
            prompt_tokens=prompt_tokens,
            response_tokens=response_tokens
        )
        log_history.id = db.insert_dict(
            'message_log_history',
            log_history.dict(exclude_none=True),
            'id'
        )
        
        message_content=MessageContent(
            message_id=log_history.id,
            prompt=prompt,
            response=response,
            audio=voice_file
        )
        message_content.id = db.insert_dict(
            'message_content',
            message_content.dict(exclude_none=True),
            'id'
        )
        
        return cls(log_history=log_history, content=message_content)