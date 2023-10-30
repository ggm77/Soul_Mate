from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import jwt, exceptions
import json
import os
from PIL import Image
import io
from io import BytesIO
import time

from lib.DBdataLib import *

BASE_DIR = os.path.dirname(os.path.abspath("secrets.json"))
SECRET_FILE = os.path.join(BASE_DIR, "secrets.json")
secrets = json.loads(open(SECRET_FILE).read())

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = secrets["server"]["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 1



def getHashedPassword(password):
    return pwd_context.hash(password)

async def raiseDBDown():
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="DataBase down"
    )

async def somethingWrong(whatFailed):
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to "+whatFailed
    )


async def create_access_token(target):
    if(type(target) != str):
        target = str(target)
    data = {"sub":target}
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"type":"access","exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def create_refresh_token(target):
    if(type(target) != str):
        target = str(target)
    data = {"sub":target}
    expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"type":"refresh", "exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def create_token(target):
    return {"access_token":await create_access_token(target),"refresh_token":await create_refresh_token(target)}

async def decodeToken(token: str, refresh_token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except exceptions.ExpiredSignatureError:
        payload = await decodeRefreshToken(refresh_token)
        if(payload == False):
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

async def decodeRefreshToken(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    return payload



async def createUserInfo(data):


    isEmpty = await checkEmailInDB(data["email"])
    data["profilePicture"] = None
    data["password"] = getHashedPassword(data["password"])

    if(isEmpty == -2):
        await raiseDBDown()
    elif(not isEmpty):
        result = await createUserInfoDB(data)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user."
        )
    
    return result


async def getUserInfo(userNumber: int):
    user = await getUserInfoDB(userNumber)
    if(user == -2):
        await raiseDBDown()
    elif(user):
        del user["userPassword"]
        return user
    else:
        await somethingWrong("get userInfo")


async def updateUserInfo(data: dict):
    payload = await decodeToken(data["access_token"], data["refresh_token"])
    userNumber = payload.get("sub")
    info = await getUserInfo(userNumber)
    if(info == -2):
        await raiseDBDown()
    elif(info == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found."
        )
    elif(info == 0):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User disabled"
        )


    if(data["userEmail"] != None and data["userEmail"] != info["userEmail"]):
        if(await checkEmailInDB(data["email"])):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email aready exist."
            )
        
    if(data["userPassword"] != None):
        data["userPassword"] = getHashedPassword(data["userPassword"])

    keyList = list(data.keys())
    for i in range(len(keyList)):
        if(data[keyList[i]] == None):
            del data[keyList[i]]

    
    
    data["id"] = userNumber
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]
    del data["access_token"]
    del data["token_type"]
    del data["refresh_token"]
    value = await updateUserInfoDB(data)
    if(value == -2):
        await raiseDBDown()
    user = await getUserInfo(value)
    if(user == -2):
        await raiseDBDown()
    if(value != 0):
        if(payload.get("type")=="refresh"):
            return {"data":user,"token":await create_token(payload.get("sub"))}
        else:
            return {"data":user,"token":{"access_token":access_token,"refresh_token":refresh_token}}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update userInfo in DB."
        )
    

async def deleteUserInfo(id: int, token: str, refresh_token: str):
    payload = await decodeToken(token, refresh_token)
    userNumber = payload.get("sub")
    if(str(id) != userNumber):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="id not matched"
        )
    
    isDeleted = await deleteUserInfoDB(id)
    if(isDeleted == -2):
        await raiseDBDown()
    elif(isDeleted == 1):
        return True
    else:
        await somethingWrong("delete userInfo")


async def createReviewInfo(data: dict):
    payload = await decodeToken(data["access_token"], data["refresh_token"])
    userNumber = payload.get("sub")
    user = await getUserInfo(data["targetUserId"])
    if(str(data["targetUserId"]) == userNumber):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can not write review for yourself."
        )
    result = await createReviewInfoDB(data)
    if(result == -2):
        await raiseDBDown()
    elif(result == 0):
        await somethingWrong("create review")
    
    isAdded = await ratePlus(data["targetUserId"], data["rate"])
    if(isAdded == -2):
        await raiseDBDown()
    elif(isAdded == False):
        await somethingWrong("create review")

    return True

async def getReviewInfo(targetUserId: int):
    result = await getReviewInfoDB(targetUserId)
    if(result == -2):
        await raiseDBDown()
    elif(result == False):
        await somethingWrong("get review info")
    return result




async def authenticate_user(email, password):
    id = await emailToIdDB(email)
    if(id == -2):
        await raiseDBDown()
    elif(id == 0):
        await somethingWrong("get user id")
    else:
        user = await getUserInfoDB(id)
        if(user == -2):
            await raiseDBDown()
        elif(user == 0):
            await somethingWrong("get userInfo")
    if(pwd_context.verify(password, user["userPassword"])):
        return user["id"]
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password not correct.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
async def joinCategoryInfo(categoryNum: int, token: str, refresh_token: str):
    payload = await decodeToken(token, refresh_token)
    userNumber = payload.get("sub")
    isJoined = await joinCategoryInfoDB(userNumber, categoryNum)
    if(isJoined == -2):
        await raiseDBDown()
    elif(isJoined == 0):
        await somethingWrong("joinCategoryInfo")
    elif(isJoined == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already in info"
        )

    if(payload.get("type") == "refresh"):
        return create_token(userNumber)
    else:
        return {"access_token":token,"refresh_token":refresh_token} 
    

async def exitCategoryInfo(categoryNum: int, token: str, refresh_token: str):
    payload = await decodeToken(token, refresh_token)
    userNumber = payload.get("sub")
    isExited = await exitCategoryInfoDB(userNumber, categoryNum)
    if(isExited == -2):
        await raiseDBDown()
    elif(isExited == -1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="category not exist."
        )
    elif(isExited == 0):
        await somethingWrong("exit category")
    
    if(payload.get("type") == "refresh"):
        return create_token(userNumber)
    else:
        return {"access_token":token,"refresh_token":refresh_token}


async def getMentorListInfo(numberOfMentor, token, refresh_token):
    payload = await decodeToken(token, refresh_token)
    userNumber = payload.get("sub")
    user = await getUserInfo(userNumber)
    
    mentorList = await getMentorListInfoDB(user["skill"],user["lat"],user["lon"],user["joinedCategory"],numberOfMentor)
    if(mentorList == -2):
        await raiseDBDown()
    elif(mentorList == 0):
        await somethingWrong("get mentor list")
    
    return mentorList


async def getMenteeListInfo(numberOfMentee, token, refresh_token):
    payload = await decodeToken(token, refresh_token)
    userNumber = payload.get("sub")
    user = await getUserInfo(userNumber)

    menteeList = await getMenteeListInfoDB(user["skill"],user["lat"],user["lon"],user["joinedCategory"],numberOfMentee)
    if(menteeList == -2):
        await raiseDBDown()
    elif(menteeList == 0):
        await somethingWrong("get mentee list")
    
    return menteeList
    

async def getPartnerListInfo(numberOfPartner, token, refresh_token):
    payload = await decodeToken(token, refresh_token)
    userNumber = payload.get("sub")
    user = await getUserInfo(userNumber)

    partnerList = await getPartnerListInfoDB(user["skill"],user["lat"],user["lon"],user["joinedCategory"],numberOfPartner)
    if(partnerList == -2):
        await raiseDBDown()
    elif(partnerList == 0):
        await somethingWrong("get partner list")

    return partnerList



