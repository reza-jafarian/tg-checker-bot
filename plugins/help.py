from telethon import events

from src.database.models import User
from src.config.config import TEXTS

async def init(bot):
    @bot.on(events.NewMessage(pattern=r'(راهنما)', func=lambda e: e.is_private))
    async def help(event):
        user = await event.get_sender()
        user_data, _ = User.get_or_create(user_id=user.id)
        
        await event.reply(TEXTS['help'][user_data.language])