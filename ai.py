# requires: tensorflow joblib aiohttp aiofiles

import os

import aiofiles
import aiohttp
import joblib
from telethon import types
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.python.keras.saving.save import load_model

from .. import loader, utils

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


@loader.tds
class BadIdeasAIDetectorMod(loader.Module):
    'BadIdeasAIDetector'

    model: Sequential = None
    tokenizer: Tokenizer = None

    strings = {
        'name': 'BadIdeasAIDetector',
        'pref': '<b>[AI]</b>',
        'downloading_model': '{} Downoading model...',
        'loading_model': '{} Loading model...',
        'need_reply': '{} Reply...',
        'answer': '{} {}',
    }

    def __predict(self, text) -> float:
        return round(float(self.model.predict(pad_sequences(self.tkn.texts_to_sequences([text]), 1024))[0]) * 100, 2)

    async def chk(self, m: types.Message):
        client = m.client
        reply = m.get_reply_message()
        if not reply or not reply.raw_text:
            return await utils.answer(m, self.strings('need_reply').format(self.strings('pref')))
        if not self.model or not self.tokenizer:
            m = await utils.answer(m, self.strings('downloading_model').format(self.strings('pref')))
            async with aiohttp.client.ClientSession() as s:
                async with s.get('https://d4n13l3k00.ru/_f/nenormdetector.h5') as tkn:
                    f = await aiofiles.open('nenormdetector.h5', mode='wb')
                    await f.write(await tkn.read())
                    await f.close()
                    self.model = load_model('nenormdetector.h5')
                async with s.get(m, 'https://d4n13l3k00.ru/_f/tokens.pkl') as tkn:
                    f = await aiofiles.open('tokens.pkl', mode='wb')
                    await f.write(await tkn.read())
                    await f.close()
                    self.tokenizer = joblib.load('tokens.pkl')
        await utils.answer(m, self.strings('answer').format(self.strings('pref'), str(self.__predict(reply.raw_text))))