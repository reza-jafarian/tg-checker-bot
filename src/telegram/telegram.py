from telethon.tl.types import (JsonObject, JsonObjectValue, JsonString, JsonNumber, CodeSettings)
from telethon.tl.functions.account import SendChangePhoneCodeRequest
from telethon.tl.functions.auth import SendCodeRequest
from telethon.sessions import StringSession
from telethon import TelegramClient, errors
import telethon.tl.types.auth as auth
from telethon.tl import functions
from random import shuffle
import telethon, asyncio, python_socks

from src.utils.logger import logger

telethon.network.mtprotostate.MSG_TOO_NEW_DELTA = 2**32
telethon.network.mtprotostate.MSG_TOO_OLD_DELTA = 2**32

class Telegram:    
    def __init__(self, phone_number: str, method: str = 'code_request', proxy: dict = None):
        from src.utils.functions import (get_random_app_version, get_random_system_version, get_random_device_model)
        
        self.phone_number = phone_number
        self.api_hash = '014b35b6184100b085b0d0572f9b5103'
        self.api_id = 4
        self.method = method
        
        self.push_token = 'c1yjMRh7QZCu-hmsSWwWi3:APA91bHk-q4LX-9Ga4AlduG9X0nU0r7Kk57Em8RJSDL0d1ni-4W2F_o5B1VJvCnIgk5pHCoqzrYWgpjCwNMQGL-t4NKHbR_6KPibkZ7q1ubXetEaKZdqorvYo_vdEZVaWj9BZni1Kdrp'
        # self.push_token = 'epdZ8WHc206AB79gYtlW7e:APA91bHGOnvVx3m_GAZ2lyZt4C4eFPo7MNn-VpEl8_IoiFEMdAC7li2L0eQo6o6HTaJ9sJXZqrwPeg9tnn77A2R6Jj7qXbgj1LxK4P_QmO5ZLJAL28ISpDubOJ8oKsuBa6apDv8P7ecZ'
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
            loop=None,
            receive_updates=False,
            entity_cache_limit=1,
            proxy={'proxy_type': python_socks.ProxyType.SOCKS5, 'addr': 'p.webshare.io', 'port': 80, 'username': 'lfkjopqn-rotate', 'password': 'ljx4agduh1rf', 'rdns':True}
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
            # await asyncio.wait_for(self.client.connect(), timeout=5.0)
            await self.client.connect()
            
            await self.client(functions.langpack.GetLangPackRequest('android', 'en'))
            await self.client(functions.help.GetCountriesListRequest('en', 0))
            await self.client(functions.help.GetNearestDcRequest())
            await self.client(functions.help.GetConfigRequest())
            
            response = await self.client.send_code_request(phone=self.phone_number)
            # sim = not False
            # response = await self.client(
            #     SendCodeRequest(
            #         phone_number=self.phone_number,
            #         api_id=self.api_id,
            #         api_hash=self.api_hash,
            #         settings=CodeSettings(
            #             allow_firebase=True,
            #             allow_flashcall=sim,
            #             unknown_number=None if sim else True,
            #             app_sandbox=None,
            #             allow_missed_call=sim,
            #             allow_app_hash=True,
            #             current_number=sim,
            #             token=None,
            #             logout_tokens=[],
            #         ),
            #     )
            # )
            logger.info(f'[+] Type: {response.type}')
            
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
    