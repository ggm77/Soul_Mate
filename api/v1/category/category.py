from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.dataClass import *

router = APIRouter(prefix="/api/v1/category")

@router.post("/join")
async def joinCategory(postData: joincategoryRequest):
    token = await joinCategoryInfo(postData.categoryNum, postData.access_token, postData.refresh_token)
    if(token):
        return JSONResponse({"result":"success","token":token})
    
@router.post("/exit")
async def exitCategory(postData: exitcategoryRequest):
    token = await exitCategoryInfo(postData.categoryNum, postData.access_token, postData.refresh_token)
    if(token):
        return JSONResponse({"result":"success","token":token})