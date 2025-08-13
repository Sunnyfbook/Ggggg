# CamGrabber Admin API

This document describes the Admin API implementation for the CamGrabber project. The admin API provides a comprehensive backend for managing the video streaming platform.

## Features

- **Authentication System**: Secure admin login with JWT tokens
- **Session Management**: Automatic session cleanup and validation
- **Statistics Tracking**: View counts, downloads, reactions, and active ads
- **Ads Management**: Banner ads and VAST ads configuration
- **Settings Management**: API, server, metadata, and page title settings
- **Activity Logging**: Comprehensive audit trail of admin actions
- **Credentials Management**: Admin account and password management

## Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Setup**
   The admin API uses MongoDB. Ensure your MongoDB connection string is properly configured in `info.py`:
   ```python
   DATABASE_URI = "mongodb+srv://username:password@cluster.mongodb.net/"
   DATABASE_NAME = "your_database_name"
   ```

3. **Environment Variables**
   Update the JWT secret in `admin_api.py` for production:
   ```python
   JWT_SECRET = "your-secure-secret-key-here"
   ```

## API Endpoints

### Authentication

#### POST `/api/admin/login`
Login to the admin panel.

**Request Body:**
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**Response:**
```json
{
    "token": "jwt_token_here",
    "user": {
        "username": "admin",
        "email": "admin@example.com"
    }
}
```

#### POST `/api/admin/logout`
Logout from the admin panel.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
    "message": "Logged out successfully"
}
```

### Statistics

#### GET `/api/admin/stats`
Get platform statistics.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
    "totalViews": 1500,
    "totalDownloads": 750,
    "totalReactions": 300,
    "activeAds": 5,
    "createdAt": "2024-01-01T00:00:00Z",
    "updatedAt": "2024-01-01T12:00:00Z"
}
```

#### POST `/api/admin/stats`
Update statistics (called automatically by frontend).

**Request Body:**
```json
{
    "action": "view|download|reaction",
    "fileId": "file_id_here",
    "title": "Video Title"
}
```

### Ads Management

#### POST `/api/admin/ads/banner`
Save banner ads configuration.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
    "top": "<script>ad_code_here</script>",
    "middle": "<script>ad_code_here</script>",
    "bottom": "<script>ad_code_here</script>",
    "sidebar": "<script>ad_code_here</script>"
}
```

#### POST `/api/admin/ads/vast`
Save VAST ads configuration.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
    "preRoll": "https://vast-url.com/preroll.xml",
    "midRoll": "https://vast-url.com/midroll.xml",
    "postRoll": "https://vast-url.com/postroll.xml"
}
```

#### GET `/api/admin/ads`
Get current ads configuration.

**Headers:** `Authorization: Bearer <token>`

### Reactions Management

#### GET `/api/admin/reactions`
Get reactions configuration.

**Headers:** `Authorization: Bearer <token>`

#### POST `/api/admin/reactions`
Save reactions configuration.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
    "enabled": true,
    "like": true,
    "dislike": true,
    "share": false
}
```

### API Settings

#### GET `/api/admin/api`
Get API configuration.

**Headers:** `Authorization: Bearer <token>`

#### POST `/api/admin/api`
Save API configuration.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
    "apiBaseUrl": "https://your-api-domain.com",
    "apiKey": "your_api_key",
    "serverPort": 8080,
    "environment": "production"
}
```

### Server Settings

#### GET `/api/admin/server`
Get server configuration.

**Headers:** `Authorization: Bearer <token>`

#### POST `/api/admin/server`
Save server configuration.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
    "serverName": "CamGrabber Server",
    "maxFileSize": 100,
    "rateLimit": 60
}
```

### Metadata Management

#### GET `/api/admin/metadata`
Get website metadata.

#### POST `/api/admin/metadata`
Save website metadata.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
    "siteTitle": "CamGrabber",
    "siteDescription": "Video streaming and download platform",
    "siteKeywords": "video, streaming, download",
    "siteAuthor": "CamGrabber Team"
}
```

### Page Titles

#### GET `/api/admin/page_titles`
Get page titles configuration.

#### POST `/api/admin/page_titles`
Save page titles configuration.

**Headers:** `Authorization: Bearer <token>`

### Credentials Management

#### GET `/api/admin/credentials`
Get admin credentials.

**Headers:** `Authorization: Bearer <token>`

#### POST `/api/admin/credentials`
Update admin credentials.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
    "username": "new_admin",
    "email": "newadmin@example.com",
    "password": "new_password"
}
```

#### POST `/api/admin/credentials/password`
Change admin password.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
    "currentPassword": "old_password",
    "newPassword": "new_password"
}
```

### Activity Logs

#### GET `/api/admin/activity`
Get activity logs.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
    {
        "message": "Admin login: admin",
        "type": "admin_login",
        "timestamp": "2024-01-01T12:00:00Z"
    }
]
```

## Admin Panel Interface

Access the admin panel at: `http://your-domain.com/admin`

### Default Credentials
- **Username:** `admin`
- **Password:** `admin123`

**Important:** Change these credentials immediately after first login!

## Database Schema

### Collections

#### `admins`
```javascript
{
    "_id": ObjectId,
    "username": String,
    "password": String, // bcrypt hashed
    "email": String,
    "createdAt": Date
}
```

#### `sessions`
```javascript
{
    "_id": ObjectId,
    "token": String,
    "adminId": ObjectId,
    "username": String,
    "createdAt": Date,
    "expiresAt": Date,
    "isActive": Boolean
}
```

#### `settings`
```javascript
{
    "_id": ObjectId,
    "key": String,
    "value": Mixed,
    "createdAt": Date,
    "updatedAt": Date
}
```

#### `stats`
```javascript
{
    "_id": ObjectId,
    "totalViews": Number,
    "totalDownloads": Number,
    "totalReactions": Number,
    "activeAds": Number,
    "createdAt": Date,
    "updatedAt": Date
}
```

#### `activities`
```javascript
{
    "_id": ObjectId,
    "message": String,
    "type": String,
    "timestamp": Date
}
```

## Security Features

1. **JWT Authentication**: Secure token-based authentication
2. **Session Management**: Automatic cleanup of expired sessions
3. **Password Hashing**: bcrypt for secure password storage
4. **CORS Protection**: Cross-origin request protection
5. **Input Validation**: Server-side validation of all inputs
6. **Activity Logging**: Complete audit trail of admin actions

## Integration with Existing Code

The admin API is integrated into the existing CamGrabber web server:

1. **File Structure:**
   ```
   camgrabber-main/
   ├── admin_api.py          # Main admin API module
   ├── web/
   │   ├── __init__.py       # Web server setup
   │   ├── stream_routes.py  # Existing routes + admin panel route
   │   └── template/
   │       └── admin.html    # Admin panel interface
   └── requirements.txt      # Updated dependencies
   ```

2. **Server Integration:**
   - Admin routes are automatically added to the web server
   - Session cleanup runs in the background
   - CORS middleware applies to admin endpoints

## Usage Examples

### Frontend Integration

```javascript
// Login
const response = await fetch('/api/admin/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'admin', password: 'admin123' })
});
const { token } = await response.json();

// Authenticated request
const stats = await fetch('/api/admin/stats', {
    headers: { 'Authorization': `Bearer ${token}` }
});
```

### Python Integration

```python
import requests

# Login
response = requests.post('http://localhost:8080/api/admin/login', json={
    'username': 'admin',
    'password': 'admin123'
})
token = response.json()['token']

# Get stats
headers = {'Authorization': f'Bearer {token}'}
stats = requests.get('http://localhost:8080/api/admin/stats', headers=headers)
```

## Error Handling

All API endpoints return consistent error responses:

```json
{
    "message": "Error description",
    "code": 400
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

## Monitoring and Maintenance

1. **Session Cleanup**: Runs automatically every hour
2. **Activity Logs**: Monitor admin actions for security
3. **Database Indexes**: Consider adding indexes for performance
4. **Backup**: Regular MongoDB backups recommended

## Troubleshooting

### Common Issues

1. **Login Fails**: Check if default admin exists, create if needed
2. **Token Expired**: Re-login to get new token
3. **Database Connection**: Verify MongoDB connection string
4. **CORS Issues**: Check browser console for CORS errors

### Debug Mode

Enable debug logging by modifying the logging level in `admin_api.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Production Deployment

1. **Change JWT Secret**: Use a strong, unique secret
2. **Update Default Credentials**: Change admin username/password
3. **Enable HTTPS**: Use SSL certificates
4. **Database Security**: Secure MongoDB access
5. **Rate Limiting**: Consider adding rate limiting middleware
6. **Monitoring**: Set up application monitoring

## Support

For issues and questions:
- Check the activity logs for error details
- Verify database connectivity
- Ensure all dependencies are installed
- Check server logs for detailed error messages 