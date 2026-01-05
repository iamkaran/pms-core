from fastapi import FastAPI
from routers import ingest   # these are modules

#--------------------------------------------#
#----PMS-CORE-IIOT-INGESTION-MICROSERVICE----#
# 
# A PYTHON MICROSERVICE THAT EXPOSES A API 
# ENDPOINT FOR IIOT GATEWAY DEVICES TO POST
# TELEMTRY WHICH IS FURTHER PROCESSED TO BE
# AGGREGATED ACCORDING TO THEIR ACTIVE JOB
# JOB CARDS. 
#
# ALL OF THIS IS DONE USING THINGSBOARD'S API FOR
# RETRIEVING AND POSTING DATA
# 
# [+] DEVELOPED BY: KARANVEER SINGH
# [+] PROPERTY OF:  M/s LCA INDUSTRIAL SOLUTIONS
# 
#--------------------------------------------#
# TO BE NOT USED WITHOUT PERMISSON @2025-2026
#--------------------------------------------#



# GLOBAL VARIABLES

app = FastAPI()

# Include the available routers
router_list = [ingest.router]  # <-- use .router
for router in router_list:
    app.include_router(router)
