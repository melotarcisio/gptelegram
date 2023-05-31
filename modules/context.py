"""
    Has no dependencies on other files.
"""
import requests
import openai
import tiktoken
import threading
from time import time, sleep
from typing import Dict, NewType


from core.settings import settings

openai.api_key = settings.OPEN_API_KEY

class UserSender:
    def __init__(self,  chat: str=None, bot: str=None):
        self.bot = bot or settings.TELEGRAM_BOT
        self.chat = chat or settings.TELEGRAM_LOG_GROUP
        self.url = f'https://api.telegram.org/bot{self.bot}/'
        
    def send_long(self, msg):
        data = {
            'chat_id': self.chat,
            'caption': f'{msg[:30]}...\n\nTexto completo convertido para arquivo devido ao tamanho:'
        }
        requests.post(self.url + 'sendDocument',
                      data=data, files={'document': ('message.txt', msg)})

    def send(self, msg: str):
        msg = str(msg)
        try:
            if len(msg) > 1950:
                return self.send_long(msg)
            
            params = {
                'chat_id': self.chat,
                'text': msg
            }
            
            requests.get(self.url + 'sendMessage', params=params)
        except Exception as e:
            print(f'Error from SEND function message: {e}')


logger = UserSender()


class UserChatContext:
    def __init__(self, chat_id):
        self.messages = []
        self.sender = UserSender(chat_id)
        self.last_message = time()
        
    @property
    def is_idle(self):
        return time() - self.last_message > 60 * 30

    def set_message(self, msg):
        self.messages.append({"role": "system", "content": msg})
        tokens = self.num_tokens_from_messages(self.messages)
        while tokens > 8000 or len(self.messages) > settings.CONTEXT_MESSAGES_MAX_SIZE:
            if not len(self.messages) > 1:
                raise MemoryError("Context is too large to continue.")
            self.messages.pop(0)
            tokens = self.num_tokens_from_messages(self.messages)
        
        return tokens
        
    def set_response(self, msg):
        self.messages.append({"role": "assistant", "content": msg})
        tokens = self.num_tokens_from_messages(self.messages)
        while tokens > 8000 or len(self.messages) > settings.CONTEXT_MESSAGES_MAX_SIZE:
            if not len(self.messages) > 1:
                raise MemoryError("Context is too large to continue.")
            self.messages.pop(0)
            tokens = self.num_tokens_from_messages(self.messages)

    def process(self, msg: str):
        self.last_message = time()
        try:
            tokens_prompt = self.set_message(msg)
            
            completion = openai.ChatCompletion.create(model="gpt-4", messages=self.messages)
            chat_response = completion.choices[0].message.content

            tokens_response = self.num_tokens_from_text(chat_response)
            self.set_response(chat_response)
            self.sender.send(chat_response)
            
            return chat_response, tokens_prompt, tokens_response
        except MemoryError:
            self.messages = []
        except Exception as e:
            self.messages = []
            self.sender.send('Um erro inesperado aconteceu, infelizmente eu esqueci o nosso contexto. Por favor, tente novamente.')
            logger.send(f'Error from PROCESS function message: {e}. Context: {self}')

    @staticmethod
    def num_tokens_from_text(text: str, model="gpt-3.5-turbo-0301"):
        """Returns the number of tokens used by a string."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    @staticmethod
    def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens
        else:
            raise NotImplementedError()
        
    def __repr__(self) -> str:
        return (
            f"Messages len: {len(self.messages)}\nTokens: {self.num_tokens_from_messages(self.messages)}\n"
            f"Chat id: {self.sender.chat}\nBot: {self.sender.bot}"
        )

User = NewType("User chat_id", str)


class ContextManager:
    contexts: Dict[User, UserChatContext] = {}
    context_thread: threading.Thread = None
    
    def __init__(self):
        self.context_thread = threading.Thread(target=self.inactivity_check_loop)
        self.context_thread.start()
        
    def inactivity_check_loop(self):
        while True:
            sleep(60)
            try:
                chats = [*self.contexts.keys()]
                for chat in chats:
                    if self.contexts[chat].is_idle:
                        del self.contexts[chat]
                        logger.send(f'Context {chat} was deleted.')
            except Exception as e:
                logger.send(f'Error from inactivity_check_loop function message: {e}. Contexts: {self.contexts}')
                
    def is_active(self, chat_id):
        return chat_id in self.contexts
    
    def new_context(self, chat_id):
        self.contexts[chat_id] = UserChatContext(chat_id)
    
    def process_text(self, chat_id, text):
        if not self.is_active(chat_id):
            self.new_context(chat_id)
        return self.contexts[chat_id].process(text)

    def send(self, chat_id, text):
        if not self.is_active(chat_id):
            self.new_context(chat_id)
        self.contexts[chat_id].sender.send(text)