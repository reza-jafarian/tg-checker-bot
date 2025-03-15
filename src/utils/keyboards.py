from telethon import Button

def start_key() -> list:
    return [
        [Button.text('اطلاعات حساب', resize = True)],
        [Button.text('راهنما')]
    ]

def admin_panel_key() -> list:
    return [
        [Button.text('📊 Bot stat', resize = True)],
        [Button.text('🟢 Open user'), Button.text('🔴 Close user')],
        [Button.text('🔙 back')]
    ]

def select_ready_date() -> list:
    return [
        [Button.text('Open for test (30 minutes)', resize = True)],
        [Button.text('1 day'), Button.text('2 day'), Button.text('3 day')],
        [Button.text('5 day'), Button.text('10 day'), Button.text('15 day')],
        [Button.text('1 month'), Button.text('2 month'), Button.text('3 month')],
        [Button.text('🔙 back to admin', resize = True)]
    ]

def back_to_admin_panel_key() -> list:
    return [
        [Button.text('🔙 back to admin', resize = True)]
    ]