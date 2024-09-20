from watchdog.events import FileSystemEventHandler
import asyncio
from utils.logging_config import logger


class TokenFileHandler(FileSystemEventHandler):
    def __init__(self, initialize_tokens, load_configuration ):
        super().__init__()
        self.loop = asyncio.get_event_loop()
        self.initialize_tokens = initialize_tokens
        self.load_configuration = load_configuration

    def on_modified(self, event):
        if event.src_path.endswith("tokens.env"):
            logger.info("tokens.env has been modified, reloading tokens...")
            asyncio.run_coroutine_threadsafe(self.initialize_tokens(), self.loop)
        elif event.src_path.endswith("config.env"):
            logger.info("config.env has been modified, reloading configuration...")
            asyncio.run_coroutine_threadsafe(self.load_configuration(), self.loop)