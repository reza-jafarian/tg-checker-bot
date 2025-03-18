from telethon.tl.types import (JsonObject, JsonObjectValue, JsonString, JsonNumber, CodeSettings)
from telethon.tl.functions.account import SendChangePhoneCodeRequest
from telethon.tl.functions.auth import SendCodeRequest
from telethon.sessions import StringSession
from telethon import TelegramClient, errors
import telethon.tl.types.auth as auth
import telethon, asyncio, python_socks
from telethon.tl import functions
import traceback

from src.utils.logger import logger

class Telegram:    
    def __init__(self, phone_number: str, user_id: int, method: str = 'code_request', proxy: dict = None):
        from src.utils.functions import (
            get_random_app_version, get_random_system_version,
            get_random_device_model, convert_timezone,
            load_used_sessions, save_used_sessions,
            get_random_session, load_session_data
        )
        
        self.api_hash = '014b35b6184100b085b0d0572f9b5103'
        self.api_id = 4
        self.method = method
        self.phone_number = phone_number
        
        if self.method == 'code_request':
            
            telethon.network.mtprotostate.MSG_TOO_NEW_DELTA = 2**32
            telethon.network.mtprotostate.MSG_TOO_OLD_DELTA = 2**32
            
            # self.push_token = 'c1yjMRh7QZCu-hmsSWwWi3:APA91bHk-q4LX-9Ga4AlduG9X0nU0r7Kk57Em8RJSDL0d1ni-4W2F_o5B1VJvCnIgk5pHCoqzrYWgpjCwNMQGL-t4NKHbR_6KPibkZ7q1ubXetEaKZdqorvYo_vdEZVaWj9BZni1Kdrp'
            self.push_token = 'epdZ8WHc206AB79gYtlW7e:APA91bHGOnvVx3m_GAZ2lyZt4C4eFPo7MNn-VpEl8_IoiFEMdAC7li2L0eQo6o6HTaJ9sJXZqrwPeg9tnn77A2R6Jj7qXbgj1LxK4P_QmO5ZLJAL28ISpDubOJ8oKsuBa6apDv8P7ecZ'
            # self.push_token = 'fnzD1TnmTUi2j3vsT3PGKX:APA91bEMa4b9iud404t1-7_ql2XNDIG-Vn00fRR8Lf3XtkxGuKxS623Nyv3_yFV5j8i15OVEY2Kk_zd7JyXyMghC2guJASNefFLtVJZfYwmZoajY9UZzeXc'
            # self.push_token = 'ex0K5vVeQdeQsMCelnY4Ol:APA91bEhUxD3KynX8LgVPzfyZtBydiezQ2zFfHubPi3nnlwYcm1USC1pxAYUFZnHaM706Fm4XW69I__vJ4UqmRql2SCsxJXDkft2TvbDPFKblkpnzkVvwWk'
            
            self.client = TelegramClient(
                session=StringSession(),
                api_id=self.api_id,
                api_hash=self.api_hash,
                app_version=get_random_app_version(platform='android'),
                system_version=get_random_system_version(platform='android'),
                device_model=get_random_device_model(platform='android'),
                lang_code='en',
                system_lang_code='en-us',
                proxy=proxy
            )
            
            self.client._init_request.app_version = get_random_app_version(platform='android')
            self.client._init_request.system_version = get_random_system_version(platform='android')
            self.client._init_request.device_model = get_random_device_model(platform='android')
            self.client._init_request.lang_pack = 'android'
            self.client._init_request.lang_code = 'en'
            self.client._init_request.system_lang_code = 'en-us'
            
            self.client._init_request.params = JsonObject(
                [
                    JsonObjectValue('device_token', JsonString(self.push_token)),
                    JsonObjectValue('data', JsonString('49C1522548EBACD46CE322B6FD47F6092BB745D0F88082145CAF35E14DCC38E1')),
                    JsonObjectValue('installer', JsonString('com.android.vending')),
                    JsonObjectValue('package_id', JsonString('org.telegram.messenger')),
                    JsonObjectValue('tz_offset', JsonNumber(convert_timezone('+6:30'))),
                    JsonObjectValue('perf_cat', JsonNumber(2)),
                ]
            )
        
        elif self.method == 'change_number_request':
            session_number = get_random_session(user_id)
            data = load_session_data(session_name=session_number)
            
            self.client = TelegramClient(
                session=f'sessions/{session_number}',
                api_id=data.get('app_id', data.get('api_id', self.api_id)),
                api_hash=data.get('app_hash', data.get('api_hash', self.api_hash)),
                app_version=data.get('app_version', get_random_app_version(platform='android')),
                system_version=data.get('system_version', data.get('sdk', get_random_system_version(platform='android'))),
                device_model=data.get('device_model', data.get('device', get_random_device_model(platform='android'))),
                system_lang_code=data.get('system_lang_code', 'en-us'),
                lang_code=data.get('lang_code', 'en'),
                proxy=proxy
            )
    
    async def check(self):
        if self.method == 'code_request':
            try:
                # await asyncio.wait_for(self.client.connect(), timeout=5.0)
                await self.client.connect()
                
                await self.client(functions.langpack.GetLangPackRequest('android', 'en'))
                await self.client(functions.help.GetCountriesListRequest('en', 0))
                await self.client(functions.help.GetNearestDcRequest())
                await self.client(functions.help.GetConfigRequest())
                response = await self.client.send_code_request(phone=self.phone_number)
                
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
                    return '[❓]', 'unknow'
                    
            except errors.rpcerrorlist.PhoneNumberBannedError:
                return '[🚫]', 'ban'
            except errors.rpcerrorlist.PhoneNumberInvalidError:
                return '[❎]', 'invalid'
            except errors.rpcerrorlist.PhoneNumberFloodError:
                return '[limited]', 'limit'
            except errors.rpcerrorlist.FloodWaitError as error:
                logger.error(f'FloodWaitError: {error}')
                return '[limit]', 'limit'
            except asyncio.TimeoutError:
                return '[timeouted]', 'timeout'
            except Exception as error:
                logger.error(error)
                return '[❓]', 'unknow'
            
            finally:
                await self.client.disconnect()
        
        elif self.method == 'change_number_request':
            try:
                # await asyncio.wait_for(self.client.connect(), timeout=5.0)
                await self.client.connect()
                
                response = await self.client(SendChangePhoneCodeRequest(phone_number=self.phone_number, settings=CodeSettings()))
                
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
                    return '[❓]', 'unknow'
            
            except errors.rpcerrorlist.PhoneNumberOccupiedError:
                return '[📶]', 'session'
            except errors.rpcerrorlist.PhoneNumberBannedError:
                return '[🚫]', 'ban'
            except errors.rpcerrorlist.PhoneNumberInvalidError:
                return '[❎]', 'invalid'
            except errors.rpcerrorlist.PhoneNumberFloodError:
                return '[limited]', 'limit'
            except errors.rpcerrorlist.FloodWaitError as error:
                logger.error(f'FloodWaitError: {error}')
                return '[limit]', 'limit'
            except asyncio.TimeoutError:
                return '[timeouted]', 'timeout'
            except Exception as error:
                logger.error(error)
                return '[❓]', 'unknow'
        