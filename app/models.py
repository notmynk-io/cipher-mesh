from sqlalchemy import Table, Column, String, MetaData, UniqueConstraint, Boolean
from databases import Database

DATABASE_URL = "sqlite:///./test.db"  # For demo, replace with your DB URL
database = Database(DATABASE_URL)
metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("wallet_address", String, primary_key=True, index=True),
    Column("public_key", String, nullable=False),
    Column("nonce", String, nullable=False),
    Column("username", String, nullable=False, unique=True),  # Added username
    Column("nickname", String, nullable=True),
    Column("avatar_url", String, nullable=True),
    UniqueConstraint('username')
)

messages = Table(
    "messages",
    metadata,
    Column("id", String, primary_key=True, index=True),
    Column("timestamp", String, nullable=False),
    Column("content", String, nullable=False),
    Column("author", String, nullable=False),
    Column("channel", String, nullable=False),
    Column("is_encrypted", Boolean, default=False),
    Column("read_receipt", String, nullable=True),
    Column("delete_at", String, nullable=True),
)