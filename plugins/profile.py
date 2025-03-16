from telethon import events

from src.utils.functions import remaining_profile_subs
from src.database.models import User
from src.config.config import TEXTS

async def init(bot):
    @bot.on(events.NewMessage(pattern=r'(👤 حساب کاربری|/profile)', func=lambda e: e.is_private))
    async def help(event):
        user = await event.get_sender()
        user_data, _ = User.get_or_create(user_id=user.id)
        
        await event.reply(str(TEXTS['profile'][user_data.language]).format(
            user.id,
            f'{user_data.free_check} / {User.DALY_FREE_CHECK}',
            f'{user_data.toman_balance:,}',
            remaining_profile_subs(user_data.datetime_subscription)
        ))