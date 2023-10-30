from pydantic import BaseModel
from typing import Union
from datetime import datetime

class tokenRequest(BaseModel):
    email: str
    password: str


class createuserRequest(BaseModel):
    email: str
    profilePicture: str
    intro: str
    password: str
    type: str
    lat: float
    lon: float
    skill: int

class updateuserRequest(BaseModel):
    userEmail: Union[str, None]
    userProfilePicture: Union[str, None]
    userIntroduction: Union[str, None]
    userPassword: Union[str, None]
    userType: Union[str, None]
    lat: Union[float, None]
    lon: Union[float, None]
    access_token: str
    token_type: str
    refresh_token: str

class deletedataRequest(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class joincategoryRequest(BaseModel):
    categoryNum: int
    access_token: str
    token_type: str
    refresh_token: str

class exitcategoryRequest(BaseModel):
    categoryNum: int
    access_token: str
    token_type: str
    refresh_token: str

class getmentorlistRequest(BaseModel):
    numberOfMentor: int
    access_token: str
    token_type: str
    refresh_token: str

class getmenteelistRequest(BaseModel):
    numberOfMentee: int
    access_token: str
    token_type: str
    refresh_token: str

class createreviewRequest(BaseModel):
    targetUserId: int
    content: str
    rate: int
    access_token: str
    token_type: str
    refresh_token: str

class getpartnerlistRequest(BaseModel):
    numberOfPartner: int
    access_token: str
    token_type: str
    refresh_token: str