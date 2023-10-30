from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from lib.lib import *
from lib.dataClass import *

router = APIRouter(prefix="/api/v1")

@router.post("/user")
async def createUser(postData: createuserRequest):
    id = await createUserInfo(jsonable_encoder(postData))
    return JSONResponse({"id":id})

@router.get("/user/{id}")
async def getUser(id: int):
    user = await getUserInfo(id)
    return JSONResponse({"data":user})

@router.patch("/user/{id}")
async def updateUser(updateData: updateuserRequest):
    data = await updateUserInfo(jsonable_encoder(updateData))
    return JSONResponse(data)

@router.delete("/user/{id}")
async def deleteUser(id: int, deleteData: deletedataRequest):
    result = await deleteUserInfo(id, deleteData.access_token, deleteData.refresh_token)
    if(result):
        return JSONResponse({"result":"success"})