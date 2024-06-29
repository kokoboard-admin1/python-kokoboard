from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import hashlib
import secrets
from sqlalchemy.exc import IntegrityError
from database import Base, engine, get_db
from models import User, Post
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

# CORSを回避するために追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

Base.metadata.create_all(bind=engine)

class RegisterForm(BaseModel):
    username: str
    password: str

class LoginForm(BaseModel):
    username: str
    password: str

class PostForm(BaseModel):
    session_id: str
    content: str
    reply_to: Optional[int] = None

class EditPostForm(BaseModel):
    session_id: str
    post_id: int
    new_content: str

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

websocket_manager = WebSocketManager()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_session_id() -> str:
    return secrets.token_hex(16)

@app.post("/register")
def register(user: RegisterForm, db: Session = Depends(get_db)):
    db_user = User(username=user.username, hashed_password=hash_password(user.password))
    try:
        db.add(db_user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already registered")
    return {"status": "User registered successfully"}

@app.post("/login")
def login(user: LoginForm, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user and db_user.hashed_password == hash_password(user.password):
        session_id = generate_session_id()
        db_user.session_id = session_id
        db.commit()
        return {"session_id": session_id}
    raise HTTPException(status_code=400, detail="Incorrect username or password")

@app.post("/posts")
def create_post(post: PostForm, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.session_id == post.session_id).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid session_id")
    db_post = Post(content=post.content, owner_id=db_user.id, reply_to=post.reply_to)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    response = {
        "id": db_post.id,
        "content": db_post.content,
        "owner_id": db_post.owner_id,
        "username": db_user.username,
        "timestamp": db_post.timestamp,
        "reply_to": db_post.reply_to,
        "edited": db_post.edited
    }
    return response

@app.post("/get_posts")
def get_posts(data: dict = Body(...), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.session_id == data['session_id']).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid session_id")
    posts = db.query(Post).all()
    response = [{
        "id": post.id,
        "content": post.content,
        "owner_id": post.owner_id,
        "username": db.query(User).filter(User.id == post.owner_id).first().username,
        "timestamp": post.timestamp,
        "reply_to": post.reply_to,
        "edited": post.edited
    } for post in posts]
    return {"posts": response}

@app.patch("/edit_post/{post_id}")
def edit_post(post_id: int, edit_form: EditPostForm, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.session_id == edit_form.session_id).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid session_id")
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.owner_id != db_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")
    db_post.content = edit_form.new_content
    db_post.edited = True
    db.commit()
    db.refresh(db_post)
    response = {
        "id": db_post.id,
        "content": db_post.content,
        "owner_id": db_post.owner_id,
        "username": db_user.username,
        "timestamp": db_post.timestamp,
        "reply_to": db_post.reply_to,
        "edited": db_post.edited
    }
    return response

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            if action == "register":
                user = RegisterForm(**data['data'])
                response = register(user, db)
                await websocket.send_json(response)
            elif action == "login":
                user = LoginForm(**data['data'])
                response = login(user, db)
                await websocket.send_json(response)
            elif action == "get_posts":
                response = get_posts(data['data'], db)
                await websocket.send_json(response)
            elif action == "create_post":
                post_form = PostForm(**data['data'])
                response = create_post(post_form, db)
                await websocket.send_json(response)
            elif action == "edit_post":
                edit_form = EditPostForm(**data['data'])
                response = edit_post(data['data']['post_id'], edit_form, db)
                await websocket.send_json(response)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        await websocket.send_json({"error": str(e)})