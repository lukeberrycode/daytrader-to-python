"""FastAPI spike: one async route, SQLAlchemy 2 (async, psycopg 3), Jinja2. Run with uvicorn."""

import os
from decimal import Decimal
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from money import summary
from sqlalchemy import ForeignKey, Numeric, Text, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

HERE = Path(__file__).parent
engine = create_async_engine(
    f"postgresql+psycopg://spike:spike@127.0.0.1:{os.environ.get('PGPORT', '5433')}/spike",
    pool_size=10,
)
Session = async_sessionmaker(engine, expire_on_commit=False)
templates = Jinja2Templates(directory=HERE)
app = FastAPI()


class Base(DeclarativeBase):
    pass


class Quote(Base):
    __tablename__ = "quote"
    symbol: Mapped[str] = mapped_column(Text, primary_key=True)
    price: Mapped[Decimal] = mapped_column(Numeric(14, 2))


class Account(Base):
    __tablename__ = "account"
    user_id: Mapped[str] = mapped_column(Text, primary_key=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    open_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2))


class Holding(Base):
    __tablename__ = "holding"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("account.user_id"))
    symbol: Mapped[str] = mapped_column(ForeignKey("quote.symbol"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    quote: Mapped[Quote] = relationship(lazy="joined")


@app.get("/home/{user_id}")
async def home(request: Request, user_id: str):
    async with Session() as session:
        account = await session.get(Account, user_id)
        holdings = (await session.scalars(select(Holding).where(Holding.user_id == user_id))).all()
    rows = [(h.symbol, h.quantity, h.quote.price) for h in holdings]
    context = {"user_id": user_id, **summary(account.balance, account.open_balance, rows)}
    return templates.TemplateResponse(request, "home.html", context)
