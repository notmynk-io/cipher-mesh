from fastapi import APIRouter, HTTPException
from app.models import database, messages
from app.schemas import Message, MessageCreate
from app.ipfs_client import IPFSClient
import datetime
import uuid

router = APIRouter()

@router.on_event("startup")
async def startup():
    await database.connect()

@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@router.get("/messages/", response_model=list[Message])
async def get_messages():
    query = messages.select().where(messages.c.channel == "general")
    db_messages = await database.fetch_all(query)

    ipfs_client = IPFSClient()
    response_messages = []
    for msg in db_messages:
        try:
            content = ipfs_client.get_bytes(msg["content"]).decode('utf-8')
        except Exception:
            content = "[Error retrieving content from IPFS]"
        
        response_messages.append(Message(
            id=msg["id"],
            timestamp=msg["timestamp"],
            channel=msg["channel"],
            author=msg["author"],
            content=content,
            is_encrypted=msg["is_encrypted"],
            read_receipt=msg["read_receipt"],
            delete_at=msg["delete_at"],
        ))
    return response_messages

@router.post("/messages/", response_model=Message)
async def create_message(message: MessageCreate):
    ipfs_client = IPFSClient()
    try:
        cid = ipfs_client.add_bytes(message.content.encode('utf-8'))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to store message on IPFS")

    message_id = str(uuid.uuid4())
    timestamp = datetime.datetime.utcnow().isoformat()
    
    query = messages.insert().values(
        id=message_id,
        timestamp=timestamp,
        channel="general",
        author=message.author,
        content=cid,  # Store CID instead of content
        is_encrypted=message.is_encrypted,
        read_receipt=message.read_receipt,
        delete_at=message.delete_at,
    )
    await database.execute(query)
    
    return Message(
        id=message_id,
        timestamp=timestamp,
        channel="general",
        author=message.author,
        content=message.content, # Return original content in this response
        is_encrypted=message.is_encrypted,
        read_receipt=message.read_receipt,
        delete_at=message.delete_at,
    )
