from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, ForeignKey, CheckConstraint, Index, Date
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id             = Column(Integer, primary_key=True, index=True)
    name           = Column(String(100), nullable=False)
    email          = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password= Column(String, nullable=False)           # renamed: never store plain password
    role           = Column(String(20), nullable=False, default="viewer")
    is_active      = Column(Boolean, default=True, nullable=False)  # Boolean not Integer
    created_at     = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at     = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship — lets you do user.records directly
    records        = relationship("Record", back_populates="owner", lazy="select")

    # DB-level constraint — only valid roles can be inserted
    __table_args__ = (
        CheckConstraint(role.in_(["admin", "analyst", "viewer"]), name="valid_role"),
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"

class Record(Base):
    __tablename__ = "records"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount     = Column(Float, nullable=False)
    type       = Column(String(20), nullable=False)       # "income" | "expense"
    category   = Column(String(100), nullable=False)
    date       = Column(Date, nullable=False)    # kept as String to match your schema
    notes      = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship — lets you do record.owner directly
    owner      = relationship("User", back_populates="records")

    # DB-level constraints
    __table_args__ = (
        CheckConstraint(amount > 0, name="positive_amount"),
        CheckConstraint(type.in_(["income", "expense"]), name="valid_type"),
        # Composite index — speeds up common filtered queries
        Index("ix_records_type_category", "type", "category"),
        Index("ix_records_user_date", "user_id", "date"),
    )

    def __repr__(self):
        return f"<Record id={self.id} type={self.type} amount={self.amount}>"