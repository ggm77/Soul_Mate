from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.dataClass import *

router = APIRouter(prefix="/api/v1")

@router.post("/review")
async def createReview(postData: createreviewRequest):
    result = await createReviewInfo(jsonable_encoder(postData))
    if(result):
        return JSONResponse({"result":"success"})
    
@router.get("/review")
async def getReview(targetUserId: int):
    result = await getReviewInfo(targetUserId)
    if(result):
        return JSONResponse({"data":result})
    