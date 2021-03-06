import html
from telethon import events
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.tl.functions.users import GetFullUserRequest
from .. import loader, utils


def mention_html(user_id, name):
        return u'<a href="tg://user?id={}">{}</a>'.format(user_id, html.escape(name))

class reportadminsMod(loader.Module):

    strings = {"name":"Reporting"}

    async def reportcmd(self, event):
        """репортит на юзера созывая админов"""
        if event.is_reply:
            reply_message = await event.get_reply_message()
            reply_user = await event.client(GetFullUserRequest(reply_message.sender_id))
            user = [i async for i in event.client.iter_participants(event.to_id.channel_id, filter=ChannelParticipantsAdmins)]
            admin = []
            for u in user:
                admin.append(mention_html(u.id, "\u200b"))
            text = f"<b><a href='tg://user?id={reply_message.sender_id}'>{reply_user.user.first_name}</a> Доложено админам.\nУдалите после прочтения!</b>"
            text += "".join(admin)
            await event.client.send_message(event.chat_id, text, reply_to=reply_message.id)
            await event.delete()
        else:
            await event.edit("<b>Реплай забыл.</b>")
    
            
