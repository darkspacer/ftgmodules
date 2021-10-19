# requires: gtts

import os
from gtts import gTTS
from .. import loader, utils

def register(cb):
    cb(SayTextMod())

class SayTextMod(loader.Module):
    strings = {'name': 'SayText'}
    def __init__(self):
        self.name = self.strings['name']
        self._me = None
        self._ratelimit = []
    async def saycmd(self, message):
        """.say <text> - сonverts text to voice."""
        reply = await message.get_reply_message()
        await message.edit("<b>Генерация голосового сообщения.</b>")
        try:
            gTTS(text=f'{message.to_dict()["message"].split("say ")[1]}', lang='ru').save("say.ogg")
            await message.delete()
            if reply:
                await message.client.send_file(message.to_id, "say.ogg", voice_note=True, reply_to=reply.id)
            else:
                await message.client.send_file(message.to_id, "say.ogg", voice_note=True)
            os.system(f"rm -rf say.ogg")
        except:
            await message.edit("<b>Ощибка!</b>")
