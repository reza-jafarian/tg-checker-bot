from typing import Union
import phonenumbers
import asyncio

from src.telegram.telegram import Telegram
from src.database.models import User
from src.config.config import TEXTS
from src.utils.logger import logger

SEMAPHORE_LIMIT = 10
BATCH_SIZE = 100
UPDATE_INTERVAL = 20
semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)

def get_country_flag(number: str) -> Union[str, bool]:
    try:
        parsed_number = phonenumbers.parse(number, None)
        country_code = phonenumbers.region_code_for_number(parsed_number)
        return ''.join(chr(ord(letter) % 32 + 0x1F1E5) for letter in country_code)
    except Exception as error:
        logger.error(f'[get_country_flag] -> Error: Phone number invalid! -> {error}')
        return False

async def check_number(number: str, index: int) -> str:
    async with semaphore:
        try:
            logger.info(f'[check_number] -> Checking Number {index}: {number}')
            status = await Telegram(phone_number=number, method='code_request').check()
            flag = get_country_flag(number)
            return f'{index}) {flag} {number} {status}' if flag else f'{index}) ❌ {number} {status}'
        except Exception as error:
            logger.error(f'[check_number] -> Error: {error} - Number {index}: {number}')
            return f'{index}) ❌ Failed {number}'

async def check_numbers(event, user_id, numbers, checked_numbers):
    try:
        user_data, _ = User.get_or_create(user_id=user_id)

        if not numbers:
            return await checked_numbers.edit(TEXTS['error'][user_data.language])

        results = []
        batch_tasks = []

        async def process_batch():
            nonlocal batch_tasks
            checked_batch = await asyncio.gather(*batch_tasks)
            results.extend(checked_batch)
            batch_tasks = []
            response = TEXTS['checked_result'][user_data.language].format('\n'.join(checked_batch), TEXTS['checking_more_numbers'][user_data.language])

            if len(results) <= BATCH_SIZE:
                await checked_numbers.edit(response)
            else:
                await event.respond(response)

        for index, number in enumerate(numbers, start=1):
            batch_tasks.append(check_number(number, index))

            if len(batch_tasks) == BATCH_SIZE:
                await process_batch()

            elif len(numbers) <= BATCH_SIZE and index % UPDATE_INTERVAL == 0:
                await process_batch()

        if batch_tasks:
            await process_batch()

    except Exception as error:
        logger.error(f'[check_numbers] -> Error: {error}')
        await checked_numbers.edit(TEXTS['error'][user_data.language])
