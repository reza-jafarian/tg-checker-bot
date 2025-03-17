from telethon import events
import datetime, re, os

from src.utils.keyboards import start_key
from src.database.models import User
from src.config.config import TEXTS
from src.utils.functions import check_numbers

async def init(bot):
    @bot.on(events.NewMessage(func=lambda e: e.is_private))
    async def receive_numbers_texts(event):
        user = await event.get_sender()
        user_data, _ = User.get_or_create(user_id=user.id)
        
        numbers = re.findall(r'(?<![\w/:])\+?\d{6,15}(?![\w/:])', event.raw_text)
        numbers = list(set(map(lambda x: '+' + x if not x.startswith('+') else x, numbers)))
        
        if len(numbers) > 0:
            if len(numbers) > user_data.free_check and (user_data.datetime_subscription == 0 or user_data.datetime_subscription < datetime.datetime.now().timestamp()):
                await event.reply(TEXTS['not_have_subs'][user_data.language])
            
            elif len(numbers) <= User.DALY_FREE_CHECK:
                processing = await event.reply(TEXTS['processing_1'][user_data.language])
                
                await processing.edit(str(TEXTS['processing_2'][user_data.language]).format(len(numbers)))
                checked_numbers = await event.reply(TEXTS['checked_numbers'][user_data.language] + '\n\n' + TEXTS['status_numbers'][user_data.language].format(len(numbers), 0, 0, 0, 0, 0))
                
                # if user_data.datetime_subscription == 0 or user_data.datetime_subscription < datetime.datetime.now().timestamp():
                #     User.update(free_check=user_data.free_check - len(numbers)).where(User.user_id == user.id).execute()
                
                await check_numbers(event=event, user_id=user.id, numbers=numbers, checked_numbers=checked_numbers)
            
            elif len(numbers) > User.DALY_FREE_CHECK and user_data.datetime_subscription > datetime.datetime.now().timestamp():
                processing = await event.reply(TEXTS['processing_1'][user_data.language])
                
                await processing.edit(str(TEXTS['processing_2'][user_data.language]).format(len(numbers)))
                checked_numbers = await event.reply(TEXTS['checked_numbers'][user_data.language] + '\n\n' + TEXTS['status_numbers'][user_data.language].format(len(numbers), 0, 0, 0, 0, 0))
                
                await check_numbers(event=event, user_id=user.id, numbers=numbers, checked_numbers=checked_numbers)
            
            else:
                await event.reply(TEXTS['not_have_subs'][user_data.language])
                
    
    @bot.on(events.NewMessage(func=lambda e: e.is_private and e.file))
    async def receive_numbers_texts(event):
        user = await event.get_sender()
        user_data, _ = User.get_or_create(user_id=user.id)
        
        file_name = event.message.media.document.attributes[0].file_name
        
        if not file_name.endswith('.txt'):
            return
        
        processing = await event.reply(TEXTS['processing_1'][user_data.language])
        
        await event.download_media(file_name)
        with open(file_name, 'r') as file:
            numbers = re.findall(r'(?<![\w/:])\+?\d+(?![\w/:])', file.read())
            numbers = list(set(map(lambda x: '+' + x if not x.startswith('+') else x, numbers)))
        os.unlink(file_name)
        
        if len(numbers) > 0:
            if len(numbers) <= 5:
                await processing.edit(str(TEXTS['processing_2'][user_data.language]).format(len(numbers)))
                checked_numbers = await event.reply(TEXTS['checked_numbers'][user_data.language] + '\n\n' + TEXTS['status_numbers'][user_data.language].format(len(numbers), 0, 0, 0, 0, 0))
                await check_numbers(event=event, user_id=user.id, numbers=numbers, checked_numbers=checked_numbers, is_file=True)
            
            elif len(numbers) > 5 and user_data.datetime_subscription > datetime.datetime.now().timestamp():
                await processing.edit(str(TEXTS['processing_2'][user_data.language]).format(len(numbers)))
                checked_numbers = await event.reply(TEXTS['checked_numbers'][user_data.language] + '\n\n' + TEXTS['status_numbers'][user_data.language].format(len(numbers), 0, 0, 0, 0, 0))
                await check_numbers(event=event, user_id=user.id, numbers=numbers, checked_numbers=checked_numbers, is_file=True)
            
            else:
                await processing.delete()
                await event.reply(TEXTS['not_have_subs'][user_data.language])
        
        