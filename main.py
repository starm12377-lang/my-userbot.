import os
import asyncio
import time
from telethon import TelegramClient, events, functions, types
from telethon.sessions import StringSession

# قراءة البيانات وأمان الجلسة من GitHub Secrets
API_ID = int(os.environ.get('API_ID', 30143426))  
API_HASH = os.environ.get('API_HASH', "75f5ba2107c280f86748e4c61f40aa22")  
SESSION_STRING = os.environ.get('SESSION', '')

# الاتصال باستخدام جلسة السيرفر الآمنة 24/7
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

is_away = False
away_message = "أهلاً بك، أنا مشغول حالياً.. سأرد عليك لاحقاً."
replied_users = set()
muted_users = set()
backup_data = {}

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.الاوامر$"))
async def show_help(event):
    help_text = """
✨ **مرحباً بك في سـورسـك الخـاص** ✨
──────────────────────
🎭 **انتحال الشخصية**
« `.انتحال` » ، « `.استرجاع` »

🛡 **أدوات الحماية**
« `.كتم` » ، « `.الغاء الكتم` »
« `.حظر` » ، « `.طرد` » ، « `.تقييد` »

⚙️ **إدارة المجموعات**
« `.منشغل` » ، « `.موجود` »
« `.رد [النص]` » ، « `.تثبيت` »
« `.مسح [العدد]` » ، « `.معلومات` »
« `.قنواتي` » ، « `.مغادرة` »

📢 **الإذاعة والتكرار**
« `.إذاعة للخاص [النص]` »
« `.تكرار [العدد] [النص]` »
« `.ملصق` » ، « `.فحص` »
──────────────────────
"""
    photos = await client.get_profile_photos("me", limit=1)
    if photos:
        file = await client.download_media(photos[0])
        await client.send_file(event.chat_id, file, caption=help_text)
        await event.delete()
        if os.path.exists(file): os.remove(file)
    else:
        await event.edit(help_text)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.انتحال$"))
async def clone_user_full(event):
    if not event.is_reply: return
    global backup_data
    me = await client.get_me()
    me_full = await client(functions.users.GetFullUserRequest(me.id))
    backup_data['first_name'] = me.first_name or ""
    backup_data['last_name'] = me.last_name or ""
    backup_data['about'] = me_full.full_user.about or ""
    reply = await event.get_reply_message()
    target_user_id = reply.sender_id
    target_full = await client(functions.users.GetFullUserRequest(target_user_id))
    target_entity = await client.get_entity(target_user_id)
    try:
        await client(functions.account.UpdateProfileRequest(first_name=target_entity.first_name or "", last_name=target_entity.last_name or "", about=target_full.full_user.about or ""))
    except: pass
    try:
        photos = await client.get_profile_photos(target_user_id, limit=1)
        if photos:
            file = await client.download_media(photos[0])
            await client(functions.photos.UploadProfilePhotoRequest(file=await client.upload_file(file)))
            if os.path.exists(file): os.remove(file)
    except: pass
    target_chan_id = getattr(target_full.full_user, 'personal_channel_id', None)
    my_chan_id = getattr(me_full.full_user, 'personal_channel_id', None)
    if target_chan_id and my_chan_id:
        try:
            target_chan = await client.get_entity(target_chan_id)
            my_chan = await client.get_entity(my_chan_id)
            backup_data['my_chan_id'] = my_chan_id
            backup_data['my_chan_title'] = my_chan.title
            await client(functions.channels.EditTitleRequest(channel=my_chan, title=target_chan.title))
            chan_photos = await client.get_profile_photos(target_chan, limit=1)
            if chan_photos:
                chan_file = await client.download_media(chan_photos[0])
                await client(functions.channels.EditPhotoRequest(channel=my_chan, photo=await client.upload_file(chan_file)))
                if os.path.exists(chan_file): os.remove(chan_file)
        except: pass
    await event.edit("🎭 **تم الانتحال بنجاح!**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(استرجاع|الغاء الانتحال|إلغاء الانتحال)$"))
async def restore_profile(event):
    global backup_data
    if not backup_data: return
    try:
        await client(functions.account.UpdateProfileRequest(first_name=backup_data.get('first_name', ''), last_name=backup_data.get('last_name', ''), about=backup_data.get('about', '')))
    except: pass
    if 'my_chan_id' in backup_data:
        try:
            my_chan = await client.get_entity(backup_data['my_chan_id'])
            await client(functions.channels.EditTitleRequest(channel=my_chan, title=backup_data['my_chan_title']))
        except: pass
    await event.edit("♻️ **تمت الاستعادة.**")

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private and e.media))
async def auto_save_all_media(event):
    if event.photo or event.video:
        try:
            path = await event.download_media()
            await client.send_file("me", path)
            if os.path.exists(path): os.remove(path)
        except: pass

@client.on(events.NewMessage(incoming=True))
async def check_muted_users(event):
    if event.sender_id in muted_users:
        try: await event.delete()
        except: pass

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.كتم$"))
async def mute_user(event):
    if not event.is_reply: return
    muted_users.add((await event.get_reply_message()).sender_id)
    await event.edit("🤐 **تم الكتم.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.الغاء الكتم$"))
async def unmute_user(event):
    if not event.is_reply: return
    muted_users.discard((await event.get_reply_message()).sender_id)
    await event.edit("🔊 **تم إلغاء الكتم.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.حظر$"))
async def block_user(event):
    if not event.is_reply: return
    await client(functions.contacts.BlockRequest(id=(await event.get_reply_message()).sender_id))
    await event.edit("🚫 **تم الحظر.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.طرد$"))
async def kick_user(event):
    if not event.is_reply: return
    try:
        await client.kick_participant(event.chat_id, (await event.get_reply_message()).sender_id)
        await event.edit("🚪 **تم الطرد.**")
    except: pass

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تقييد$"))
async def restrict_user(event):
    if not event.is_reply: return
    try:
        await client(functions.messages.EditChatDefaultBannedRightsRequest(peer=event.chat_id, banned_rights=types.ChatBannedRights(until_date=None, send_messages=True)))
        await event.edit("🔒 **تم التقييد.**")
    except: pass

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(إلغاء التقييد|الغاء التقييد)$"))
async def unrestrict_user(event):
    if not event.is_reply: return
    try:
        await client(functions.messages.EditChatDefaultBannedRightsRequest(peer=event.chat_id, banned_rights=types.ChatBannedRights(until_date=None, send_messages=False)))
        await event.edit("🔓 **تم فك التقييد.**")
    except: pass

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تثبيت$"))
async def pin_msg(event):
    if not event.is_reply: return
    await client.pin_message(event.chat_id, await event.get_reply_message())
    await event.edit("📌 **تم التثبيت.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.مسح (\d+)$"))
async def purge_my_messages(event):
    count = int(event.pattern_match.group(1))
    await event.delete()
    msgs = []
    async for msg in client.iter_messages(event.chat_id, from_user="me", limit=count): msgs.append(msg.id)
    if msgs: await client.delete_messages(event.chat_id, msgs)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.معلومات$"))
async def user_info(event):
    if not event.is_reply: return
    u = await client.get_entity((await event.get_reply_message()).sender_id)
    await event.edit(f"👤 {u.first_name}\n🆔 `{u.id}`")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.منشغل$"))
async def set_away(event):
    global is_away, replied_users
    is_away = True
    replied_users.clear()
    await event.edit("🔴 **تفعيل وضع الغياب.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.(موجود|ايقاف الرد|إيقاف الرد)$"))
async def set_present(event):
    global is_away, replied_users
    is_away = False
    replied_users.clear()
    await event.edit("🟢 **إيقاف الرد الآلي.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.رد (.+)"))
async def set_custom_reply(event):
    global away_message
    away_message = event.pattern_match.group(1)
    await event.edit("📝 **تم تحديث الرد.**")

@client.on(events.NewMessage(incoming=True))
async def smart_auto_reply(event):
    global is_away, replied_users, away_message
    if is_away and event.is_private:
        s = await event.get_sender()
        if s and not s.bot and s.id not in replied_users:
            await event.reply(away_message)
            replied_users.add(s.id)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.قنواتي$"))
async def list_admin_dialogs(event):
    await event.edit("🔄 **جاري الفحص..**")
    l = []
    async for d in client.iter_dialogs():
        try:
            if d.is_channel or d.is_group:
                p = await client.get_permissions(d.id, "me")
                if p and p.is_admin: l.append(f"• {d.title}")
        except: pass
    await event.edit("\n".join(l) if l else "❌ **لا يوجد.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.مغادرة$"))
async def leave_chat(event):
    await client(functions.channels.LeaveChannelRequest(event.chat_id))

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.تكرار (\d+) (.+)"))
async def spam_text(event):
    c = int(event.pattern_match.group(1))
    t = event.pattern_match.group(2)
    await event.delete()
    for _ in range(min(c, 30)):
        await event.respond(t)
        await asyncio.sleep(0.3)

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.إذاعة للخاص (.+)"))
async def broadcast_private(event):
    text = event.pattern_match.group(1)
    await event.edit("📢 **جاري الإرسال..**")
    async for d in client.iter_dialogs():
        if d.is_user and not d.entity.bot:
            try:
                await client.send_message(d.id, text)
                await asyncio.sleep(0.4)
            except: pass
    await event.edit("✅ **تمت الإذاعة.**")

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.ملصق$"))
async def convert_to_sticker(event):
    if not event.is_reply: return
    r = await event.get_reply_message()
    if r.photo:
        await event.edit("⏳ **جاري التحويل..**")
        f = await client.download_media(r)
        await client.send_file(event.chat_id, f, force_document=False)
        if os.path.exists(f): os.remove(f)
        await event.delete()

@client.on(events.NewMessage(outgoing=True, pattern=r"^\.فحص$"))
async def ping(event):
    s = time.time()
    await event.edit("⚡")
    await event.edit(f"✅ `{round((time.time()-s)*1000, 2)}ms`")

with client:
    print("...اليوزر بوت يعمل الآن على حسابك الشخصي 24/7...")
    client.run_until_disconnected()

