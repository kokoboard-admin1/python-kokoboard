
# API Documentation

## HTTP Endpoints

### /register (POST)
**Summary:** Registers a new user.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
- **Success:**
  ```json
  {
    "status": "User registered successfully"
  }
  ```
- **Failure:**
  - **Status Code:** 400
  - **Error Message:** "Username already registered"

### /login (POST)
**Summary:** Logs in an existing user.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
- **Success:**
  ```json
  {
    "session_id": "string"
  }
  ```
- **Failure:**
  - **Status Code:** 400
  - **Error Message:** "Incorrect username or password"

### /posts (POST)
**Summary:** Creates a new post.

**Request Body:**
```json
{
  "session_id": "string",
  "content": "string",
  "reply_to": "integer"  // Optional
}
```

**Response:**
- **Success:**
  ```json
  {
    "id": "integer",
    "content": "string",
    "owner_id": "integer",
    "username": "string",
    "timestamp": "string",
    "reply_to": "integer",
    "edited": "boolean"
  }
  ```
- **Failure:**
  - **Status Code:** 400
  - **Error Message:** "Invalid session_id"

### /get_posts (POST)
**Summary:** Retrieves all posts.

**Request Body:**
```json
{
  "session_id": "string"
}
```

**Response:**
- **Success:**
  ```json
  {
    "posts": [
      {
        "id": "integer",
        "content": "string",
        "owner_id": "integer",
        "username": "string",
        "timestamp": "string",
        "reply_to": "integer",
        "edited": "boolean"
      },
      ...
    ]
  }
  ```
- **Failure:**
  - **Status Code:** 400
  - **Error Message:** "Invalid session_id"

### /edit_post/{post_id} (PATCH)
**Summary:** Edits an existing post.

**Request Body:**
```json
{
  "session_id": "string",
  "post_id": "integer",
  "new_content": "string"
}
```

**Response:**
- **Success:**
  ```json
  {
    "id": "integer",
    "content": "string",
    "owner_id": "integer",
    "username": "string",
    "timestamp": "string",
    "reply_to": "integer",
    "edited": "boolean"
  }
  ```
- **Failure:**
  - **Status Code:** 400
  - **Error Message:** "Invalid session_id"
  - **Status Code:** 403
  - **Error Message:** "Not authorized to edit this post"
  - **Status Code:** 404
  - **Error Message:** "Post not found"

## WebSocket Endpoints

### /ws
**Summary:** Handles real-time bidirectional communication via WebSocket.

**Actions:** Each action is sent as a JSON object.

#### register
**Summary:** Registers a new user.

**Sent Data:**
```json
{
  "action": "register",
  "data": {
    "username": "string",
    "password": "string"
  }
}
```

**Response:**
- **Success:**
  ```json
  {
    "status": "User registered successfully"
  }
  ```
- **Failure:**
  ```json
  {
    "error": "Username already registered"
  }
  ```

#### login
**Summary:** Logs in an existing user.

**Sent Data:**
```json
{
  "action": "login",
  "data": {
    "username": "string",
    "password": "string"
  }
}
```

**Response:**
- **Success:**
  ```json
  {
    "session_id": "string"
  }
  ```
- **Failure:**
  ```json
  {
    "error": "Incorrect username or password"
  }
  ```

#### get_posts
**Summary:** Retrieves all posts.

**Sent Data:**
```json
{
  "action": "get_posts",
  "data": {
    "session_id": "string"
  }
}
```

**Response:**
- **Success:**
  ```json
  {
    "posts": [
      {
        "id": "integer",
        "content": "string",
        "owner_id": "integer",
        "username": "string",
        "timestamp": "string",
        "reply_to": "integer",
        "edited": "boolean"
      },
      ...
    ]
  }
  ```
- **Failure:**
  ```json
  {
    "error": "Invalid session_id"
  }
  ```

#### create_post
**Summary:** Creates a new post.

**Sent Data:**
```json
{
  "action": "create_post",
  "data": {
    "session_id": "string",
    "content": "string",
    "reply_to": "integer"  // Optional
  }
}
```

**Response:**
- **Success:**
  ```json
  {
    "id": "integer",
    "content": "string",
    "owner_id": "integer",
    "username": "string",
    "timestamp": "string",
    "reply_to": "integer",
    "edited": "boolean"
  }
  ```
- **Failure:**
  ```json
  {
    "error": "Invalid session_id"
  }
  ```

#### edit_post
**Summary:** Edits an existing post.

**Sent Data:**
```json
{
  "action": "edit_post",
  "data": {
    "session_id": "string",
    "post_id": "integer",
    "new_content": "string"
  }
}
```

**Response:**
- **Success:**
  ```json
  {
    "id": "integer",
    "content": "string",
    "owner_id": "integer",
    "username": "string",
    "timestamp": "string",
    "reply_to": "integer",
    "edited": "boolean"
  }
  ```
- **Failure:**
  ```json
  {
    "error": "Invalid session_id"
  }
  ```
  ```json
  {
    "error": "Post not found"
  }
  ```
  ```json
  {
    "error": "Not authorized to edit this post"
  }
  ```

## Models

### User
**Columns:**
- id: Auto-increment primary key
- username: Unique username
- hashed_password: Hashed password
- session_id: Session ID

### Post
**Columns:**
- id: Auto-increment primary key
- content: Post content
- owner_id: User ID of the post owner (foreign key)
- timestamp: Timestamp
- reply_to: ID of the post being replied to (optional)
- edited: Edited flag
