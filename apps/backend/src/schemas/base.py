from datetime import datetime
from pydantic import BaseModel, Field

class BaseSchema(BaseModel):
    """
    Base Pydantic schema that includes common fields present in all models.
    """
    id: int | None = Field(None, description='Unique identifier')
    created_at: datetime | None = Field(None, description='Creation timestamp')
    updated_at: datetime | None = Field(None, description='Last update timestamp')

    model_config = {
        'from_attributes': True
    }
