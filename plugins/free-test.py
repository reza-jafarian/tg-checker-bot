from datetime import datetime, timedelta
from telethon import events

from src.database.models import User, Setting
from src.config.config import TEXTS, SETTINGS
from src.utils.keyboards import start_key

async def init(bot):
    @bot.on(events.NewMessage(pattern=r'(🆓 تست رایگان|/free_test)', func=lambda e: e.is_private))
    async def free_test(event):
        user = await event.get_sender()
        user_data, _ = User.get_or_create(user_id=user.id)

        if not Setting.get().test_status and user.id != SETTINGS.OWNER:
            return await event.reply(TEXTS['test_not_available'][user_data.language])
        
        elif user_data.is_tested == False:
            wait = await event.reply(TEXTS['wait'][user_data.language])

            current_timestamp = int(datetime.now().timestamp())
            new_timestamp = current_timestamp + User.TEST_TIME

            User.update(
                is_tested=True,
                datetime_subscription=new_timestamp
            ).where(User.user_id == user.id).execute()

            await wait.delete()
            await event.reply(str(TEXTS['test_activated'][user_data.language]).format(timedelta(seconds=User.TEST_TIME).days), buttons=start_key())
        else:
            await event.reply(TEXTS['already_tested'][user_data.language])
