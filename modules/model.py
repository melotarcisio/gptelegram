"""
Simple ORM for the database with some business logic.
"""
from datetime import datetime
from pydantic import BaseModel, validator
from typing import Literal

from database import get_db
from io import BytesIO

from .utils import audio_file_to_str
from .schema import Chat

class User(BaseModel):
    id: int = None
    chat_id: str
    first_name: str = None
    username: str = None
    type: str = None

    def save(self):
        db = get_db()
        db.update('users', self.dict(exclude=None), {'chat_id': self.chat_id})

    def count_credit(self):
        db = get_db()
        query = f"""
            SELECT SUM(amount) as credit 
            FROM transactions 
            WHERE chat_id = '{self.chat_id}' 
            GROUP BY chat_id
        """
        data = db.select(query)
        if data and len(data):
            return sum([d['credit'] for d in data])
        else:
            return 0
    
    def count_used(self):
        db = get_db()
        query = f"""
            SELECT 
                SUM(response_tokens) + SUM(prompt_tokens) as used 
            FROM message_log_history 
            WHERE chat_id = '{self.chat_id}' 
            GROUP BY chat_id
        """
        data = db.select(query)
        if data and len(data):
            return sum([d['used'] for d in data])
        else:
            return 0

    @property
    def credit_situation(self) -> Literal['free', 'free-exceeded', 'paid', 'paid-exceeded']:
        return 'paid'
        # TODO: feature pagamento
        # sit = ''
        
        # credit = self.count_credit() + settings.FREE_CREDIT
        # sit = 'free' if credit == settings.FREE_CREDIT else 'paid'

        # used = self.count_used()
        # sit += '-exceeded' if used >= credit else ''
        # return sit

    @classmethod
    def get_or_create(cls, chat: Chat):
        db = get_db()
        data = db.select_dict('users', {'chat_id': chat.id})
        
        if not len(data):
            db.insert_dict('users', chat.to_orm_dict(), 'id')
            return cls.get_or_create(chat)
        
        instance = cls(**data[0])
        if instance.type != chat.type:
            instance.first_name = chat.first_name
            instance.username = chat.username
            instance.save()
        
        return instance


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
    

class Transaction(BaseModel):
    id: int = None
    chat_id: str
    amount: int
    value_paid: float
    created_at: datetime = None

    @classmethod
    def create(cls, chat_id: str, amount: int, value_paid: float):
        db = get_db()
        transaction = cls(chat_id=chat_id, amount=amount, value_paid=value_paid)
        transaction.id = db.insert_dict(
            'transactions',
            transaction.dict(exclude_none=True),
            'id'
        )
        return transaction