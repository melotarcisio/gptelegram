"""
Depends on context.py, schema.py, utils.py
"""
import requests

from typing import List, Callable

from core.settings import settings
from core.constants import (
    INITIAL_MESSAGE, 
    PAYMENT_OPTIONS_MESSAGE, 
    LIMIT_EXCEEDED_MESSAGE_FREE, 
    LIMIT_EXCEEDED_MESSAGE_PAID
)

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


def recarregar_command(sender: Callable[[str], None], args = List[str]):
    value = None
    try:
        value = float(args[0])
    except Exception:
        pass

    if not value:
        return sender(PAYMENT_OPTIONS_MESSAGE)
    else:
        # TODO: generate a payment link and send to user
        ...


Comand = Callable[[Callable[[str], None], List[str]], None]
COMMANDS = { # To be used as "/command args" by the user
    'start': lambda sender, _: sender(INITIAL_MESSAGE),
    # TODO: feature pagamento
    # 'recarregar': recarregar_command,
    # 'help': lambda sender, _: sender(PAYMENT_OPTIONS_MESSAGE)
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
                    COMMANDS[command](
                        lambda message: self.context_manager.send(chat_id, message),
                        args
                    )
                    return

        user = User.get_or_create(update.message.chat)
        if user.credit_situation == 'free-exceeded':
            return self.context_manager.send(
                chat_id,
                LIMIT_EXCEEDED_MESSAGE_FREE
            )
        elif user.credit_situation == 'paid-exceeded':
            return self.context_manager.send(
                chat_id,
                LIMIT_EXCEEDED_MESSAGE_PAID
            )

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