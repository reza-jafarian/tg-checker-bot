from aioprocessing import AioProcess, AioQueue
from typing import Union
from pathlib import Path
import phonenumbers
import python_socks
import traceback
import asyncio
import random
import json
import glob
import re
import os

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

from src.database.models import User, Setting, redis_db
from src.telegram.telegram import Telegram
from src.telegram.client import getClient
from src.config.config import TEXTS
from src.utils.logger import logger

SEMAPHORE_LIMIT = 20
BATCH_SIZE = 100
UPDATE_INTERVAL = 20
semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)

def add_time_to_now(time_str: str) -> str:
    now = datetime.now()
    time_units = {
        "second": "seconds",
        "seconds": "seconds",
        "minute": "minutes",
        "minutes": "minutes",
        "hour": "hours",
        "hours": "hours",
        "day": "days",
        "days": "days",
        "week": "weeks",
        "weeks": "weeks",
        "month": "months",
        "months": "months",
        "year": "years",
        "years": "years",
    }
    
    matches = re.findall(r"(\d+)\s*(\w+)", time_str)
    
    delta = timedelta()
    rdelta = relativedelta()

    for amount, unit in matches:
        amount = int(amount)
        unit = unit.lower()
        
        if unit in ['month', 'months', 'year', 'years']:
            rdelta += relativedelta(**{time_units[unit]: amount})
        elif unit in time_units:
            delta += timedelta(**{time_units[unit]: amount})

    return now + delta + rdelta

def remaining_profile_subs(timestamp: int) -> Union[str, int]:
    input_time = datetime.fromtimestamp(timestamp)
    remaining_seconds = (input_time - datetime.now()).total_seconds()

    if remaining_seconds <= 0:
        return 0

    remaining_days = int(remaining_seconds // (24 * 3600))
    remaining_seconds %= (24 * 3600)

    hours = int(remaining_seconds // 3600)
    remaining_seconds %= 3600

    minutes = int(remaining_seconds // 60)
    seconds = int(remaining_seconds % 60)

    time_string = []
    if remaining_days > 0:
        time_string.append(f'{remaining_days} روز')
    if hours > 0:
        time_string.append(f'{hours} ساعت')
    if minutes > 0:
        time_string.append(f'{minutes} دقیقه')
    if seconds > 0 or not time_string:
        time_string.append(f'{seconds} ثانیه')

    return ' و '.join(time_string)

# ------------------------------------------------------- #

def load_used_sessions(user_id):
    used_sessions = redis_db.get(f'used_sessions:{user_id}')
    if used_sessions:
        return json.loads(used_sessions)
    return {}

def save_used_sessions(user_id, used_sessions):
    redis_db.set(f'used_sessions:{user_id}', json.dumps(used_sessions))

def get_random_session(user_id):
    all_sessions = glob.glob('sessions/*.session')
    if not all_sessions:
        raise FileNotFoundError("No session files found.")

    used_sessions = load_used_sessions(user_id)
    
    session_usage = {Path(s).stem: used_sessions.get(Path(s).stem, 0) for s in all_sessions}

    min_usage = min(session_usage.values(), default=0)
    least_used_sessions = [s for s, usage in session_usage.items() if usage == min_usage]

    selected_session = random.choice(least_used_sessions)

    used_sessions[selected_session] = used_sessions.get(selected_session, 0) + 1
    save_used_sessions(user_id, used_sessions)

    return selected_session

def load_session_data(session_name):
    with open(f'sessions/{session_name}.json', 'r') as f:
        return json.load(f)

# ------------------------------------------------------- #

def convert_timezone(timezone: str) -> int:
    if timezone:
        sign = 1 if '+' in timezone else -1
        hours, _, minutes = timezone.lstrip('+-').partition(':')
        return sign * (int(hours) * 3600 + int(minutes or 0) * 60)
    return 0

def get_random_proxy() -> dict:
    with open('src/utils/proxies.txt', 'r') as f:
        proxies = [line.strip().split(':') for line in f.readlines() if line.strip() and not line.startswith('#')]
        if len(proxies) > 0:
            proxy = random.choice(proxies)
            return ':'.join(proxy), {
                    'proxy_type': python_socks.ProxyType.SOCKS5,
                    'addr': str(proxy[0]),
                    'port': int(proxy[1]),
                    'username': str(proxy[2]),
                    'password': str(proxy[3]),
                    'rdns': True,
                }
        else:
            return None

def get_random_app_version(platform: str = 'desktop') -> str:
    if platform == 'desktop':
        return random.choice(['5.1.7 x64'])
    elif platform == 'android':
        return random.choice(['10.14.5 (49452)', '11.6.2 (56152)'])

def get_random_system_version(platform: str = 'desktop') -> str:
    if platform == 'desktop':
        return random.choice(['Windows 7 x64', 'Windows 8 x64', 'Windows 8.1 x64', 'Windows 10 x64', 'Windows 11 x64'])
    elif platform == 'android':
        return random.choice([
            'SDK 23',
            'SDK 24',
            'SDK 25',
            'SDK 26',
            'SDK 27',
            'SDK 28',
            'SDK 29',
            'SDK 30',
            'SDK 31',
            'SDK 32',
            'SDK 33',
            'SDK 34'
        ])
    elif platform == 'macOS':
        return random.choice(system_versions = [
            'macOS 10.12',
            'macOS 10.12.1',
            'macOS 10.12.2',
            'macOS 10.12.3',
            'macOS 10.12.4',
            'macOS 10.12.5',
            'macOS 10.12.6',
            'macOS 10.13',
            'macOS 10.13.1',
            'macOS 10.13.2',
            'macOS 10.13.3',
            'macOS 10.13.4',
            'macOS 10.13.5',
            'macOS 10.13.6',
            'macOS 10.14',
            'macOS 10.14.1',
            'macOS 10.14.2',
            'macOS 10.14.3',
            'macOS 10.14.4',
            'macOS 10.14.5',
            'macOS 10.14.6',
            'macOS 10.15',
            'macOS 10.15.1',
            'macOS 10.15.2',
            'macOS 10.15.3',
            'macOS 10.15.4',
            'macOS 10.15.5',
            'macOS 10.15.6',
            'macOS 10.15.7',
            'macOS 11.0',
            'macOS 11.0.1',
            'macOS 11.1',
            'macOS 11.2',
            'macOS 11.2.1',
            'macOS 11.2.2',
            'macOS 11.2.3',
            'macOS 11.3',
            'macOS 11.3.1',
            'macOS 11.4',
            'macOS 11.5',
            'macOS 11.5.1',
            'macOS 11.5.2',
            'macOS 11.6',
            'macOS 11.6.1',
            'macOS 11.6.2',
            'macOS 12.0',
            'macOS 12.0.1',
            'macOS 12.1',
        ])

def get_random_device_model(platform: str = 'desktop') -> str:
    if platform == 'desktop':
        device_models = [
            "0000000000",
            "0133D9",
            "03X0MN",
            "0R849J",
            "0T105W",
            "0TP406",
            "0U785D",
            "0UU795",
            "0WCNK6",
            "0Y2MRG",
            "0YF8P5",
            "1005P",
            "1005PE",
            "10125",
            "103C_53307F",
            "DH77EB",
            "DP55WB",
            "DT1412",
            "DX4300",
            "DX4831",
            "DX4860",
            "DX58SO",
            "Dazzle_RL",
            "Default string",
            "Dell DM061",
            "Dell DV051",
            "Dell DXC061",
            "Dell XPS420",
            "Dell XPS720",
            "Desktop",
            "Dimension 3000",
            "Dimension 4700",
            "Dimension E521",
            "Durian 7A1",
            "EP35-DS3",
            "EP35-DS3R",
            "EP35-DS4",
            "EP35C-DS3R",
            "EP43-DS3L",
        ]
        return random.choice(device_models)
    elif platform == 'android':
        device_models = [
            "Samsung GT-I5510M",
            "Samsung GT-I5800L",
            "Samsung SCH-I559",
            "Samsung SCH-i559",
            "Samsung Behold II",
            "Samsung GT-I9260",
            "Samsung SM-A710XZ",
            "Samsung GT-B9120",
            "Samsung SCH-R880",
            "Samsung SCH-R720",
            "Samsung SGH-S730M",
            "Samsung SHV-E270L",
            "Samsung SAMSUNG-SGH-I927",
            "Samsung SGH-I927",
            "Samsung SCH-I699I",
            "Samsung Samsung Chromebook 3",
            "Samsung Samsung Chromebook Plus",
            "Samsung kevin",
            "Samsung Samsung Chromebook Plus (V2)",
            "Samsung nautilus",
            "Samsung Samsung Chromebook Pro",
            "Samsung caroline",
            "Samsung SPH-D600",
            "Samsung SAMSUNG-SGH-I857",
            "Samsung SCH-I510",
            "Samsung SM-G1600",
            "Samsung SM-G1650",
            "Samsung GT-I5500B",
            "Samsung GT-I5500L",
            "Samsung GT-I5500M",
            "Samsung GT-I5503T",
            "Samsung GT-I5510L",
            "Samsung SGH-T759",
            "Samsung EK-GC100",
            "Samsung GT-B9062",
            "Samsung YP-GI2",
            "Samsung SHW-M100S",
            "Samsung archer",
            "Samsung SM-A716S",
            "Samsung SM-A015A",
            "Samsung SM-A015AZ",
            "Samsung SM-A015F",
            "Samsung SM-A015G",
            "Samsung SM-A015M",
            "Samsung SM-A015T1",
            "Samsung SM-A015U",
            "Samsung SM-A015U1",
            "Samsung SM-A015V",
            "Samsung SM-S111DL",
            "Samsung SM-A013F",
            "Samsung SM-A013G",
            "Samsung SM-A013M",
            "Samsung SM-A022F",
            "Samsung SM-A022G",
            "Samsung SM-A022M",
            "Samsung SM-A025A",
            "Samsung SM-A025AZ",
            "Samsung SM-A025F",
            "Samsung SM-A025G",
            "Samsung SM-A025M",
            "Samsung SM-A025U",
            "Samsung SM-A025U1",
            "Samsung SM-A025V",
            "Samsung SM-A105F",
            "Samsung SM-A105FN",
            "Samsung SM-A105G",
            "Samsung SM-A105M",
            "Samsung SM-A105N",
            "Samsung SM-A102U",
            "Samsung SM-A102U1",
            "Samsung SM-A102W",
            "Samsung SM-S102DL",
            "Samsung SM-A102N",
            "Samsung SM-A107F",
            "Samsung SM-A107M",
            "Samsung SM-A115A",
            "Samsung SM-A115AP",
            "Samsung SM-A115AZ",
            "Samsung SM-A115F",
            "Samsung SM-A115M",
            "Samsung SM-A115U",
            "Samsung SM-A115U1",
            "Samsung SM-A115W",
            "Samsung SM-A125F",
            "Samsung SM-A125M",
            "Samsung SM-A125N",
            "Samsung SM-A125U",
            "Samsung SM-A125U1",
            "Samsung SM-S127DL",
            "Samsung SM-A260F",
            "Samsung SM-A260G",
            "Samsung SC-02M",
            "Samsung SCV46",
            "Samsung SCV46-j",
            "Samsung SCV46-u",
            "Samsung SM-A205F",
            "Samsung SM-A205FN",
            "Samsung SM-A205G",
            "Samsung SM-A205GN",
            "Samsung SM-A205W",
            "Samsung SM-A205YN",
            "Samsung SM-A205U",
            "Samsung SM-A205U1",
            "Samsung SM-S205DL",
            "Samsung SM-A202F",
            "Samsung SM-A2070",
            "Samsung SM-A207F",
            "Samsung SM-A207M",
            "Samsung SC-42A",
            "Samsung SCV49",
            "Samsung SM-A215U",
            "Samsung SM-A215U1",
            "Samsung SM-A215W",
            "Samsung SM-S215DL",
            "Samsung SM-A217F",
            "Samsung SM-A217M",
        ]
        return random.choice(device_models)

def get_country_flag(number: str) -> Union[str, bool]:
    try:
        parsed_number = phonenumbers.parse(number, None)
        country_code = phonenumbers.region_code_for_number(parsed_number)
        return ''.join(chr(ord(letter) % 32 + 0x1F1E5) for letter in country_code)
    except Exception as error:
        logger.error(f'[get_country_flag] -> Error: Phone number invalid!')
        return False

# ------------------------------------------------------- #

def get_caption(status: str, language: str = 'fa') -> str:
    if status == 'register':
        return 'شماره های خام'
    elif status == 'session':
        return 'شماره های سشن دار'
    elif status == 'ban':
        return 'شماره های بن شده'
    elif status == 'limit':
        return 'شماره های محدود شده'
    elif status == 'invalid':
        return 'شماره های نامعتبر'
    elif status == 'timeout':
        return 'شماره های تایم اوت شده'
    elif status == 'unknow':
        return 'شماره های نامشخص / دیگر'
    elif status == 'failed':
        return 'شماره های ناموفق'
    else:
        return 'نامشخص ( خطا در ربات )'

# async def check_number(user_id: Union[int, str], numbers: list, number: str, index: int, live_status: dict, checked_numbers, is_file: bool = False) -> Union[str, tuple]:
#     async with semaphore:
#         try:
#             user_data, _ = User.get_or_create(user_id=user_id)
            
#             # proxy = get_random_proxy()
#             status = await Telegram(phone_number=number, method='code_request', proxy=None).check()
            
#             flag = get_country_flag(number)
            
#             logger.info(f'[<yellow>check_number</yellow>] -> Checking Number <red>{index}</red>: [{flag}] <green>{number}</green> -> <blue>{status[0]}</blue>')

#             if is_file:
#                 if status[1] == 'register':
#                     live_status['true_numbers'] += 1
#                 elif status[1] == 'session':
#                     live_status['has_session'] += 1
#                 elif status[1] == 'ban':
#                     live_status['ban_numbers'] += 1
#                 elif status[1] == 'limit':
#                     live_status['limit_numbers'] += 1
#                 else:
#                     live_status['other'] += 1
                
#                 if index % 2 == 0:
#                     try:
#                         await checked_numbers.edit(str(TEXTS['checked_numbers'][user_data.language]) + '\n\n' + str(TEXTS['status_numbers'][user_data.language]).format(
#                             len(numbers),
#                             live_status['true_numbers'],
#                             live_status['has_session'],
#                             live_status['ban_numbers'],
#                             live_status['limit_numbers'],
#                             live_status['other']
#                         ))
#                     except Exception:
#                         pass

#             return (f'{index}) {flag} {number} {status[0]}' if flag else f'{index}) ❌ {number} {status[0]}', status[1])
#         except Exception as error:
#             logger.error(f'[check_number] -> Error: {error} - Number {index}: {number}')
#             return (f'{index}) ❌ Failed {number}', 'failed')

# async def check_numbers(event, user_id, numbers, checked_numbers, is_file=False):
#     try:
#         user_data, _ = User.get_or_create(user_id=user_id)
#         bot = await getClient()

#         if not numbers:
#             return await checked_numbers.edit(TEXTS['error'][user_data.language])

#         live_status = {'total_numbers': len(numbers), 'true_numbers': 0, 'has_session': 0, 'ban_numbers': 0, 'limit_numbers': 0, 'other': 0}
#         results = set()
#         batch_tasks = []

#         async def process_batch(last_batch=False):
#             nonlocal batch_tasks
#             checked_batch = await asyncio.gather(*batch_tasks)

#             for result_tuple in checked_batch:
#                 if isinstance(result_tuple, tuple) and len(result_tuple) == 2:
#                     result, status = result_tuple
#                     if result not in results:
#                         results.add((result, status))

#             batch_tasks = []

#             sorted_results = sorted(results, key=lambda x: int(x[0].split(")")[0]))

#             if is_file:
#                 file_data = {}
#                 for result, status in sorted_results:
#                     number = result.split(' ')[2]
#                     file_data.setdefault(status, []).append(number)

#                 for status, numbers in file_data.items():
#                     file_name = f'{status}_{user_id}.txt'
#                     with open(file_name, 'w', encoding='utf-8') as file:
#                         file.write('\n'.join(numbers) + '\n')

#             else:
#                 checked_texts = "\n".join([r for r, _ in sorted_results])
#                 if last_batch:
#                     response = TEXTS['checked_result'][user_data.language].format(checked_texts, TEXTS['done'][user_data.language])
#                 else:
#                     response = TEXTS['checked_result'][user_data.language].format(checked_texts, TEXTS['checking_more_numbers'][user_data.language])

#                 if len(results) <= BATCH_SIZE:
#                     await checked_numbers.edit(response)
#                 else:
#                     await event.respond(response)

#         # -------------------- #

#         unique_numbers = list(set(numbers))
#         for index, number in enumerate(unique_numbers, start=1):
#             # Pass live_status to check_number
#             batch_tasks.append(check_number(user_id, numbers, number, index, live_status, checked_numbers, is_file))
            
#             if len(batch_tasks) == BATCH_SIZE:
#                 remaining_numbers = len(unique_numbers) - (index + 1)
#                 last_batch = remaining_numbers <= 0
#                 await process_batch(last_batch=last_batch)
            
#             elif len(unique_numbers) <= BATCH_SIZE and index % (UPDATE_INTERVAL if UPDATE_INTERVAL <= len(numbers) else len(numbers)) == 0:
#                 remaining_numbers = len(unique_numbers) - (index + 1)
#                 last_batch = remaining_numbers <= 0
#                 await process_batch(last_batch=last_batch)

#         if batch_tasks:
#             await process_batch(last_batch=True)

#         if is_file:
#             unique_statuses = set(status for _, status in results)

#             for status in unique_statuses:
#                 file_name = f'{status}_{user_id}.txt'
#                 caption = '<b>' + get_caption(status, user_data.language) + '</b>'
                
#                 if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
#                     await bot.send_file(entity=user_id, file=file_name, caption=caption)
#                     os.unlink(file_name)

#     except Exception as error:
#         logger.error(f'[check_numbers] -> Error: {error}')
#         traceback.print_exc()
        
#         try:
#             await checked_numbers.edit(TEXTS['error'][user_data.language])
#         except Exception:
#             await event.respond(TEXTS['error'][user_data.language])

# -------------------------------------- #

def extract_number(entry):
    match = re.match(r'^(\d+)\|', entry)
    return match.group(1) if match else entry

def worker(queue, result_queue):
    async def process_number(user_id, number, index, original_entry):
        try:
            status = await Telegram(
                phone_number=number,
                user_id=user_id,
                method=Setting.select().first().check_type,
                proxy={'proxy_type': python_socks.ProxyType.SOCKS5, 'addr': 'p.webshare.io', 'port': 80, 'username': 'lfkjopqn-rotate', 'password': 'ljx4agduh1rf', 'rdns': True}
            ).check()
            
            result_queue.put((index, original_entry, status[0], status[1]))
            logger.info(f'Checked Number {index}: {number} -> {status[0]}')
        
        except Exception as e:
            logger.error(f'Error checking number {index}: {number} - {e}')
            result_queue.put((index, original_entry, "Failed", "failed"))

    while True:
        task = queue.get()
        if task is None:
            break
        user_id, number, index, original_entry = task
        asyncio.run(process_number(user_id, number, index, original_entry))

async def check_numbers(event, user_id, numbers, checked_numbers, is_file=False):
    user_data, _ = User.get_or_create(user_id=user_id)
    bot = await getClient()
    if not numbers:
        return await checked_numbers.edit(TEXTS['error'][user_data.language])

    queue = AioQueue()
    result_queue = AioQueue()
    num_workers = min(len(numbers), BATCH_SIZE)
    workers = [AioProcess(target=worker, args=(queue, result_queue)) for _ in range(num_workers)]
    
    for w in workers:
        w.start()

    processed_numbers = [(index, extract_number(entry), entry) for index, entry in enumerate(set(numbers), start=1)]

    for index, number, original_entry in processed_numbers:
        queue.put((user_id, number, index, original_entry))

    for _ in workers:
        queue.put(None)

    results = []
    file_data = {}
    message_chunks = []
    
    while len(results) < len(numbers):
        index, original_entry, result, status = await result_queue.coro_get()
        results.append((index, original_entry, result, status))

        if is_file:
            file_data.setdefault(status, []).append(original_entry)
        else:
            message_chunks.append((index, f"{index}) {extract_number(original_entry)} {result}"))

        if not is_file and len(message_chunks) >= 100:
            message_chunks.sort(key=lambda x: x[0])
            checked_texts = '\n'.join([msg for _, msg in message_chunks])
            await bot.send_message(user_id, TEXTS['checked_result'][user_data.language].format(checked_texts, TEXTS['checking_more_numbers'][user_data.language]))
            message_chunks = []

    for w in workers:
        w.join()

    if not is_file:
        if message_chunks:
            message_chunks.sort(key=lambda x: x[0])
            checked_texts = '\n'.join([msg for _, msg in message_chunks])
            await bot.send_message(user_id, TEXTS['checked_result'][user_data.language].format(checked_texts, TEXTS['done'][user_data.language]))

    if is_file:
        for status, entries in file_data.items():
            file_name = f'{status}_{user_id}.txt'
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write('\n'.join(entries) + '\n')
            
            caption = '<b>' + get_caption(status, user_data.language) + '</b>'
            if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
                await bot.send_file(entity=user_id, file=file_name, caption=caption)
                os.unlink(file_name)