from telethon import Button

def start_key() -> list:
    return [
        [Button.text('اطلاعات حساب', resize = True)],
        [Button.text('راهنما')]
    ]