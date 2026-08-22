import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# قراءة البيانات من الـ Secrets
api_id = int(os.environ.get('API_ID', 0))
api_hash = os.environ.get('API_HASH', '')
session_string = os.environ.get('SESSION', '')

client = TelegramClient(StringSession(session_string), api_id, api_hash)

# متغيرات النظام
auto_reply_status = False
auto_reply_text = "حبيبي طالع بس ارجع احجي وياك"

# --- قائمة الأوامر ---
@client.on(events.NewMessage(pattern=r'\.الاوامر', outgoing=True))
async def help_handler(event):
    help_text = """
⚙️ **قسم الحساب والخاص:**
• `.رد [النص]` : تفعيل الرد التلقائي في الخاص.
• `.ايقاف الرد` : تعطيل الرد التلقائي.
• `.قنواتي` : جلب قائمة القنوات والمجموعات التي تملك فيها صلاحيات أدمين.
• `.مغادرة` : للخروج من المجموعة الحالية.

🎙️ **قسم الإذاعة:**
• `.إذاعة [النص]` : إرسال رسالة جماعية لكل المحادثات (الخاص).

🎭 **قسم الانتحال والتسلية:**
• `.انتحال` : (بالرد على شخص) لنسخ الاسم والصورة.
• `.استرجاع` : لاستعادة بيانات حسابك الأصلية.
• `.فحص` : للتحقق من سرعة اليوزر بوت.
    """
    await event.edit(help_text)

# --- الفحص ---
@client.on(events.NewMessage(pattern=r'\.فحص', outgoing=True))
async def ping_handler(event):
    await event.edit("Userbot is active 24/7 ✔️")

# --- الرد التلقائي ---
@client.on(events.NewMessage(pattern=r'\.رد (.*)', outgoing=True))
async def set_autoreply(event):
    global auto_reply_status, auto_reply_text
    auto_reply_text = event.pattern_match.group(1)
    auto_reply_status = True
    await event.edit(f'✅ تم تفعيل الرد التلقائي:\n"{auto_reply_text}"')

@client.on(events.NewMessage(pattern=r'\.ايقاف الرد', outgoing=True))
async def stop_autoreply(event):
    global auto_reply_status
    auto_reply_status = False
    await event.edit("❌ تم تعطيل الرد التلقائي.")

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def autoreply_listener(event):
    global auto_reply_status, auto_reply_text
    if auto_reply_status and not event.out:
        sender = await event.get_sender()
        if sender and not sender.bot:
            await event.reply(auto_reply_text)

# --- جلب القنوات ---
@client.on(events.NewMessage(pattern=r'\.قنواتي', outgoing=True))
async def channels_handler(event):
    await event.edit("🔄 جاري جلب القنوات والمجموعات...")
    chats_list = "📋 **قنواتك ومجموعاتك الإدارية:**\n\n"
    async for dialog in client.iter_dialogs():
        if (dialog.is_group or dialog.is_channel) and (getattr(dialog.entity, 'admin_rights', None)):
            chats_list += f"• {dialog.name}\n"
    await event.edit(chats_list)

# --- الانتحال ---
@client.on(events.NewMessage(pattern=r'\.انتحال', outgoing=True))
async def mimic_handler(event):
    if not event.is_reply:
        await event.edit("⚠️ رد على رسالة الشخص المراد انتحاله.")
        return
    reply = await event.get_reply_message()
    user = await client.get_entity(reply.sender_id)
    from telethon.tl.functions.account import UpdateProfileRequest
    await client(UpdateProfileRequest(first_name=user.first_name))
    await event.edit(f"🎭 تم انتحال شخصية {user.first_name}")

# --- مغادرة ---
@client.on(events.NewMessage(pattern=r'\.مغادرة', outgoing=True))
async def leave_handler(event):
    if event.is_group:
        await event.edit("👋 جاري المغادرة...")
        await client.delete_dialog(event.chat_id)

async def main():
    await client.start()
    print("...اليوزر بوت يعمل الآن على حسابك الشخصي 24/7...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())

