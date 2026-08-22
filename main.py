import os
from telethon import TelegramClient, events

# هذه البيانات ستأخذها من "موقع الاستضافة" لاحقاً
api_id = int(os.environ.get('API_ID', 0))
api_hash = os.environ.get('API_HASH', '')
phone = os.environ.get('PHONE', '')

client = TelegramClient('session_name', api_id, api_hash)

@client.on(events.NewMessage(pattern='.ping'))
async def handler(event):
    await event.reply('سورس البوت يعمل 24/7 بنجاح! ✅')

async def main():
    await client.start(phone=phone)
    print("البوت يعمل الآن...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
