import datetime
import peewee
import redis

from src.config.config import SETTINGS

if SETTINGS.DB_ENGINE == 'sqlite3':
    db = peewee.SqliteDatabase(SETTINGS.DB_NAME)
elif SETTINGS.DB_ENGINE == 'mysql':
    db = peewee.MySQLDatabase(
        SETTINGS.DB_NAME,
        user=SETTINGS.DB_USER,
        password=SETTINGS.DB_PASSWORD,
        host=SETTINGS.DB_HOST,
        port=SETTINGS.DB_PORT
    )
else:
    raise ValueError("Unsupported database engine. Please use 'sqlite3' or 'mysql'.")

if SETTINGS.ENABLE_REDIS:
    redis_db = redis.Redis(host=SETTINGS.DB_HOST, port=6379, db=0, encoding='utf-8')


class BaseModel(peewee.Model):
    class Meta:
        database = db


class User(BaseModel):
    DALY_FREE_CHECK = 5 # Daily free check: 50
    TEST_TIME = 86400 # 1 day
    
    user_id = peewee.BigIntegerField(unique=True)
    step = peewee.CharField(max_length=255, default='none') # default: none
    language = peewee.CharField(max_length=5, default='fa') # default: English
    account_status = peewee.BooleanField(default=True) # default: Active (Free)
    is_tested = peewee.BooleanField(default=False) # default: Not tested
    usdt_balance = peewee.FloatField(default=0.0) # default: 0.0
    toman_balance = peewee.BigIntegerField(default=0) # default: 0
    free_check = peewee.BigIntegerField(default=DALY_FREE_CHECK) # Daly free check: 50
    datetime_joined = peewee.DateTimeField(default=datetime.datetime.now) # default: now
    datetime_subscription = peewee.BigIntegerField(default=0) # default: 0


class Setting(BaseModel):
    bot_status = peewee.BooleanField(default=True) # default: Active
    check_status = peewee.BooleanField(default=True) # default: Active
    test_status = peewee.BooleanField(default=True) # default: Active
    check_type = peewee.CharField(max_length=50, default='code_request') # default = 'code_request' | Methods -> [code_request, change_number_request]


db.connect()
db.create_tables(models=[User, Setting])

if Setting.select().count() == 0:
    Setting.create()
