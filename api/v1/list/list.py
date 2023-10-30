from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.dataClass import *

router = APIRouter(prefix="/api/v1")

@router.post("/mentor/list")
async def getMentorList(postData: getmentorlistRequest):
    mentorList = await getMentorListInfo(postData.numberOfMentor, postData.access_token, postData.refresh_token)
    return JSONResponse({"data":mentorList})


@router.post("/mentee/list")
async def getMenteeList(postData: getmenteelistRequest):
    menteeList = await getMenteeListInfo(postData.numberOfMentee, postData.access_token, postData.refresh_token)
    return JSONResponse({"data":menteeList})

@router.post("/partner/list")
async def getPartnerList(postData: getpartnerlistRequest):
    partnerList = await getPartnerListInfo(postData.numberOfPartner, postData.access_token, postData.refresh_token)
    return JSONResponse({"data":partnerList})