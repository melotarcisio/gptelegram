"""
Pass.
"""
import requests
import os
import speech_recognition as sr
import base64

from io import BytesIO
from uuid import uuid4
from pydub import AudioSegment
from contextlib import contextmanager
from typing import Tuple

from core.settings import settings
from .schema import Voice
from .context import logger

def get_voice_file(voice: Voice) -> BytesIO:
    file_id = voice.file_id
    
    # Get file path using get_file API
    get_file_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT}/getfile?file_id={file_id}"
    response = requests.get(get_file_url).json()
    file_path = response["result"]["file_path"]

    # Download and save file as binary in BytesIO
    file_url = f"https://api.telegram.org/file/bot{settings.TELEGRAM_BOT}/{file_path}"
    file_data = requests.get(file_url).content

    return BytesIO(file_data)


def convert_ogg_to_wav(ogg_file: BytesIO) -> BytesIO:
    ogg_audio = AudioSegment.from_ogg(ogg_file)

    # wav_audio = ogg_audio
    wav_audio = ogg_audio.set_channels(1).set_frame_rate(16000)

    temp = f'{uuid4()}.wav'
    wav_audio.export(temp, format="wav")

    @contextmanager
    def file_context():
        yield open(temp, 'rb')
        os.remove(temp)

    return file_context


def get_text_from_wav_file(wav_file_context: callable) -> str:
    recognizer = sr.Recognizer()
    text = ''
    with wav_file_context() as wav_file:
        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='pt-BR')
    return text


def get_text_from_voice(voice: Voice) -> Tuple[str, BytesIO]:
    try:
        voice_file = get_voice_file(voice)
        wav_file_context = convert_ogg_to_wav(voice_file)
        text = get_text_from_wav_file(wav_file_context)
        return text, voice_file
    except Exception as e:
        logger.send(f'Error from get_text_from_voice function message: {e}')
        raise e


def audio_file_to_str(audio: BytesIO) -> str:
    if not audio:
        return ''

    bytes_data = audio.getvalue()
    base64_bytes = base64.b64encode(bytes_data)
    return base64_bytes.decode('utf-8')
