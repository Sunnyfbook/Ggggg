import asyncio
import json
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, ChatAdminRequired, ChannelPrivate
from info import BIN_CHANNEL, LOG_CHANNEL, ADMINS
from database.users_db import db
from Script import script

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP

class GroupTopicHandler:
    def __init__(self):
        self.processed_topics = set()
    
    async def fetch_group_topics(self, client: Client, group_id: int):
        """Fetch all topics from a group"""
        try:
            # Get group info
            chat = await client.get_chat(group_id)
            if not chat.is_forum:
                return {"error": "This group is not a forum (doesn't have topics)"}
            
            topics = []
            async for topic in client.get_forum_topics_by_id(group_id, [1, 2, 3, 4, 5]):  # Get first 5 topics
                topic_data = await self.process_topic(client, group_id, topic)
                if topic_data:
                    topics.append(topic_data)
            
            return {"success": True, "topics": topics, "group_name": chat.title}
            
        except ChatAdminRequired:
            return {"error": "Bot needs admin rights to access group topics"}
        except ChannelPrivate:
            return {"error": "Bot is not a member of this group"}
        except Exception as e:
            return {"error": f"Error fetching topics: {str(e)}"}
    
    async def process_topic(self, client: Client, group_id: int, topic):
        """Process a single topic and extract data"""
        try:
            topic_id = topic.id
            topic_name = topic.name
            
            # Check if already processed
            if f"{group_id}_{topic_id}" in self.processed_topics:
                return None
            
            # Get messages from this topic
            messages = []
            async for message in client.get_chat_history(group_id, limit=50):
                if hasattr(message, 'topic') and message.topic and message.topic.id == topic_id:
                    messages.append(message)
                    if len(messages) >= 10:  # Limit to first 10 messages
                        break
            
            if not messages:
                return None
            
            # Extract data from messages
            topic_data = {
                "topic_id": topic_id,
                "topic_name": topic_name,
                "group_id": group_id,
                "title": "",
                "thumbnail": "",
                "videos": [],
                "processed_at": datetime.now().isoformat()
            }
            
            # Extract title from first text message
            for msg in messages:
                if msg.text and not topic_data["title"]:
                    topic_data["title"] = msg.text[:200]  # Limit title length
                    break
            
            # Extract thumbnail from first image
            for msg in messages:
                if msg.photo and not topic_data["thumbnail"]:
                    topic_data["thumbnail"] = msg.photo.file_id
                    break
            
            # Extract videos
            for msg in messages:
                if msg.video:
                    video_data = {
                        "message_id": msg.id,
                        "file_id": msg.video.file_id,
                        "file_name": msg.video.file_name or f"video_{msg.id}.mp4",
                        "file_size": msg.video.file_size,
                        "duration": msg.video.duration,
                        "caption": msg.caption or ""
                    }
                    topic_data["videos"].append(video_data)
            
            # Store in database
            await self.store_topic_data(topic_data)
            
            # Forward videos to bin channel with topic info
            await self.forward_to_bin_channel(client, topic_data)
            
            # Mark as processed
            self.processed_topics.add(f"{group_id}_{topic_id}")
            
            return topic_data
            
        except Exception as e:
            print(f"Error processing topic {topic_id}: {e}")
            return None
    
    async def store_topic_data(self, topic_data):
        """Store topic data in database"""
        try:
            await db.db.group_topics.update_one(
                {"topic_id": topic_data["topic_id"], "group_id": topic_data["group_id"]},
                {"$set": topic_data},
                upsert=True
            )
        except Exception as e:
            print(f"Error storing topic data: {e}")
    
    async def forward_to_bin_channel(self, client: Client, topic_data):
        """Forward videos to bin channel with topic information"""
        try:
            # Send topic info header
            header_text = f"""
📋 **Topic Information**
🏷️ **Title:** {topic_data['topic_name']}
📝 **Description:** {topic_data['title'][:100]}...
🆔 **Topic ID:** `{topic_data['topic_id']}`
📅 **Processed:** {topic_data['processed_at']}

📹 **Videos Found:** {len(topic_data['videos'])}
"""
            
            header_msg = await client.send_message(
                BIN_CHANNEL,
                header_text,
                parse_mode="markdown"
            )
            
            # Forward videos with topic context
            for video in topic_data["videos"]:
                try:
                    # Forward the video message
                    forwarded = await client.forward_messages(
                        BIN_CHANNEL,
                        from_chat_id=topic_data["group_id"],
                        message_ids=video["message_id"]
                    )
                    
                    # Add topic context to the forwarded message
                    context_text = f"""
🎬 **From Topic:** {topic_data['topic_name']}
📝 **Caption:** {video['caption'][:100] if video['caption'] else 'No caption'}
🆔 **Topic ID:** `{topic_data['topic_id']}`
"""
                    
                    await forwarded.reply_text(context_text, parse_mode="markdown")
                    
                except Exception as e:
                    print(f"Error forwarding video {video['message_id']}: {e}")
            
        except Exception as e:
            print(f"Error forwarding to bin channel: {e}")

# Initialize handler
topic_handler = GroupTopicHandler()

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP

@Client.on_message(filters.command("fetch_topics") & filters.user(ADMINS))
async def fetch_topics_command(client: Client, message: Message):
    """Command to fetch topics from a group"""
    try:
        # Extract group ID from command
        args = message.text.split()
        if len(args) < 2:
            await message.reply_text("❌ Please provide a group ID\nUsage: `/fetch_topics -1001234567890`")
            return
        
        group_id = int(args[1])
        
        # Send processing message
        status_msg = await message.reply_text("🔄 Fetching topics from group...")
        
        # Fetch topics
        result = await topic_handler.fetch_group_topics(client, group_id)
        
        if result.get("error"):
            await status_msg.edit_text(f"❌ Error: {result['error']}")
        else:
            topics_count = len(result["topics"])
            await status_msg.edit_text(
                f"✅ Successfully processed {topics_count} topics from {result['group_name']}\n"
                f"📊 Check {BIN_CHANNEL} for forwarded content"
            )
            
            # Log to admin channel
            await client.send_message(
                LOG_CHANNEL,
                f"📋 **Topics Fetched**\n"
                f"👥 **Group:** {result['group_name']}\n"
                f"📊 **Topics Processed:** {topics_count}\n"
                f"👤 **By:** {message.from_user.mention}"
            )
    
    except ValueError:
        await message.reply_text("❌ Invalid group ID format")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("list_topics") & filters.user(ADMINS))
async def list_topics_command(client: Client, message: Message):
    """Command to list stored topics"""
    try:
        topics = await db.db.group_topics.find({}).to_list(length=50)
        
        if not topics:
            await message.reply_text("📭 No topics found in database")
            return
        
        text = "📋 **Stored Topics:**\n\n"
        for topic in topics[:10]:  # Show first 10
            text += f"🏷️ **{topic['topic_name']}**\n"
            text += f"🆔 ID: `{topic['topic_id']}`\n"
            text += f"📝 Title: {topic['title'][:50]}...\n"
            text += f"📹 Videos: {len(topic['videos'])}\n"
            text += f"📅 Date: {topic['processed_at'][:10]}\n\n"
        
        if len(topics) > 10:
            text += f"... and {len(topics) - 10} more topics"
        
        await message.reply_text(text, parse_mode="markdown")
    
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@Client.on_message(filters.command("clear_topics") & filters.user(ADMINS))
async def clear_topics_command(client: Client, message: Message):
    """Command to clear all stored topics"""
    try:
        result = await db.db.group_topics.delete_many({})
        await message.reply_text(f"🗑️ Cleared {result.deleted_count} topics from database")
        
        # Clear processed topics cache
        topic_handler.processed_topics.clear()
        
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP 