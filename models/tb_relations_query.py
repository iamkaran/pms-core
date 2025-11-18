from pydantic import BaseModel
from enum import Enum
from uuid import UUID
from typing import List
from models.tb_legacy_models import EntityType

class RelationDirection(str, Enum):
    TO = "TO"
    FROM = "FROM"

class RelationTypeGroup(str, Enum):
    COMMON = "COMMON"

class RelationsQueryParameters(BaseModel):
    rootId: str
    rootType: EntityType = EntityType.DEVICE
    direction: RelationDirection = RelationDirection.FROM
    relationTypeGroup: RelationTypeGroup = RelationTypeGroup.COMMON
    maxLevel: int = 0
    fetchLastLevelOnly: bool = True

class RelationFilter(BaseModel):
    relationType: str = "ACTIVE_JOB"
    entityTypes: List[EntityType] = List[EntityType.ASSET]
    negate: bool = True

class EntityRelationsQuery(BaseModel):
    parameters: RelationsQueryParameters
    filters: List[RelationFilter] = []