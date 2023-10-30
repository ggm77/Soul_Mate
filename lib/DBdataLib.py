from fastapi.encoders import jsonable_encoder
from datetime import timedelta, datetime
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

import json
from typing import Union

from DB.database import engineconn
from DB.models import *



engine = engineconn()
session = engine.sessionmaker()

async def emailToIdDB(email: str):
    try:
        result = (session.query(userInfo).filter(userInfo.userEmail == email).all())[0].id
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.emailToIdDB]",type(e),e)
        session.rollback()
        session.close()
        return 0
    session.close()

    return result


async def checkEmailInDB(email: str):
    try:
        result = session.execute(session.query(session.query(userInfo).filter(userInfo.userEmail == email).exists())).all()[0][0]
        session.close()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.checkEmailInDB]",type(e),e)
        session.rollback()
        session.close()
        return 0
    

    return result


async def getUserInfoDB(userNumber: int):
    try:
        result = jsonable_encoder(session.query(userInfo).filter(userInfo.id == userNumber).first())
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.getUserInfoDB]",type(e),e)
        session.rollback()
        session.close()
        return 0
    session.close()

    return result


async def createUserInfoDB(user: dict):
    data = userInfo(
        userEmail = user["email"],
        userProfilePictureURL = user["profilePicture"],
        userIntroduction = user["intro"],
        userPassword = user["password"],
        userType = user["type"],
        point = 0,
        disabled = False,
        isAdmin = False
    )
    try:
        session.add(data)
        session.commit()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.createUserInfoDB]",type(e),e)
        session.rollback()
        session.close()
        return False
    session.close()

    return await emailToIdDB(user["email"])


async def updateUserInfoDB(user: dict):
    try:
        session.query(userInfo).filter(userInfo.id == user["id"]).update(user)
        session.commit()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.updateUserInfoDB]",type(e),e)
        session.rollback()
        session.close()
        return 0
    session.close()
    return user["id"]

async def deleteUserInfoDB(id: int):
    try:
        session.delete(session.query(userInfo).filter(userInfo.id == id).first())
        session.commit()
        session.close()
        return 1
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.deleteUserInfoDB]",type(e),e)
        session.rollback()
        session.close()
        return 0
    
async def joinCategoryInfoDB(id: int, categoryNum: int):
    user = await getUserInfoDB(id)
    if(user == -2):
        return -2
    elif(user == 0):
        return 0
    category = user["joinedCategory"]
    if(category == None or category == ""):
        category = str(categoryNum)
    else:
        if(not str(categoryNum) in category.split("-")):
            category += "-"+str(categoryNum)
            try:
                session.query(userInfo).filter(userInfo.id == id).update({"joinedCategory":category})
                session.commit()
            except OperationalError:
                print(f"[{datetime.now()}] DATABASE DOWN")
                session.rollback()
                session.close()
                return -2
            except Exception as e:
                print("[DB Error - DBdataLib.joinCategoryInfoDB]",type(e),e)
                session.rollback()
                session.close()
                return 0
            session.close()
            return True
        else:
            return -1

async def exitCategoryInfoDB(id: int, categoryNum: int):
    user = await getUserInfoDB(id)
    if(user == -2):
        return -2
    elif(user == 0):
        return 0
    category = user["joinedCategory"]
    if(category == None or category == ""):
        return -1
    else:
        categoryList = category.split("-")
        if(str(categoryNum) in categoryList):
            categoryList.remove(str(categoryNum))
        else:
            return -1
        
        try:
            session.query(userInfo).filter(userInfo.id==id).update({"joinedCategory":("-".join(categoryList))})
            session.commit()
        except OperationalError:
            print(f"[{datetime.now()}] DATABASE DOWN")
            session.rollback()
            session.close()
            return -2
        except Exception as e:
            print("[DB Error - DBdataLib.joinCategoryInfoDB]",type(e),e)
            session.rollback()
            session.close()
            return 0
        session.close()
        return True

async def getMentorListInfoDB(skill, lat, lon, joinedCategory, numberOfMentor):
    mentorList = []
    try:
        value = list(session.execute(text(
            f"SELECT JSON_OBJECT(\
            'id',id,\
            'userEmail', userEmail,\
            'userProfilePictureURL', userProfilePictureURL,\
            'userIntroduction', userIntroduction,\
            'userType', userType,\
            'point', point,\
            'disabled', disabled,\
            'isAdmin', isAdmin,\
            'lat', lat,\
            'lon', lon,\
            'skill', skill,\
            'joinedCategory', joinedCategory\
            ),\
            (6371*acos(cos(radians({lat}))*cos(radians(lat))*cos(radians(lon)-radians({lon}))\
            +sin(radians({lat}))*sin(radians(lat))))AS distance\
            FROM userInfo\
            WHERE skill > {skill}\
            AND disabled != 1\
            AND userType = 'mentor'\
            ORDER BY distance\
            "
        )))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.getMentorListInfoDB]",type(e),e)
        session.rollback()
        session.close()
        return 0
    
    try:
        for i in range(numberOfMentor):
            mentorList.append(json.loads(value[i][0]))
    except IndexError:
        pass
    session.close()
    return mentorList


async def getMenteeListInfoDB(skill, lat, lon, joinedCategory, numberOfMentee):
    menteeList = []
    try:
        value = list(session.execute(text(
            f"SELECT JSON_OBJECT(\
            'id',id,\
            'userEmail', userEmail,\
            'userProfilePictureURL', userProfilePictureURL,\
            'userIntroduction', userIntroduction,\
            'userType', userType,\
            'point', point,\
            'disabled', disabled,\
            'isAdmin', isAdmin,\
            'lat', lat,\
            'lon', lon,\
            'skill', skill,\
            'joinedCategory', joinedCategory\
            ),\
            (6371*acos(cos(radians({lat}))*cos(radians(lat))*cos(radians(lon)-radians({lon}))\
            +sin(radians({lat}))*sin(radians(lat))))AS distance\
            FROM userInfo\
            WHERE skill > {skill}\
            AND disabled != 1\
            AND userType = 'mentee'\
            ORDER BY distance\
            "
        )))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.getMenteeListInfoDB]",type(e),e)
        session.rollback()
        session.close()
        return 0
    
    try:
        for i in range(numberOfMentee):
            menteeList.append(json.loads(value[i][0]))
    except IndexError:
        pass
    session.close()
    return menteeList


async def createReviewInfoDB(data: dict):
    del data["access_token"]
    del data["token_type"]
    del data["refresh_token"]
    
    info = reviewInfo(
        targetUserId = data["targetUserId"],
        content = data["content"],
        rate = data["rate"],
        disabled = False
    )
    try:
        session.add(info)
        session.commit()
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.createReviewInfoDB]",type(e),e)
        session.rollback()
        session.close()
        return 0
    session.close()
    return True


async def ratePlus(userNumber, rate):
    try:
        session.execute(text(f"update userInfo set rateSum  = userInfo.rateSum + {rate}, rateCount = userInfo.rateCount + 1 where id = {userNumber}"))
        session.commit()
        session.close()
        return True
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.ratePlus]",type(e),e)
        session.rollback()
        session.close()
        return False
    
async def getReviewInfoDB(targetUserId: int):
    try:
        result = jsonable_encoder(session.query(reviewInfo).filter(reviewInfo.targetUserId == targetUserId).all())
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.getReviewInfoDB]",type(e),e)
        session.rollback()
        session.close()
        return False
    
    session.close()
    return result

async def getPartnerListInfoDB(skill, lat, lon, joinedCategory, numberOfPartner):
    partnerList = []
    try:
        value = list(session.execute(text(
            f"SELECT JSON_OBJECT(\
            'id',id,\
            'userEmail', userEmail,\
            'userProfilePictureURL', userProfilePictureURL,\
            'userIntroduction', userIntroduction,\
            'userType', userType,\
            'point', point,\
            'disabled', disabled,\
            'isAdmin', isAdmin,\
            'lat', lat,\
            'lon', lon,\
            'skill', skill,\
            'joinedCategory', joinedCategory\
            ),\
            (6371*acos(cos(radians({lat}))*cos(radians(lat))*cos(radians(lon)-radians({lon}))\
            +sin(radians({lat}))*sin(radians(lat))))AS distance\
            FROM userInfo\
            WHERE skill >= {skill}\
            AND disabled != 1\
            ORDER BY distance\
            "
        )))
    except OperationalError:
        print(f"[{datetime.now()}] DATABASE DOWN")
        session.rollback()
        session.close()
        return -2
    except Exception as e:
        print("[DB Error - DBdataLib.getPartnerListInfoDB]",type(e),e)
        session.rollback()
        session.close()
        return 0
    
    try:
        for i in range(numberOfPartner):
            partnerList.append(json.loads(value[i][0]))
    except IndexError:
        pass
    session.close()
    return partnerList
    