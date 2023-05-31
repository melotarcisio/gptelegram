"""
Depends on context.py, schema.py, utils.py
"""
import requests

from typing import List

from core.settings import settings

from .context import ContextManager
from .schema import Update
from .utils import get_text_from_voice
from .model import Message, User


def get_updates(offset: int=None) -> List[Update]:
    url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT}/getUpdates'
    params = {'offset': offset, 'timeout': 60}
    try:
        response = requests.get(url, params=params)
        return [Update(**data) for data in response.json()['result']]
    except Exception:
        return []


COMMANDS = {
    'start': lambda _: None, # TODO: send a presentation message
    'recarregar': lambda _: None # TODO: send a message with payment options
}


class MessageHandler:
    def __init__(self):
        self.context_manager = ContextManager()

    def handle(self, update: Update):
        chat_id = update.message.chat.id
        if not self.context_manager.is_active(chat_id):
            self.context_manager.new_context(chat_id)

        prompt = ''
        voice_file = None

        if update.message.voice:
            prompt, voice_file = get_text_from_voice(update.message.voice)

        elif update.message.text:
            prompt = update.message.text

            # Handle commands
            if prompt.startswith('/'):
                [command, *args] = prompt[1:].split(' ')
                if command in COMMANDS:
                    COMMANDS[command](args)
                    return

        user = User.get_or_create(chat_id)
        if user.reached_limit():
            self.context_manager.send(
                chat_id, 
                'Você atingiu sua cota maxima. Realize uma recarga para continuar.'
            )
            # TODO: send a message with payment options
            return

        chat_response, tokens_prompt, tokens_response = \
            self.context_manager.process_text(chat_id, prompt)
        Message.create(
            chat_id=update.message.chat.id,
            update_id=update.update_id,
            prompt_tokens=tokens_prompt,
            prompt=prompt,
            response_tokens=tokens_response,
            response=chat_response,
            voice_file=voice_file,
        )
