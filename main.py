from fastapi import FastAPI
from routers import ingest   # these are modules

# GLOBAL VARIABLES

app = FastAPI()

# Include the available routers
router_list = [ingest.router]  # <-- use .router
for router in router_list:
    app.include_router(router)
