"""
Main file for the bot.
"""
from time import sleep
from threading import Thread
from typing import List

from modules.message import MessageHandler, get_updates
from modules.context import logger

message_handler = MessageHandler()


def bot_loop():
    print('Loading bot...')
    updates = get_updates()
    off_set = max([*map(
        lambda x: x.update_id,
        updates
    ), 0])
    
    threads: List[Thread] = []
    
    def thread_cleaner():
        nonlocal threads
        
        while True:
            sleep(60)
            for i in range(len(threads) - 1):
                if not threads[i].is_alive():
                    del threads[i]
                    break
    Thread(target=thread_cleaner).start()
    print('Bot running.')
    while True:
        sleep(1)
        try:
            updates = get_updates(off_set + 1)
            for update in updates:
                if update.update_id > off_set:
                    off_set = update.update_id
                thread = Thread(target=lambda: message_handler.handle(update))
                thread.start()
                threads.append(thread)
        except Exception as e:
            logger.send(str(e))


if __name__ == '__main__':
    bot_loop()
