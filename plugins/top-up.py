from telethon import events

from src.database.models import User
from src.config.config import TEXTS

async def init(bot):
    @bot.on(events.NewMessage(pattern=r'(💸 افزایش موجودی|/topup)', func=lambda e: e.is_private))
    async def topup(event):
        user = await event.get_sender()
        user_data, _ = User.get_or_create(user_id=user.id)
        
        await event.reply(TEXTS['not_have_subs'][user_data.language])
        