# API Endpoints Reference - Multi-Tenant System

## Authentication Endpoints

### 1. Register New School & User
```
POST /api/v1/auth/register
Headers: Content-Type: application/json

Request:
{
  "username": "admin_school_one",
  "password": "password123",
  "email": "admin@schoolone.com",
  "mobile": "9876543210",
  "school_name": "School One"
}

Response (201):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "tenant_id": "school_one",
  "user": {
    "id": 1,
    "username": "admin_school_one",
    "email": "admin@schoolone.com",
    "tenant_id": "school_one",
    "school_name": "School One",
    "is_admin": true,
    "is_active": true,
    "created_at": "2024-05-11T10:30:00"
  }
}

Errors:
- 400: Username already registered
- 400: Invalid input data
```

### 2. Login
```
POST /api/v1/auth/login
Headers: Content-Type: application/json

Request:
{
  "username": "admin_school_one",
  "password": "password123"
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "tenant_id": "school_one",
  "user": {
    "id": 1,
    "username": "admin_school_one",
    "email": "admin@schoolone.com",
    "tenant_id": "school_one",
    "is_admin": true,
    "is_active": true,
    "created_at": "2024-05-11T10:30:00"
  }
}

Errors:
- 401: Incorrect username or password
- 403: User account is inactive
```

---

## School Management Endpoints

### 1. Create School
```
POST /api/v1/auth/schools
Headers: 
  Content-Type: application/json

Request:
{
  "name": "School One",
  "admin_email": "admin@schoolone.com",
  "admin_name": "John Doe"
}

Response (201):
{
  "id": 1,
  "name": "School One",
  "tenant_id": "school_one",
  "admin_email": "admin@schoolone.com",
  "admin_name": "John Doe",
  "is_active": true,
  "created_at": "2024-05-11T10:30:00"
}

Errors:
- 400: School name already exists
```

### 2. Get School Details
```
GET /api/v1/auth/schools/{tenant_id}

Response (200):
{
  "id": 1,
  "name": "School One",
  "tenant_id": "school_one",
  "admin_email": "admin@schoolone.com",
  "admin_name": "John Doe",
  "is_active": true,
  "created_at": "2024-05-11T10:30:00"
}

Errors:
- 404: School not found
```

### 3. List All Schools
```
GET /api/v1/auth/schools

Response (200):
[
  {
    "id": 1,
    "name": "School One",
    "tenant_id": "school_one",
    "admin_email": "admin@schoolone.com",
    "is_active": true,
    "created_at": "2024-05-11T10:30:00"
  },
  {
    "id": 2,
    "name": "School Two",
    "tenant_id": "school_two",
    "admin_email": "admin@schooltwo.com",
    "is_active": true,
    "created_at": "2024-05-11T10:35:00"
  }
]
```

---

## User Management Endpoints

### 1. Get Users for Current Tenant
```
GET /api/v1/auth/users
Headers:
  Authorization: Bearer {jwt_token}
  X-Tenant-ID: school_one

Response (200):
[
  {
    "id": 1,
    "username": "admin_school_one",
    "email": "admin@schoolone.com",
    "tenant_id": "school_one",
    "school_name": "School One",
    "is_admin": true,
    "is_active": true,
    "created_at": "2024-05-11T10:30:00"
  }
]

Errors:
- 401: X-Tenant-ID header is required
- 401: Invalid token
```

### 2. Get Current User Info
```
GET /api/v1/auth/users/me
Headers:
  Authorization: Bearer {jwt_token}
  X-Tenant-ID: school_one
  X-User-ID: 1

Response (200):
{
  "id": 1,
  "username": "admin_school_one",
  "email": "admin@schoolone.com",
  "tenant_id": "school_one",
  "school_name": "School One",
  "is_admin": true,
  "is_active": true,
  "created_at": "2024-05-11T10:30:00"
}

Errors:
- 401: Headers X-User-ID and X-Tenant-ID are required
- 404: User not found
```

### 3. Delete User (Soft Delete)
```
DELETE /api/v1/auth/users/{user_id}
Headers:
  Authorization: Bearer {jwt_token}
  X-Tenant-ID: school_one

Response (200):
{
  "message": "User deleted successfully"
}

Errors:
- 401: X-Tenant-ID header is required
- 404: User not found
```

---

## Protected Endpoints Pattern

### All Data Endpoints Require:

```
Headers:
  Authorization: Bearer {jwt_token}
  X-Tenant-ID: school_one
```

### Example: Get Vendors (Already Implemented)
```
GET /api/v1/inventory/vendors
Headers:
  Authorization: Bearer {jwt_token}
  X-Tenant-ID: school_one

Response (200):
[
  {
    "id": 1,
    "name": "Vendor A",
    "tenant_id": "school_one",
    ...
  }
]

Note: Only returns vendors where tenant_id = "school_one"
      School Two's request would return their vendors only
```

---

## Header Requirements

### Authorization Header
```
Format: Authorization: Bearer {jwt_token}
Where:  jwt_token = token returned from /auth/login or /auth/register
Used:   All protected endpoints
Note:   Token expires 24 hours after creation
        Must include for all data access
```

### X-Tenant-ID Header
```
Format: X-Tenant-ID: school_one
Where:  tenant_id = unique identifier for school
Used:   All data endpoints (vendors, inventory, sales, etc.)
Note:   Automatically injected by frontend api-client
        Must match user's tenant_id or 401 error
```

### X-User-ID Header
```
Format: X-User-ID: 1
Where:  user id = numeric user ID
Used:   Some endpoints like /auth/users/me
Note:   Automatically sent by frontend when needed
        Optional for most endpoints
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Incorrect username or password"
}
```
OR
```json
{
  "detail": "X-Tenant-ID header is required for this endpoint"
}
```

### 400 Bad Request
```json
{
  "detail": "Username already registered"
}
```

### 403 Forbidden
```json
{
  "detail": "User account is inactive"
}
```

### 404 Not Found
```json
{
  "detail": "School not found"
}
```

---

## Authentication Flow Diagram

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ├─ POST /auth/register ────┬────────────────────────┐
       │                          │                        │
       │                    Backend Validates:             │
       │                    - Username unique              │
       │                    - Hash password                │
       │                    - Generate tenant_id           │
       │                    - Create School + User         │
       │                    - Generate JWT token           │
       │                          │                        │
       │  ◄─────────────────────┬─┘────────────────────────┤
       │  Response:             │                          │
       │  - JWT token           │                          │
       │  - User info           │                          │
       │  - Tenant ID           │                          │
       │                        │                          │
       └─────────────────────────────────────────────────────┘
```

---

## Response Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Login successful |
| 201 | Created | School/User created |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Inactive account |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Database error |

---

## Testing with cURL

### Register New School
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_school_one",
    "password": "password123",
    "email": "admin@schoolone.com",
    "mobile": "9876543210",
    "school_name": "School One"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_school_one",
    "password": "password123"
  }'
```

### Get Vendors (with token)
```bash
curl -X GET http://localhost:8000/api/v1/inventory/vendors \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "X-Tenant-ID: school_one"
```

### Get Users for Tenant
```bash
curl -X GET http://localhost:8000/api/v1/auth/users \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "X-Tenant-ID: school_one"
```

