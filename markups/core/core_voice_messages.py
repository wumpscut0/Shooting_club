from aiogram.types import FSInputFile
from aiogram.methods.send_voice import SendVoice
from markups.core import VoiceMessageConstructor, ButtonWidget


class Voice(VoiceMessageConstructor):
    def __init__(self, voice: str | FSInputFile):
        super().__init__()
        self.voice = voice
        self._back = ButtonWidget(text="Ok", callback_data="return_to_context")

    async def init(self):
        self.add_button_in_new_row(self._back)
