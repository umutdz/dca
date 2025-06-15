# API Usage Guide

This guide provides examples of how to use the DCA API endpoints using curl commands.

## Authentication Endpoints

### Register a New User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'
```
Response will include access token and refresh token.

### Get Current User Info
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer your_access_token"
```

### Refresh Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh-token \
  -H "Authorization: Bearer your_refresh_token"
```

### Change Password
```bash
curl -X POST http://localhost:8000/api/v1/auth/change-password \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "old_password",
    "new_password": "new_password"
  }'
```

## PDF Endpoints

### Upload PDF
```bash
curl -X POST http://localhost:8000/api/v1/pdf/upload \
  -H "Authorization: Bearer your_access_token" \
  -F "file=@/path/to/your/document.pdf" \
  -F "title=Document Title" \
  -F "filename=document.pdf"
```

### List User's PDFs
```bash
curl -X GET http://localhost:8000/api/v1/pdf/list \
  -H "Authorization: Bearer your_access_token"
```

### Parse PDF
```bash
curl -X POST http://localhost:8000/api/v1/pdf/parse/{pdf_id} \
  -H "Authorization: Bearer your_access_token"
```

### Select PDF for Chat
```bash
curl -X POST http://localhost:8000/api/v1/pdf/select/{pdf_id} \
  -H "Authorization: Bearer your_access_token"
```

### Chat with PDF
```bash
curl -X POST http://localhost:8000/api/v1/pdf/chat \
  -H "Authorization: Bearer your_access_token" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic of this document?"
  }'
```

### Get Chat History
```bash
curl -X GET http://localhost:8000/api/v1/pdf/chat-history \
  -H "Authorization: Bearer your_access_token"
```

## Notes
- Replace `your_access_token` and `your_refresh_token` with actual tokens received from login/refresh endpoints
- Replace `{pdf_id}` with actual PDF ID from the list endpoint
- All endpoints require authentication except register and login
- PDF upload endpoint only accepts PDF files
- Make sure to parse the PDF before using chat features
