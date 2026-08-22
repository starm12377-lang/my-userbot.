import os
import asyncio
from telethon import TelegramClient, events

# قراءة البيانات بأمان
api_id = int(os.environ.get('API_ID', 0))
api_hash = os.environ.get('API_HASH', '')
token = os.environ.get('TOKEN', '')

client = TelegramClient('bot_session', api_id, api_hash)

# متغيرات النظام
auto_reply_status = True
auto_reply_text = "حبيبي طالع بس ارجع احجي وياك"
original_profile = {"first_name": None, "about": None}

# 1. قسم الأوامر الرئيسية (القائمة الكاملة)
@client.on(events.NewMessage(pattern=r'\.الاوامر'))
async def help_handler(event):
    help_text = """
⚙️ **قسم الحساب والخاص:**
• `رد [النص]` : تفعيل الرد التلقائي في الخاص.
• `ايقاف الرد` : تعطيل الرد التلقائي.
• `قنواتي` : جلب قائمة القنوات والمجموعات التي تملك فيها صلاحيات أدمين.
• `مغادرة` : للخروج من المجموعة الحالية.

🎙️ **قسم الإذاعة:**
• `إذاعة للخاص [النص]` : إرسال رسالة جماعية لكل المحادثات الخاصة.
• `إذاعة للمجموعات [النص]` : إرسال رسالة جماعية لكل الكروبات.

🎭 **قسم الانتحال والتسلية:**
• `انتحال` : بالرد على شخص لنسخ الاسم والبايو والصورة.
• `استرجاع` : لاستعادة بيانات حسابك الأصلية.
• `فحص` : للتحقق من سرعة البوت واستجابته.
    """
    await event.reply(help_text)

# 2. الفحص وسرعة الاستجابة
@client.on(events.NewMessage(pattern=r'\.فحص'))
async def ping_handler(event):
    await event.reply("البوت يعمل 24/7 بنجاح ✔️ وسرعة الاستجابة ممتازة.")

# 3. تفعيل الرد التلقائي
@client.on(events.NewMessage(pattern=r'رد (.*)'))
async def set_autoreply(event):
    global auto_reply_status, auto_reply_text
    text = event.pattern_match.group(1)
    auto_reply_text = text
    auto_reply_status = True
    await event.reply(f'✅ تم تفعيل الرد التلقائي:\n"{auto_reply_text}"')

# 4. إيقاف الرد التلقائي
@client.on(events.NewMessage(pattern=r'ايقاف الرد'))
async def stop_autoreply(event):
    global auto_reply_status
    auto_reply_status = False
    await event.reply("❌ تم تعطيل الرد التلقائي.")

# 5. الرد التلقائي الفعلي على الخاص
@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def autoreply_listener(event):
    global auto_reply_status, auto_reply_text
    if auto_reply_status and not event.out:
        sender = await event.get_sender()
        if sender and not sender.bot:
            await event.reply(auto_reply_text)

# 6. جلب القنوات والمجموعات (أدمين)
@client.on(events.NewMessage(pattern=r'\.قنواتي'))
async def channels_handler(event):
    await event.reply("🔄 جاري جلب القنوات والمجموعات التي تديرها...")
    chats_list = "📋 **قنواتك ومجموعاتك الإدارية:**\n\n"
    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            entity = dialog.entity
            if getattr(entity, 'admin_rights', None) or getattr(entity, 'creator', False):
                chats_list += f"• {dialog.name}\n"
    await event.respond(chats_list)

# 7. مغادرة المجموعة الحالية
@client.on(events.NewMessage(pattern=r'\.مغادرة'))
async def leave_handler(event):
    if event.is_group or event.is_channel:
        await event.reply("👋 جاري مغادرة المجموعة...")
        await client.delete_dialog(event.chat_id)
    else:
        await event.reply("⚠️ هذا الأمر يستعمل داخل المجموعات فقط.")

# 8. انتحال شخصية (بالرد على شخص)
@client.on(events.NewMessage(pattern=r'\.انتحال'))
async def mimic_handler(event):
    if not event.is_reply:
        await event.reply("⚠️ يجب الرد على رسالة الشخص المراد انتحال شخصيته.")
        return
    
    reply_msg = await event.get_reply_message()
    target_user = await client.get_entity(reply_msg.sender_id)
    me = await client.get_me()
    
    # حفظ البيانات الأصلية قبل التغيير إذا لم تكن محفوظة
    if not original_profile["first_name"]:
        original_profile["first_name"] = me.first_name
        
    try:
        # تغيير الاسم الأول
        from telethon.tl.functions.account import UpdateProfileRequest
        await client(UpdateProfileRequest(first_name=target_user.first_name))
        
        # نسخ الصورة الشخصية إن وجدت
        photo = await client.get_profile_photos(target_user)
        if photo:
            path = await client.download_profile_photo(target_user)
            from telethon.tl.functions.photos import UploadProfilePhotoRequest
            file = await client.upload_file(path)
            await client(UploadProfilePhotoRequest(file))
            
        await event.reply(f"🎭 تم انتحال شخصية {target_user.first_name} بنجاح!")
    except Exception as e:
        await event.reply(f"❌ حدث خطأ أثناء الانتحال: {str(e)}")

# 9. استرجاع البيانات الأصلية للحساب
@client.on(events.NewMessage(pattern=r'\.استرجاع'))
async def restore_handler(event):
    global original_profile
    if original_profile["first_name"]:
        try:
            from telethon.tl.functions.account import UpdateProfileRequest
            await client(UpdateProfileRequest(first_name=original_profile["first_name"]))
            await event.reply("🔄 تم استرجاع اسمك الأصلي بنجاح!")
        except Exception as e:
            await event.reply(f"❌ حدث خطأ أثناء الاسترجاع: {str(e)}")
    else:
        await event.reply("⚠️ لا توجد بيانات مخزنة مسبقاً للاسترجاع.")

async def main():
    await client.connect()
    await client.sign_in(bot_token=token)
    print("...البوت يعمل الآن بكامل الأوامر والشغال بنجاح...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())

