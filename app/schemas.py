from pydantic import BaseModel

class UserRegistration(BaseModel):
    wallet_address: str
    public_key: str
    username: str  # Added username

class UserLoginRequest(BaseModel):
    username: str  # Changed from wallet_address to username
    signature: str

class UserProfileUpdate(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None

class UserProfile(BaseModel):
    wallet_address: str
    public_key: str
    username: str  # Added username
    nickname: str | None
    avatar_url: str | None

class MessageCreate(BaseModel):
    author: str
    content: str
    is_encrypted: bool = False
    read_receipt: str | None = None
    delete_at: str | None = None

class Message(BaseModel):
    id: str
    timestamp: str
    channel: str
    author: str
    content: str
    is_encrypted: bool
    read_receipt: str | None
    delete_at: str | None

