from telethon import events
import re, os

from src.utils.keyboards import start_key
from src.database.models import User
from src.config.config import TEXTS
from src.utils.functions import check_numbers

async def init(bot):
    @bot.on(events.NewMessage(pattern=r'\+?\b\d{6,15}\b', func=lambda e: e.is_private))
    async def receive_numbers_texts(event):
        user = await event.get_sender()
        user_data, _ = User.get_or_create(user_id=user.id)
        
        processing = await event.reply(TEXTS['processing_1'][user_data.language])
        
        numbers = re.findall(r'(?<![\w/:])\+?\d+(?![\w/:])', event.raw_text)
        numbers = list(set(map(lambda x: '+' + x if not x.startswith('+') else x, numbers)))
        
        await processing.edit(str(TEXTS['processing_2'][user_data.language]).format(len(numbers)))
        checked_numbers = await event.reply(TEXTS['checked_numbers'][user_data.language]) 
        
        await check_numbers(event=event, user_id=user.id, numbers=numbers, checked_numbers=checked_numbers)
        
        # if response:
        #     await checked_numbers.edit(TEXTS['checked_result'][user_data.language].format(response))
        # else:
        #     await checked_numbers.edit(TEXTS['error'][user_data.language])
    
    @bot.on(events.NewMessage(func=lambda e: e.is_private and e.file))
    async def receive_numbers_texts(event):
        user = await event.get_sender()
        user_data, _ = User.get_or_create(user_id=user.id)
        
        processing = await event.reply(TEXTS['processing_1'][user_data.language])
        
        file_name = event.message.media.document.attributes[0].file_name
        await event.download_media(file_name)
        with open(file_name, 'r') as file:
            numbers = re.findall(r'(?<![\w/:])\+?\d+(?![\w/:])', file.read())
            numbers = list(set(map(lambda x: '+' + x if not x.startswith('+') else x, numbers)))
        os.unlink(file_name)
        
        await processing.edit(str(TEXTS['processing_2'][user_data.language]).format(len(numbers)))
        checked_numbers = await event.reply(TEXTS['checked_numbers'][user_data.language]) 
        
        await check_numbers(event=event, user_id=user.id, numbers=numbers, checked_numbers=checked_numbers)
        
        # if response:
        #     await checked_numbers.edit(TEXTS['checked_result'][user_data.language].format(response))
        # else:
        #     await checked_numbers.edit(TEXTS['error'][user_data.language])