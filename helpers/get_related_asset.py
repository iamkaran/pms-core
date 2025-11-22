# Import Default Dependencies
import os
from dotenv import load_dotenv
from modules.tb_http import tb_post
from services.logger import logger as log

load_dotenv()
# Module specific imports

from models.tb_relations_query import (
    EntityRelationsQuery,
    RelationsQueryParameters,
    RelationFilter,
    RelationDirection,
    RelationTypeGroup,
)
from models.tb_legacy_models import EntityType

async def find_related_entity(device_id: str):
    '''Takes in device id and finds the related asset using a defined relation'''
    Query = EntityRelationsQuery(
        parameters=RelationsQueryParameters(
            rootId=device_id,
            rootType=EntityType.DEVICE,
            direction=RelationDirection.FROM,
            relationTypeGroup=RelationTypeGroup.COMMON,
            maxLevel=0,
            fetchLastLevelOnly=True
        ),
        filters=[
            RelationFilter(
                relationType=os.getenv("DEVICE_TO_ASSET_RELATION"),
                entityTypes=[EntityType.ASSET],
                negate=True
            )
        ]
    )
    
    log.debug(f"Query body: \n {Query.model_dump()}")
    raw = await tb_post(path="/api/relations", json_body=Query)
    if not raw:
        return None
    else:
        asset_list: list = []
        
        for obj in raw:
            id = obj["to"]["id"]
            asset_list.append(id)
        
        return asset_list
