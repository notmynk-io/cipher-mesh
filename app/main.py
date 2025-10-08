from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import users, messages

app = FastAPI(
    title="Decentralized Messaging Backend",
    description="API for a secure, decentralized blockchain-based messaging platform",
    version="0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Decentralized Messaging Backend API"}
