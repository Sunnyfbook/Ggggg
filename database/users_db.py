import re
import motor.motor_asyncio
from info import DATABASE_NAME, DATABASE_URI

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.bannedList = self.db.bannedList
        self.group_topics = self.db.group_topics

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
        )

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})
        
#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP
    
    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def ban_user(self , user_id):
        user = await self.bannedList.find_one({'banId' : int(user_id)})
        if user:
            return False
        else:
            await self.bannedList.insert_one({'banId' : int(user_id)})
            return True
        
    async def is_banned(self , user_id):
        user = await self.bannedList.find_one({'banId' : int(user_id)})
        return True if user else False

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP
    
    async def is_unbanned(self , user_id):
        try : 
            if await self.bannedList.find_one({'banId' : int(user_id)}):
                await self.bannedList.delete_one({'banId' : int(user_id)})
                return True
            else:
                return False
        except Exception as e:
            e = f'Fᴀɪʟᴇᴅ ᴛᴏ ᴜɴʙᴀɴ.Rᴇᴀsᴏɴ : {e}'
            print(e)
            return e

    # Group Topics Methods
    async def add_topic(self, topic_data):
        """Add or update a topic in database"""
        try:
            await self.group_topics.update_one(
                {"topic_id": topic_data["topic_id"], "group_id": topic_data["group_id"]},
                {"$set": topic_data},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error adding topic: {e}")
            return False
    
    async def get_topic(self, topic_id, group_id):
        """Get a specific topic by ID"""
        try:
            return await self.group_topics.find_one({"topic_id": topic_id, "group_id": group_id})
        except Exception as e:
            print(f"Error getting topic: {e}")
            return None
    
    async def get_all_topics(self, limit=50):
        """Get all topics with limit"""
        try:
            return await self.group_topics.find({}).limit(limit).to_list(length=limit)
        except Exception as e:
            print(f"Error getting topics: {e}")
            return []
    
    async def get_topics_by_group(self, group_id, limit=20):
        """Get topics from a specific group"""
        try:
            return await self.group_topics.find({"group_id": group_id}).limit(limit).to_list(length=limit)
        except Exception as e:
            print(f"Error getting group topics: {e}")
            return []
    
    async def delete_topic(self, topic_id, group_id):
        """Delete a specific topic"""
        try:
            result = await self.group_topics.delete_one({"topic_id": topic_id, "group_id": group_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting topic: {e}")
            return False
    
    async def clear_all_topics(self):
        """Clear all topics from database"""
        try:
            result = await self.group_topics.delete_many({})
            return result.deleted_count
        except Exception as e:
            print(f"Error clearing topics: {e}")
            return 0
        

db = Database(DATABASE_URI, DATABASE_NAME)

#Dont Remove My Credit @AV_BOTz_UPDATE 
#This Repo Is By @BOT_OWNER26 
# For Any Kind Of Error Ask Us In Support Group @AV_SUPPORT_GROUP

class AdsConfig:
    def __init__(self, db):
        self.col = db.ads_config

    async def get_ads(self):
        doc = await self.col.find_one({'_id': 'singleton'})
        if not doc:
            # Return default structure if not found
            return {
                'top': '', 'pre_video': '', 'post_video': '',
                'sidebar1': '', 'sidebar2': '', 'mobile': '', 'footer': ''
            }
        return doc

    async def update_ads(self, data):
        await self.col.update_one(
            {'_id': 'singleton'},
            {'$set': data},
            upsert=True
        )

ads_config = AdsConfig(db.db)
