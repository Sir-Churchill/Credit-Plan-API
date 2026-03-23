from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(255), unique=True, index=True)
    registration_date = Column(Date, index=True)

    credits = relationship("Credit", back_populates="user")


class Dictionary(Base):
    __tablename__ = "dictionary"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)

    payments = relationship("Payment", back_populates="payment_type")
    plans = relationship("Plan", back_populates="category")


class Credit(Base):
    __tablename__ = "credits"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    issuance_date = Column(Date, index=True)
    return_date = Column(Date, index=True)
    actual_return_date = Column(Date, index=True, nullable=True)
    body = Column(Float, index=True)
    percent = Column(Float, index=True)

    user = relationship("User", back_populates="credits")
    payments = relationship("Payment", back_populates="credit")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    sum = Column(Float, index=True)
    payment_date = Column(Date, index=True)
    credit_id = Column(Integer, ForeignKey("credits.id"))
    type_id = Column(Integer, ForeignKey("dictionary.id"))

    credit = relationship("Credit", back_populates="payments")
    payment_type = relationship("Dictionary", back_populates="payments")


class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True, index=True)
    period = Column(Date, index=True)
    sum = Column(Float, index=True)
    category_id = Column(Integer, ForeignKey("dictionary.id"))

    category = relationship("Dictionary", back_populates="plans")
