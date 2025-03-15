from telethon import TelegramClient, errors
from telethon.sessions import StringSession
import telethon.tl.types.auth as auth

class Telegram:
    def __init__(self, phone_number: str, method='code_request'):
        self.phone_number = phone_number
        self.api_id = 2040
        self.api_hash = 'b18441a1ff607e10a989891a5462e627'
        self.method = method
        
        self.client = TelegramClient(
            session=StringSession(),
            api_id=self.api_id,
            api_hash=self.api_hash,
            loop=None,
            receive_updates=False,
            entity_cache_limit=1
        )
    
    async def check(self):
        try:
            await self.client.connect()
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
        except Exception as error:
            return '[❓]'
        
        finally:
            await self.client.disconnect()
    