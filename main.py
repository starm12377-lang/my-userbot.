import os
from telethon import TelegramClient, events

# قراءة البيانات بأمان من السيرفر
api_id = int(os.environ.get('API_ID', 0))
api_hash = os.environ.get('API_HASH', '')
token = os.environ.get('TOKEN', '')

# تشغيل البوت باستخدام التوكن مباشرة بدون طلب رقم هاتف أو كود
client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=token)

@client.on(events.NewMessage(pattern='.ping'))
async def handler(event):
    await event.reply("البوت يعمل 24/7 بنجاح ✔️")

async def main():
    print("...البوت يعمل الآن...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
