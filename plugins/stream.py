import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from info import URL, BOT_USERNAME, BIN_CHANNEL, BAN_ALERT, FSUB, CHANNEL, SHORTLINK
from database.users_db import db
from web.utils.file_properties import get_hash
from utils import get_size
from Script import script
from plugins.avbot import is_user_joined, is_user_allowed, get_shortlink

@Client.on_message((filters.private) & (filters.document | filters.video | filters.audio), group=4)
async def private_receive_handler(c: Client, m: Message):
    if FSUB:
        if not await is_user_joined(c, m):
            return

    user_id = m.from_user.id

    if await db.is_banned(user_id):
        return await m.reply_text(BAN_ALERT, quote=True)

    # ✅ Limit Check
    is_allowed, remaining_time = await is_user_allowed(user_id)
    if not is_allowed:
        return await m.reply_text(
            f"🚫 **आप 10 फाइल पहले ही भेज चुके हैं!**\nकृपया **{remaining_time} सेकंड** बाद फिर से प्रयास करें।",
            quote=True
        )

    file = m.document or m.video or m.audio
    file_name = file.file_name or "Unknown File"
    file_size = get_size(file.file_size or 0)

    try:
        # ✅ Forward to BIN_CHANNEL
        msg = await m.forward(chat_id=BIN_CHANNEL)

        # 🔐 Generate File Hash Once
        file_hash = get_hash(msg)

        if not SHORTLINK:
            stream = f"{URL}watch/{msg.id}?hash={file_hash}"
            download = f"{URL}{msg.id}?hash={file_hash}"
            file_link = f"https://t.me/{BOT_USERNAME}?start=file_{msg.id}"
            share_link = f"https://t.me/share/url?url={file_link}"
        else:
            stream = await get_shortlink(f"{URL}watch/{msg.id}?hash={file_hash}")
            download = await get_shortlink(f"{URL}{msg.id}?hash={file_hash}")
            file_link = await get_shortlink(f"https://t.me/{BOT_USERNAME}?start=file_{msg.id}")
            share_link = await get_shortlink(f"https://t.me/share/url?url={file_link}")

        # ✅ BIN_CHANNEL Log
        await msg.reply_text(
            text=f"Requested By: [{m.from_user.first_name}](tg://user?id={user_id})\nUser ID: {user_id}\nStream Link: {stream}",
            disable_web_page_preview=True,
            quote=True
        )

        # ✅ Reply to User
        caption = script.CAPTION_TXT.format(CHANNEL, file_name, file_size, stream, download) \
            if file_name else script.CAPTION2_TXT.format(CHANNEL, file_name, file_size, download)

        buttons = [
            [InlineKeyboardButton(" Stream ", url=stream),
             InlineKeyboardButton(" Download ", url=download)],
            [InlineKeyboardButton("Get File", url=file_link),
             InlineKeyboardButton("Share", url=share_link),
             InlineKeyboardButton("❌ Close", callback_data='close_data')]
        ]

        await m.reply_text(
            text=caption,
            quote=True,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except FloodWait as e:
        print(f"[FloodWait] Sleeping for {e.value}s")
        await asyncio.sleep(e.value)
        await c.send_message(
            chat_id=BIN_CHANNEL,
            text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {e.value}s from [{m.from_user.first_name}](tg://user?id={user_id})\n\n**User ID :** `{user_id}`",
            disable_web_page_preview=True
    )
