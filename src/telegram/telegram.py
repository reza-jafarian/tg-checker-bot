from telethon.tl.types import (JsonObject, JsonObjectValue, JsonString, JsonNumber)
from telethon import TelegramClient, errors
from telethon.sessions import StringSession
import telethon.tl.types.auth as auth
import asyncio

from src.utils.logger import logger

class Telegram:
    def __init__(self, phone_number: str, method='code_request'):
        self.phone_number = phone_number
        self.api_hash = '014b35b6184100b085b0d0572f9b5103'
        self.api_id = 4
        self.method = method
        
        self.push_token = 'c1yjMRh7QZCu-hmsSWwWi3:APA91bHk-q4LX-9Ga4AlduG9X0nU0r7Kk57Em8RJSDL0d1ni-4W2F_o5B1VJvCnIgk5pHCoqzrYWgpjCwNMQGL-t4NKHbR_6KPibkZ7q1ubXetEaKZdqorvYo_vdEZVaWj9BZni1Kdrp'
        
        self.client = TelegramClient(
            session=StringSession(),
            api_id=self.api_id,
            api_hash=self.api_hash,
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
                # JsonObjectValue('tz_offset', JsonNumber(timezone_offset('UTC +6:30'))),
                JsonObjectValue('perf_cat', JsonNumber(2)),
            ]
        )
    
    async def check(self):
        try:
            # await self.client.connect()
            await asyncio.wait_for(self.client.connect(), timeout=5.0)
            response = await self.client.send_code_request(phone=self.phone_number)
            
            if isinstance(response.type, auth.SentCodeTypeSetUpEmailRequired):
                return '[✔️][📧]'
            elif isinstance(response.type, auth.SentCodeTypeApp):
                return '[📶]'
            elif isinstance(response.type, auth.SentCodeTypeSms):
                return '[✔️][📩]'
            elif isinstance(response.type, auth.SentCodeTypeCall):
                return '[✔️][📞]'
            elif isinstance(response.type, auth.SentCodeTypeEmailCode):
                return '[📶][📧]'
            else:
                print(response.type)
                
        except errors.rpcerrorlist.PhoneNumberBannedError:
            return '[🚫]'
        except errors.rpcerrorlist.PhoneNumberInvalidError:
            return '[❎]'
        except errors.rpcerrorlist.PhoneNumberFloodError:
            return '[limited]'
        except errors.rpcerrorlist.FloodWaitError:
            return '[limit]'
        except asyncio.TimeoutError:
            return '[timeouted]'
        except Exception as error:
            return '[❓]'
        
        finally:
            await self.client.disconnect()
    