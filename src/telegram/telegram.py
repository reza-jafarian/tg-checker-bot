from telethon.tl.types import (JsonObject, JsonObjectValue, JsonString, JsonNumber, CodeSettings)
from telethon.tl.functions.account import SendChangePhoneCodeRequest
from telethon import TelegramClient, errors
from telethon.sessions import StringSession
import telethon.tl.types.auth as auth

import asyncio, glob, random, json
from pathlib import Path

from src.utils.logger import logger

class Telegram:
    def __init__(self, phone_number: str, method='code_request'):
        from src.utils.functions import (get_random_app_version, get_random_system_version, get_random_device_model)
        
        self.phone_number = phone_number
        self.api_hash = '014b35b6184100b085b0d0572f9b5103'
        self.api_id = 4
        self.method = method
        
        # self.push_token = 'c1yjMRh7QZCu-hmsSWwWi3:APA91bHk-q4LX-9Ga4AlduG9X0nU0r7Kk57Em8RJSDL0d1ni-4W2F_o5B1VJvCnIgk5pHCoqzrYWgpjCwNMQGL-t4NKHbR_6KPibkZ7q1ubXetEaKZdqorvYo_vdEZVaWj9BZni1Kdrp'
        self.push_token = 'fnzD1TnmTUi2j3vsT3PGKX:APA91bEMa4b9iud404t1-7_ql2XNDIG-Vn00fRR8Lf3XtkxGuKxS623Nyv3_yFV5j8i15OVEY2Kk_zd7JyXyMghC2guJASNefFLtVJZfYwmZoajY9UZzeXc'
        
        if self.method == 'code_request':
            self.client = TelegramClient(
                session=StringSession(),
                api_id=self.api_id,
                api_hash=self.api_hash,
                app_version=get_random_app_version(platform='android'),
                system_version=get_random_system_version(platform='android'),
                device_model=get_random_device_model(platform='android'),
                loop=None,
                receive_updates=False,
                entity_cache_limit=1
            )
        
            self.client._init_request.lang_pack = 'android'
            self.client._init_request.params = JsonObject(
                [
                    JsonObjectValue('device_token', JsonString(self.push_token)),
                    JsonObjectValue('data', JsonString('49C1522548EBACD46CE322B6FD47F6092BB745D0F88082145CAF35E14DCC38E1')),
                    JsonObjectValue('installer', JsonString('com.android.vending')),
                    JsonObjectValue('package_id', JsonString('org.telegram.messenger')),
                    JsonObjectValue('tz_offset', JsonNumber(self._convert_timezone('+6:30'))),
                    JsonObjectValue('perf_cat', JsonNumber(2)),
                ]
            )
        
        elif self.method == 'change_number':
            select_sessions = glob.glob('sessions/*.session')
            
            if len(select_sessions) == 0:
                raise Exception('You do not have any session file!')
            else:
                select_random_session = random.choice(select_sessions)
                phone_number = Path(select_random_session).stem
                json_data = json.load(open('sessions/' + phone_number + '.json'))
            
            self.client = TelegramClient(
                session='sessions/' + phone_number,
                api_id=self.api_id, # json_data.get('app_id', json_data.get('api_id', self.api_id)),
                api_hash=self.api_hash, #json_data.get('app_hash', json_data.get('api_hash', self.api_hash)),
                app_version=get_random_app_version(platform='android'),
                system_version=get_random_system_version(platform='android'),
                device_model=get_random_device_model(platform='android'),
                system_lang_code='en',
                lang_code='en',
                lang_pack='android',
                # loop=None,
                # receive_updates=False,
                # entity_cache_limit=1
            )
            
            self.client._init_request.lang_pack = 'android'
            self.client._init_request.params = JsonObject(
                [
                    JsonObjectValue('device_token', JsonString(self.push_token)),
                    JsonObjectValue('data', JsonString('49C1522548EBACD46CE322B6FD47F6092BB745D0F88082145CAF35E14DCC38E1')),
                    JsonObjectValue('installer', JsonString('com.android.vending')),
                    JsonObjectValue('package_id', JsonString('org.telegram.messenger')),
                    JsonObjectValue('tz_offset', JsonNumber(self._convert_timezone('+6:30'))),
                    JsonObjectValue('perf_cat', JsonNumber(2)),
                ]
            )
    
    def _convert_timezone(self, timezone: str) -> int:
        if timezone:
            sign = 1 if '+' in timezone else -1
            hours, _, minutes = timezone.lstrip('+-').partition(':')
            return sign * (int(hours) * 3600 + int(minutes or 0) * 60)
        return 0
    
    async def check(self):
        try:
            if self.method == 'code_request':
                await asyncio.wait_for(self.client.connect(), timeout=5.0)
                response = await self.client.send_code_request(phone=self.phone_number)
                logger.info(f'[+] Type: {response.type}')
            
            elif self.method == 'change_number':
                await asyncio.wait_for(self.client.connect(), timeout=5.0)
                settings = CodeSettings(
                    allow_firebase=True,
                    allow_flashcall=True,
                    unknown_number=None if True else True,
                    app_sandbox=None,
                    allow_missed_call=True,
                    allow_app_hash=True,
                    current_number=True,
                    token=None,
                    logout_tokens=[],
                ),
                response = (await self.client(SendChangePhoneCodeRequest(phone_number=self.phone_number, settings=settings)))
                logger.info(f'[+] Type: {response}')
            
            if isinstance(response.type, auth.SentCodeTypeSetUpEmailRequired):
                return '[✔️][📧]', 'register'
            elif isinstance(response.type, auth.SentCodeTypeApp):
                return '[📶]', 'session'
            elif isinstance(response.type, auth.SentCodeTypeSms):
                return '[✔️][📩]', 'register'
            elif isinstance(response.type, auth.SentCodeTypeCall):
                return '[✔️][📞]', 'session'
            elif isinstance(response.type, auth.SentCodeTypeEmailCode):
                return '[📶][📧]', 'session'
            else:
                print(response.type)
                
        except errors.rpcerrorlist.PhoneNumberBannedError:
            return '[🚫]', 'ban'
        except errors.rpcerrorlist.PhoneNumberInvalidError:
            return '[❎]', 'invalid'
        except errors.rpcerrorlist.PhoneNumberFloodError:
            return '[limited]', 'limit'
        except errors.rpcerrorlist.FloodWaitError:
            return '[limit]', 'limit'
        except asyncio.TimeoutError:
            return '[timeouted]', 'timeout'
        except Exception as error:
            logger.error(error)
            return '[❓]', 'unknow'
        
        finally:
            await self.client.disconnect()
    