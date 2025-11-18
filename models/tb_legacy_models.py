from pydantic import BaseModel
from enum import Enum
from uuid import UUID

class EntityType(str, Enum):
    DEVICE = "DEVICE"
    ASSET = "ASSET"
    TENANT = "TENANT"

class EntityId(BaseModel):
    id: UUID
    entityType: EntityType

class JobStatus(str, Enum):
    UNKNOWN = "unknown"
    PLANNED = "planned"
    ACTIVE = "active"
    EXPIRED = "expired"