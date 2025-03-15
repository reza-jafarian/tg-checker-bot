from telethon import events

from src.utils.keyboards import start_key
from src.database.models import User
from src.config.config import TEXTS

async def init(bot):
    @bot.on(events.NewMessage(pattern=r'^([\/\#\!\.]start|🔙 back)$', func=lambda e: e.is_private))
    async def start(event):
        user = await event.get_sender()
        
        user_data, _ = User.get_or_create(user_id=user.id)
        
        await event.reply(TEXTS['start'][user_data.language], buttons = start_key())