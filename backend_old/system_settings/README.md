# Notification Settings Backend

Backend API service for managing system notification settings across multiple channels.

## Setup Instructions

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the `backend/system_settings/` directory:

```env
# Flask
FLASK_ENV=development
DEBUG=True

# Database
DATABASE_URL=sqlite:///notification_settings.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/notif_settings

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Server
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### 4. Database Setup

```bash
# Create tables and seed initial data
cd backend/system_settings
python -c "from app.main import create_app; app = create_app(); app.app_context().push()"
```

### 5. Run the Server

```bash
# Development
python app/main.py

# Or using Flask command
flask --app app.main run

# Production (using gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 app.main:app
```

The API will be available at `http://localhost:5000/api/system-settings`

## API Endpoints

### Get All Notification Settings
```
GET /api/system-settings/notification-settings
Query Parameters:
  - page: int (default: 1)
  - per_page: int (default: 100)

Response:
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 100,
    "total": 34,
    "pages": 1
  }
}
```

### Get Single Setting
```
GET /api/system-settings/notification-settings/{event_key}

Response:
{
  "success": true,
  "data": {
    "id": 1,
    "event_key": "student_admission",
    "event_name": "Student Admission",
    ...
  }
}
```

### Create Setting
```
POST /api/system-settings/notification-settings

Body:
{
  "event_key": "custom_event",
  "event_name": "Custom Event",
  "enable_email": true,
  "enable_sms": false,
  "enable_app": true,
  "enable_whatsapp": false,
  "recipients": ["student", "guardian"],
  "sms_template_id": "TMPLT_SMS_001",
  "whatsapp_template_id": "TMPLT_WA_001",
  "sample_message": "Hello {{student_name}}"
}

Response:
{
  "success": true,
  "data": { ... }
}
```

### Update Setting
```
PUT /api/system-settings/notification-settings

Body: (same as create)

Response:
{
  "success": true,
  "data": { ... }
}
```

### Bulk Update Settings
```
POST /api/system-settings/notification-settings

Body:
{
  "settings": [
    { "event_key": "event1", "enable_email": true, ... },
    { "event_key": "event2", "enable_sms": true, ... }
  ]
}

Response:
{
  "success": true,
  "data": {
    "updated": [...],
    "errors": [...],
    "total_updated": 2,
    "total_errors": 0
  }
}
```

### Delete Setting
```
DELETE /api/system-settings/notification-settings/{event_key}

Response:
{
  "success": true,
  "message": "Setting deleted successfully"
}
```

### Export Settings
```
GET /api/system-settings/notification-settings/export?format=csv|excel|json

Response: File download or JSON
```

### Get Available Templates
```
GET /api/system-settings/notification-templates?channel=sms|whatsapp|email

Response:
{
  "success": true,
  "channel": "sms",
  "templates": [
    {"id": "TMPLT_SMS_001", "name": "Student Admission"},
    ...
  ]
}
```

## Database Schema

### notification_settings Table

| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PRIMARY KEY, AUTO_INCREMENT |
| event_key | String(255) | UNIQUE, NOT NULL, INDEX |
| event_name | String(255) | NOT NULL, INDEX |
| enable_email | Boolean | DEFAULT FALSE |
| enable_sms | Boolean | DEFAULT FALSE |
| enable_app | Boolean | DEFAULT FALSE |
| enable_whatsapp | Boolean | DEFAULT FALSE |
| recipients | JSON | DEFAULT [] |
| sms_template_id | String(255) | NULLABLE |
| whatsapp_template_id | String(255) | NULLABLE |
| sample_message | Text | NULLABLE |
| created_at | DateTime | DEFAULT now() |
| updated_at | DateTime | DEFAULT now(), ON UPDATE now() |
| updated_by | String(255) | NULLABLE |

## Error Handling

All errors follow this format:

```json
{
  "success": false,
  "error": "Error message",
  "errors": ["error1", "error2"]  // For validation errors
}
```

Common Status Codes:
- 200: Success
- 201: Created
- 400: Bad Request / Validation Error
- 404: Not Found
- 500: Server Error

## Validation Rules

1. **SMS Template ID**: Required if SMS is enabled
2. **WhatsApp Template ID**: Required if WhatsApp is enabled
3. **At least one channel**: Must have at least one notification channel enabled
4. **Event Key**: Must be unique, lowercase, underscore-separated

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_ENV=production
ENV DATABASE_URL=postgresql://...

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.main:app"]
```

### Environment Variables for Production

```env
FLASK_ENV=production
DEBUG=False
DATABASE_URL=postgresql://user:password@host/db
SECRET_KEY=production-secret-key
JWT_SECRET_KEY=production-jwt-secret
CORS_ORIGINS=https://yourdomain.com
```

## Support

For issues or questions, contact the development team.
