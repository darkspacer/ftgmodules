#by @innomods
from .. import loader, utils
import asyncio
import datetime
import io
import json

@loader.tds
class BackuperMod(loader.Module):
    """Backup everything and anything"""
    strings = {"name":"Backuper"}

    async def client_ready(self, client, db):
        self.db = db
        self.client = client

    async def backupdbcmd(self, message):
        """.backupdb - Создать бекап базы данных фтг"""
        txt = io.BytesIO(json.dumps(self.db).encode('utf-8'))
        txt.name = f"ftg-db-backup-{datetime.datetime.now().strftime('%d-%m-%Y-%H-%M')}.db"
        await self.client.send_file('me', txt)
        await self.client.send_message('me', '☝️ <b>Это - бекап базы данных. Никому его не передавай</b>')
        await message.delete()

    async def restoredbcmd(self, message):
        """.restoredb <key> - Восстановить базу данных из файла"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            await utils.answer(message, '<b>Reply to .db file</b>')
            await asyncio.sleep(3)
            await message.delete()
            return

        file = await message.client.download_file(reply.media)
        decoded_text = json.loads(file.decode('utf-8'))
        self.db.update(**decoded_text)
        self.db.save()
        # print(decoded_text)
        await utils.answer(message, '<b>База данных обновлена. Перезапускаю юзербот...</b>')
        await self.allmodules.commands['restart'](await message.respond('_'))

