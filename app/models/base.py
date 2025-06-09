"""
Base Model Classes

This module contains base model classes that provide common functionality
for all database models in the application.
"""

from datetime import datetime
from typing import Any, Dict
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class TimestampMixin:
    """Mixin class to add timestamp fields to models"""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Record creation timestamp"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Record last update timestamp"
    )


class BaseModel(Base, TimestampMixin):
    """
    Base model class with common functionality.
    
    All application models should inherit from this class.
    Provides timestamp fields and common methods.
    """
    
    __abstract__ = True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Update model instance from dictionary.
        
        Args:
            data: Dictionary with field values to update
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def __repr__(self) -> str:
        """String representation of the model"""
        class_name = self.__class__.__name__
        
        # Try to get an ID field for representation
        id_field = None
        if hasattr(self, 'id'):
            id_field = f"id={self.id}"
        elif hasattr(self, 'uuid'):
            id_field = f"uuid={self.uuid}"
        
        if id_field:
            return f"<{class_name}({id_field})>"
        else:
            return f"<{class_name}()>"
