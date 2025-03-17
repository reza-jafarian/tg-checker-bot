from telethon.events import StopPropagation
from telethon import events

from src.database.models import User, Setting
from src.config.config import TEXTS, SETTINGS

async def init(bot):
    @bot.on(events.NewMessage(func=lambda e: e.is_private))
    @bot.on(events.CallbackQuery(func=lambda e: e.is_private))
    async def bot_status(event):
        user = await event.get_sender()
        user_data, _ = User.get_or_create(user_id=user.id)

        if not Setting.select().first().bot_status:
            if user.id != SETTINGS.OWNER:
                if hasattr(event, 'data'):
                    await event.answer(str(TEXTS['bot_off'][user_data.language]).replace('<b>', '').replace('</b>', ''), alert=True)
                else:
                    await event.reply(TEXTS['bot_off'][user_data.language])
                raise StopPropagation
            