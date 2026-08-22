import os
import asyncio
from telethon import TelegramClient, events

# قراءة البيانات من السيرفر بأمان
api_id = int(os.environ.get('API_ID', 0))
api_hash = os.environ.get('API_HASH', '')
token = os.environ.get('TOKEN', '')

client = TelegramClient('bot_session', api_id, api_hash)

@client.on(events.NewMessage(pattern='.ping'))
async def handler(event):
    await event.reply("البوت يعمل 24/7 بنجاح ✔️")

async def main():
    # تسجيل الدخول باستخدام التوكن مباشرة بدون أي طلبات إدخال
    await client.sign_in(bot_token=token)
    print("...البوت يعمل الآن بصورة طبيعية...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
