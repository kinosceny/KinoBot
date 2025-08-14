import os

DATABASE_DSN = os.environ['DATABASE_DSN']
BOT_TOKEN = os.environ['BOT_TOKEN']
ADMINS = [int(admin_id) for admin_id in os.environ['ADMINS'].split(',')]
API_SERVER = os.environ['API_SERVER']