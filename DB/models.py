from sqlalchemy import Column, Boolean, VARCHAR, FLOAT, INTEGER, DATETIME, PickleType, BLOB, TEXT, DOUBLE
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class userInfo(Base):
    __tablename__ = "userInfo"

    id = Column(INTEGER, nullable=False, primary_key=True)
    userEmail = Column(TEXT, nullable=False)
    userProfilePictureURL = Column(TEXT, nullable=True)
    userIntroduction = Column(VARCHAR, nullable=False)
    userPassword = Column(VARCHAR, nullable=False)
    userType = Column(VARCHAR, nullable=False)
    point = Column(INTEGER, nullable=False)
    disabled = Column(Boolean, nullable=False)
    isAdmin = Column(Boolean, nullable=False)
    lat = Column(DOUBLE, nullable=False)
    lon = Column(DOUBLE, nullable=False)
    skill = Column(INTEGER, nullable=False)
    joinedCategory = Column(TEXT, nullable=True)
    rateSum = Column(INTEGER, nullable=False)
    rateCount = Column(INTEGER, nullable=False)

class reviewInfo(Base):
    __tablename__ = "reviewInfo"

    id = Column(INTEGER, nullable=False, primary_key=True)
    targetUserId = Column(INTEGER, nullable=False)
    content = Column(TEXT, nullable=False)
    rate = Column(INTEGER, nullable=False)
    disabled = Column(Boolean, nullable=False)