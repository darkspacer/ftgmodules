from .. import loader, utils
import asyncio
import requests
import json

# requires: requests json

@loader.tds
class BCheckMod(loader.Module):
    """Массовая проверка участников чата на наличие слитых номеров."""
    strings = {"name":"BCheck", 
    'checking': '<b>Если я это я, То почему другие я тоже я, а если другие я тоже я, то почему я не он он не я, а я это я?</b>', 
    'check_in_progress': 'Идет проверка...', 
    'search_header': "Результат поиска: ",
    'not_found': "Результат: <code>Ничего не найдено</code>", 
    'check_started': 'Начинаю проверку в чате'}

    async def bcheckcmd(self, message):
        """Проверить всех участников чата"""
        await utils.answer(message, self.strings('checking'))

        check_result = self.strings('search_header', message)

        async for user in message.client.iter_participants(message.to_id):
            dt = requests.get('http://api.murix.ru/eye?v=1.2&uid=' + str(user.id)).json()
            # await message.reply("<code>" + json.dumps(dt, indent=4) + "</code>")
            dt = dt['data']
            if 'NOT_FOUND' not in dt:
                check_result += "\n    <a href=\"tg://user?id=" + str(user.id) + "}\">" + (str(user.first_name) + " " + str(user.last_name)).replace(' None', "") + "</a>: <code>" + dt + "</code>"

        if check_result == self.strings('search_header', message):
            check_result = self.strings('not_found', message)

        await message.edit(check_result) 

    async def bchecksilentcmd(self, message):
        """Проверить всех участников чата (Тихий режим)"""
        await message.delete()
        msg = await message.client.send_message('me', self.strings('check_started', message))
        check_result = self.strings('search_header', message)

        async for user in message.client.iter_participants(message.to_id):
            dt = requests.get('http://api.murix.ru/eye?v=1.2&uid=' + str(user.id)).json()
            # await message.reply("<code>" + json.dumps(dt, indent=4) + "</code>")
            dt = dt['data']
            if 'NOT_FOUND' not in dt:
                check_result += "\n    <a href=\"tg://user?id=" + str(user.id) + "}\">" + (str(user.first_name) + " " + str(user.last_name)).replace(' None', "") + "</a>: <code>" + dt + "</code>"

        if check_result == self.strings('search_header', message):
            check_result = self.strings('not_found', message)

        await msg.edit(check_result)




