from fastapi import APIRouter, HTTPException, Depends
from app.models import database, users
from app.schemas import UserRegistration, UserLoginRequest, UserProfile, UserProfileUpdate
import secrets
from eth_account.messages import encode_defunct
from eth_account.account import Account

router = APIRouter()

@router.on_event("startup")
async def startup():
    await database.connect()

@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@router.post("/register", response_model=UserProfile)
async def register_user(user: UserRegistration):
    print(f"Received registration request: {user}")
    try:
        # Check if user with wallet or username already exists
        print("Checking for existing wallet...")
        existing_wallet = await database.fetch_one(users.select().where(users.c.wallet_address == user.wallet_address))
        if existing_wallet:
            print("Wallet already registered.")
            raise HTTPException(status_code=400, detail="Wallet already registered")

        print("Checking for existing username...")
        existing_username = await database.fetch_one(users.select().where(users.c.username == user.username))
        if existing_username:
            print("Username already taken.")
            raise HTTPException(status_code=400, detail="Username already taken")

        print("Generating nonce...")
        nonce = secrets.token_hex(16)  # random nonce for sign-in challenge

        print("Inserting new user into database...")
        query = users.insert().values(
            wallet_address=user.wallet_address,
            public_key=user.public_key,
            nonce=nonce,
            username=user.username,
            nickname=None,
            avatar_url=None,
        )
        await database.execute(query)
        print("User inserted successfully.")

        profile = UserProfile(
            wallet_address=user.wallet_address,
            public_key=user.public_key,
            username=user.username,
            nickname=None,
            avatar_url=None,
        )
        print(f"Returning profile: {profile}")
        return profile
    except Exception as e:
        print(f"An error occurred: {e}")
        raise

@router.get("/nonce/{username}")
async def get_nonce(username: str):
    user = await database.fetch_one(users.select().where(users.c.username == username))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"nonce": user["nonce"]}

@router.post("/login")
async def login(request: UserLoginRequest):
    user = await database.fetch_one(users.select().where(users.c.username == request.username))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Construct Ethereum signed message for nonce
    message = encode_defunct(text=user["nonce"])
    try:
        signer = Account.recover_message(message, signature=request.signature)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if signer.lower() != user["wallet_address"].lower():
        raise HTTPException(status_code=401, detail="Signature does not match wallet address")

    # Update nonce to prevent replay attacks
    new_nonce = secrets.token_hex(16)
    await database.execute(users.update().where(users.c.username == request.username).values(nonce=new_nonce))

    return {"message": "Login successful"}

@router.get("/profile/{username}", response_model=UserProfile)
async def get_profile(username: str):
    user = await database.fetch_one(users.select().where(users.c.username == username))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfile(
        wallet_address=user["wallet_address"],
        public_key=user["public_key"],
        username=user["username"],
        nickname=user["nickname"],
        avatar_url=user["avatar_url"],
    )

@router.put("/profile/{username}", response_model=UserProfile)
async def update_profile(username: str, profile: UserProfileUpdate):
    user = await database.fetch_one(users.select().where(users.c.username == username))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = profile.dict(exclude_unset=True)
    await database.execute(users.update().where(users.c.username == username).values(update_data))

    updated_user = await database.fetch_one(users.select().where(users.c.username == username))
    return UserProfile(
        wallet_address=updated_user["wallet_address"],
        public_key=updated_user["public_key"],
        username=updated_user["username"],
        nickname=updated_user["nickname"],
        avatar_url=updated_user["avatar_url"],
    )
