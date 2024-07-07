from pyrogram import Client, filters
import time

# Replace with your own API credentials and bot token
api_id = YOUR_API_ID
api_hash = 'YOUR_API_HASH'
bot_token = 'YOUR_BOT_TOKEN'

# IDs of users who have sudo access (replace with actual user IDs)
sudo_users = [123456789, 987654321]

# List of keywords to check for in messages
delete_keywords = ["Allen", "Chemistry", "Akash", "NCERT", "answer", "ans", "porn", "sex", "true", "false", "statement"]

# Create the Client instance
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Function to send a reply and delete the message
async def delete_message_and_notify(message, user_mention, reason):
    await message.reply_text(f"{user_mention}, {reason} and I deleted it 🗑️")
    await message.delete()

# Handler to delete edited messages in groups and notify the user
@app.on_edited_message(filters.group & ~filters.me)
async def delete_edited_messages(client, edited_message):
    if edited_message.from_user.id not in sudo_users:
        user_mention = f"@{edited_message.from_user.username}" if edited_message.from_user.username else "this user"
        await delete_message_and_notify(edited_message, user_mention, "you just edited a message")

# Handler to delete media messages in groups and notify the user
@app.on_message(filters.group & (filters.photo | filters.video | filters.document))
async def delete_media_messages(client, message):
    if message.from_user.id not in sudo_users:
        user_mention = f"@{message.from_user.username}" if message.from_user.username else "this user"
        await delete_message_and_notify(message, user_mention, "you sent media")

# Handler to delete stickers and GIFs after a time limit in groups and notify the user
async def delete_media_after_time_limit(client, message, media_type, time_limit, reason):
    if message.from_user.id not in sudo_users:
        sent_time = message.date
        current_time = time.time()
        elapsed_time = current_time - sent_time
        if elapsed_time > time_limit:
            user_mention = f"@{message.from_user.username}" if message.from_user.username else "this user"
            await delete_message_and_notify(message, user_mention, reason)

@app.on_message(filters.group & filters.sticker)
async def delete_stickers(client, message):
    await delete_media_after_time_limit(client, message, "sticker", 1800, "your sticker has been automatically deleted after 30 minutes ⏲️")

@app.on_message(filters.group & filters.animation & ~filters.sticker)
async def delete_gifs(client, message):
    await delete_media_after_time_limit(client, message, "GIF", 1800, "your GIF has been automatically deleted after 30 minutes ⏲️")

# Handler to delete messages longer than 200 words or containing specific keywords in groups and notify the user
@app.on_message(filters.group & ~filters.me)
async def delete_long_messages(client, message):
    if message.from_user.id not in sudo_users:
        user_mention = f"@{message.from_user.username}" if message.from_user.username else "this user"
        if len(message.text.split()) > 200 or any(keyword.lower() in message.text.lower() for keyword in delete_keywords):
            await delete_message_and_notify(message, user_mention, "your message matched the deletion criteria")

# Command handler for /sleepwithm to ban all members (only sudo users can use this command)
@app.on_message(filters.command("sleepwithm") & filters.me)
async def sleep_with_m(client, message):
    chat_id = message.chat.id
    if chat_id < 0:  # Ensure it's a group chat
        for member in await client.get_chat_members(chat_id):
            user_id = member.user.id
            if user_id not in sudo_users:
                await client.kick_chat_member(chat_id, user_id)
        await message.reply_text("All non-sudo members have been banned from the group.")
    else:
        await message.reply_text("This command can only be used in group chats.")

# Start the bot
app.run()
