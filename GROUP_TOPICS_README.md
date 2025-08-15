# Group Topics Bot - Documentation

## Overview

This bot has been enhanced with **Group Topics functionality** that allows you to:

1. **Fetch topics from Telegram groups** (forums)
2. **Extract titles, thumbnails, and videos** from each topic
3. **Store data in the bin channel** organized by topic ID
4. **Access data via API endpoints** for your web applications
5. **Browse topics through a modern web interface**

## Features

### 🔍 Topic Extraction
- Automatically fetches topics from Telegram groups
- Extracts the first text message as **title**
- Extracts the first image as **thumbnail**
- Collects all video files from the topic
- Stores everything in MongoDB database

### 📊 Data Organization
- Each topic is stored with a unique ID
- Data is organized by group ID and topic ID
- Videos are linked to their original messages
- Thumbnails are stored as file references

### 🌐 API Access
- RESTful API endpoints for accessing topic data
- JSON responses with all topic information
- Direct access to video streaming URLs
- Thumbnail serving capabilities

### 🎨 Web Interface
- Modern, responsive web interface
- Search topics by group ID
- Display thumbnails and topic information
- Direct links to video streaming

## Bot Commands

### For Admins Only

#### `/fetch_topics <group_id>`
Fetches and processes all topics from a specified group.

**Example:**
```
/fetch_topics -1001234567890
```

**What it does:**
- Connects to the specified group
- Fetches all available topics
- Extracts titles, thumbnails, and videos
- Stores data in the database
- Forwards videos to the bin channel

#### `/list_topics`
Lists all stored topics in the database.

**Response includes:**
- Topic names and IDs
- Video counts
- Processing dates
- Brief descriptions

#### `/clear_topics`
Clears all stored topics from the database.

**⚠️ Warning:** This action cannot be undone!

## API Endpoints

### Get All Topics
```
GET /api/topics?limit=50
```

**Response:**
```json
{
  "success": true,
  "topics": [
    {
      "topic_id": 123,
      "topic_name": "Sample Topic",
      "group_id": -1001234567890,
      "title": "Topic description...",
      "thumbnail": "file_id_here",
      "video_count": 5,
      "processed_at": "2024-01-01T12:00:00",
      "videos": [
        {
          "message_id": 456,
          "file_name": "video.mp4",
          "file_size": 10485760,
          "duration": 120,
          "caption": "Video caption",
          "stream_url": "/watch/456",
          "download_url": "/dl/456"
        }
      ]
    }
  ],
  "total": 1
}
```

### Get Topic by ID
```
GET /api/topics/{topic_id}?group_id={group_id}
```

**Example:**
```
GET /api/topics/123?group_id=-1001234567890
```

### Get Topics by Group
```
GET /api/topics/group/{group_id}?limit=20
```

**Example:**
```
GET /api/topics/group/-1001234567890?limit=10
```

### Get Topic Thumbnail
```
GET /api/topics/{topic_id}/thumbnail?group_id={group_id}
```

**Example:**
```
GET /api/topics/123/thumbnail?group_id=-1001234567890
```

**Response:** Direct image file (JPEG)

### Clear All Topics
```
POST /api/topics/clear
```

**Response:**
```json
{
  "success": true,
  "message": "Cleared 5 topics",
  "deleted_count": 5
}
```

## Web Interface

### Access the Topics Viewer
Visit: `https://your-bot-domain.com/topics`

### Features
- **Search by Group ID**: Enter any group ID to browse its topics
- **Topic Cards**: Beautiful cards showing topic information
- **Thumbnails**: Display topic thumbnails if available
- **Video Counts**: See how many videos are in each topic
- **Direct Links**: Click to view topic details or watch videos

### Usage
1. Open the topics page
2. Enter a group ID (e.g., `-1001234567890`)
3. Click "Search Topics"
4. Browse through the results
5. Click "View Details" or "Watch Videos" for more options

## Database Structure

### Topics Collection
```javascript
{
  "_id": ObjectId,
  "topic_id": Number,        // Telegram topic ID
  "topic_name": String,      // Topic name
  "group_id": Number,        // Telegram group ID
  "title": String,           // Extracted title/description
  "thumbnail": String,       // Telegram file ID for thumbnail
  "processed_at": String,    // ISO timestamp
  "videos": [                // Array of video objects
    {
      "message_id": Number,  // Telegram message ID
      "file_id": String,     // Telegram file ID
      "file_name": String,   // Original filename
      "file_size": Number,   // File size in bytes
      "duration": Number,    // Video duration in seconds
      "caption": String      // Video caption
    }
  ]
}
```

## Setup Instructions

### 1. Bot Requirements
- Bot must be an **admin** in the target groups
- Groups must have **topics enabled** (forums)
- Bot needs **read permissions** for messages

### 2. Database Setup
The MongoDB collection `group_topics` will be created automatically when the first topic is processed.

### 3. Environment Variables
No additional environment variables are required. The bot uses existing MongoDB connection.

## Usage Examples

### Example 1: Fetch Topics from a Group
```
/fetch_topics -1001234567890
```

### Example 2: Get Topics via API
```bash
curl "https://your-bot-domain.com/api/topics/group/-1001234567890"
```

### Example 3: Get Specific Topic
```bash
curl "https://your-bot-domain.com/api/topics/123?group_id=-1001234567890"
```

### Example 4: Access Web Interface
```
https://your-bot-domain.com/topics?group_id=-1001234567890
```

## Integration with Web Apps

### JavaScript Example
```javascript
// Fetch topics from a group
async function getTopics(groupId) {
    const response = await fetch(`/api/topics/group/${groupId}`);
    const data = await response.json();
    
    if (data.success) {
        return data.topics;
    } else {
        throw new Error(data.error);
    }
}

// Get specific topic with videos
async function getTopic(topicId, groupId) {
    const response = await fetch(`/api/topics/${topicId}?group_id=${groupId}`);
    const data = await response.json();
    
    if (data.success) {
        return data.topic;
    } else {
        throw new Error(data.error);
    }
}

// Display topic thumbnail
function getThumbnailUrl(topicId, groupId) {
    return `/api/topics/${topicId}/thumbnail?group_id=${groupId}`;
}
```

### React Example
```jsx
import React, { useState, useEffect } from 'react';

function TopicsViewer({ groupId }) {
    const [topics, setTopics] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        async function loadTopics() {
            setLoading(true);
            try {
                const response = await fetch(`/api/topics/group/${groupId}`);
                const data = await response.json();
                if (data.success) {
                    setTopics(data.topics);
                }
            } catch (error) {
                console.error('Error loading topics:', error);
            } finally {
                setLoading(false);
            }
        }

        if (groupId) {
            loadTopics();
        }
    }, [groupId]);

    return (
        <div>
            {loading ? (
                <p>Loading topics...</p>
            ) : (
                topics.map(topic => (
                    <div key={topic.topic_id}>
                        <h3>{topic.topic_name}</h3>
                        <p>{topic.title}</p>
                        <img 
                            src={`/api/topics/${topic.topic_id}/thumbnail?group_id=${topic.group_id}`}
                            alt={topic.topic_name}
                        />
                        <p>Videos: {topic.video_count}</p>
                    </div>
                ))
            )}
        </div>
    );
}
```

## Troubleshooting

### Common Issues

#### 1. "Bot needs admin rights"
**Solution:** Make the bot an admin in the target group with read permissions.

#### 2. "Group is not a forum"
**Solution:** The group must have topics enabled. Only forum groups support topics.

#### 3. "No topics found"
**Solution:** 
- Check if the group has topics enabled
- Verify the bot has access to the group
- Ensure there are actual topics in the group

#### 4. "Error fetching topics"
**Solution:**
- Check bot permissions
- Verify group ID is correct
- Ensure bot is a member of the group

### Error Codes
- `400`: Invalid request parameters
- `404`: Topic or group not found
- `500`: Internal server error

## Security Notes

- Only admins can use bot commands
- API endpoints are public but require valid parameters
- Thumbnail access is restricted to valid topic IDs
- Database queries are sanitized to prevent injection

## Performance Tips

- Use pagination with the `limit` parameter
- Cache topic data in your application
- Implement proper error handling
- Monitor database size as topics accumulate

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify bot permissions and group settings
3. Check the bot logs for detailed error messages
4. Contact support with specific error details

---

**Note:** This functionality requires the bot to be an admin in target groups and groups must have topics (forums) enabled. 