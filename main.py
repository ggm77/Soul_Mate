from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from api.v1.user import user
from api.v1.token import token
from api.v1.category import category
from api.v1.list import list as mentorMenteeList
from api.v1.review import review

from lib.lib import *
from lib.DBdataLib import *

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)



templates = Jinja2Templates(directory="frontend")

app.include_router(user.router)
app.include_router(token.router)
app.include_router(category.router)
app.include_router(mentorMenteeList.router)
app.include_router(review.router)

# @app.get("/test")
# async def test(request: Request):
#     return templates.TemplateResponse("index.html",{"request":request})

# @app.get("/test2")
# async def test2():
#     data = {
#         "email":"shmshm86@naver.com",
#         "profilePicture":None,
#         "intro":"Hello, World!",
#         "password":"",
#         "type":"mentor"
#     }
#     return await createUserInfo(data)

