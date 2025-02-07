
# from alchemy_db import db.Model
from sqlalchemy import  MetaData, ForeignKey, Table
from flask_login import login_user, UserMixin
from sqlalchemy.orm import backref, relationship
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
# from app import app

db = SQLAlchemy()

metadata = MetaData()

# Association table (no model required)
likes_table = db.Table(
    "likes",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("image_id", db.Integer, db.ForeignKey("images.id"), primary_key=True)
)

#Users class, The class table name 'h1t_users_cvs'
class User(db.Model,UserMixin):

    #Create db.Columns
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))
    image = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120),unique=True)
    password = db.Column(db.String(120), unique=True)
    confirm_password = db.Column(db.String(120), unique=True)
    verified = db.Column(db.Boolean, default=False)
    contacts = db.Column(db.String(70))
    role = db.Column(db.String(120))
    images = relationship("Images",backref="User",lazy=True)
    timestamp = db.Column(db.DateTime)
     # Relationship to define which images the user has liked
    liked_images = db.relationship("Images", secondary=likes_table, back_populates="likers")
    # project_briefs = relationship("Project_Brief", backref="Project_Brief", lazy=True)

    __mapper_args__={
        "polymorphic_identity":'user',
        'polymorphic_on':role
    }


class gen_user(User):

    id = db.Column(db.Integer, ForeignKey('user.id'), primary_key=True)
    gender = db.Column(db.String(70))
    address =  db.Column(db.String(70))
    town =  db.Column(db.String(70))
    region =  db.Column(db.String(70))

    __mapper_args__={
            "polymorphic_identity":'gen_user'
        }

class admin_user(User):

    id = db.Column(db.Integer, ForeignKey('user.id'), primary_key=True)
    contacts = db.Column(db.String(20))
    address = db.Column(db.String(120))
    other = db.Column(db.String(120)) #Resume
    # jobs_applied_for = relationship("Applications", backref='Applications.job_title', lazy=True)
    # hired_user = relationship("hired", backref='Hired Applicant', lazy=True)

    __mapper_args__={
            "polymorphic_identity":'admin_user'
        }


class Images(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    uid = db.Column(db.Integer,ForeignKey("user.id"))
    img_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    image_category = db.Column(db.String(255))
    alias = db.Column(db.String(100))
    image_thumbnail = db.Column(db.String(100))
    publish=db.Column(db.Boolean,default=True)
    approved=db.Column(db.Boolean)
    timestamp=db.Column(db.DateTime)
    company_name=db.Column(db.String(100))
    company_contact=db.Column(db.String(100))
    company_email=db.Column(db.String(100))
    edited=db.Column(db.DateTime)
    edited_by=db.Column(db.String(100))
    access=relationship("Image_Access_Credits",backref="App_Info",lazy=True)
    # likes_id=relationship("Likes",backref="App_Info",lazy=True)
    # Relationship to define users who liked this image
    likers = db.relationship("User", secondary=likes_table, back_populates="liked_images")




# class Likes(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     img_id = db.Column(db.Integer, ForeignKey('images.id'))
#     liker_id = db.Column(db.Integer,ForeignKey("user.id"))
#     num_likes = db.Column(db.Integer,default=0,nullable=False)
#     timestamp = db.Column(db.DateTime)

class Image_Access_Credits(db.Model):

    __tablename__ = "image_access_credits"

    id = db.Column(db.Integer,primary_key=True)
    img_id = db.Column(db.Integer,ForeignKey("images.id"),unique=True)
    token = db.Column(db.String(255))


class stats_visitors(db.Model):

    __tablename__ = "stats_visitors"

    id = db.Column(db.Integer,primary_key=True)
    user_addr=db.Column(db.String(255))
    device=db.Column(db.String(255))
    browser=db.Column(db.String(255))
    timestamp=db.Column(db.DateTime)


class stats_image_dlink(db.Model):

    __tablename__ = "stats_app_dlink"
    id = db.Column(db.Integer,primary_key=True)
    image_name=db.Column(db.String(255))
    download_link=db.Column(db.String(255))
    # visitor_act=db.Column(db.Integer,ForeignKey("stats_visitors.id"),unique=True)
    user_addr=db.Column(db.String(255))
    device=db.Column(db.String(255))
    browser=db.Column(db.String(255))
    timestamp=db.Column(db.DateTime)


