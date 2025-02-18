
from flask import Flask,render_template,url_for,redirect,request,flash,jsonify,make_response,session,abort
from flask_login import login_user, LoginManager,current_user,logout_user, login_required
from sqlalchemy.exc import IntegrityError
from Forms import *
from models import *
from flask_bcrypt import Bcrypt
import secrets
# import MySQLdb
import os
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from authlib.integrations.flask_client import OAuth
# from bs4 import BeautifulSoup as bs
from flask_colorpicker import colorpicker
from image_processor import ImageProcessor
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
import itsdangerous
import random
import json
from PIL import Image
import threading
# from celery import Celery
import re
import base64

# import logging

# logging.basicConfig(level=logging.INFO)

# import sqlite3
# import pymysql
# import pyodbc

import mysql.connector
import user_agents


#Change App
app = Flask(__name__)
app.config['SECRET_KEY'] = "sdsdjfe832j2rj_32j"
if os.getenv("FLASK_DATABASE_URI"):
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:tmazst41@localhost/images_hub_db" #?driver=MySQL+ODBC+8.0+Driver"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://techtlnf_tmaz:!Tmazst41#@localhost/techtlnf_images_hub_db"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle':280}
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["CELERY_BROKER_URL"] = "redis://localhost:6379/0"
# app.config["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/0"
app.config["UPLOADED"] = 'static/uploads/usr_images'
app.config["THUMBS"] = 'static/uploads/usr_images/thumbnails'


# app.config['SESSION_TYPE'] = 'sqlalchemy'
# app.config['SESSION_SQLALCHEMY'] = db  # E.g., provided by Flask-SQLAlchemy
# Session(app)


# def make_celery(app):
#     celery = Celery(
#         app.import_name,
#         backend=app.config["CELERY_RESULT_BACKEND"],
#         broker=app.config["CELERY_BROKER_URL"],
#     )
#     celery.conf.update(app.config)
#     return celery

oauth = OAuth(app)
# Initialise App with DB 
db.init_app(app)

application = app

# run_celery = make_celery(app) 

#Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

if os.path.exists('client.json'):
    # Load secrets from JSON file
    with open('client.json') as f:
        creds = json.load(f)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)



def compress_image(image_path, target_size_kb):
    thumbnail_dir = app.config["THUMBS"]

    if not os.path.exists(thumbnail_dir):
        os.makedirs(thumbnail_dir)

    with Image.open(image_path) as img:
        img = img.convert('RGB')

        # Gradually reduce resolution
        max_width, max_height = img.size
        while True:
            file = os.path.basename(image_path)
            temp_file = os.path.join(thumbnail_dir, file)

            # Save to check size
            img.save(temp_file, format="WEBP", quality=85)

            # Check size
            if os.path.getsize(temp_file) <= target_size_kb * 1024:  # Convert KB to bytes
                print(f"Image successfully compressed to target size: {os.path.getsize(temp_file) / 1024} KB")
                break

            # Dynamically reduce resolution
            max_width = int(max_width * 0.9)
            max_height = int(max_height * 0.9)
            img = img.resize((max_width, max_height), Image.Resampling.LANCZOS)

            if max_width < 100 or max_height < 100:  # Safety check for very small images
                print("Minimum dimensions reached. Could not achieve target size.")
                break


def process_file(file,usr):
        global img_checker
        target_size = 90
        
        filename = secure_filename(file.filename)

        file_path = os.path.join(app.config["UPLOADED"])

        #static/images/usr_images
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        _img_name, _ext = os.path.splitext(file.filename)
        gen_random = secrets.token_hex(8) + "_" + str(usr.id)
        new_file_name = gen_random + _ext

        print("DEBIG IMAGE: ",new_file_name)

        if file.filename == '':
            return 'No selected file'

        if file.filename:
            new_path =os.path.join(file_path,new_file_name)
            file_saved = file.save(new_path)
            threading.Thread(target=compress_image, args=(new_path,),kwargs={"target_size_kb":90}).start()

            flash(f"File Upload Successful!!", "success")
            jsonify({"Success":"Upload Successful"})

            return new_file_name

        # else:
        #     return f"Allowed are [ .png, .jpg, .jpeg, .gif] only"


def process_profile(file,usr):
    
    print("Check File: ",file)
    if isinstance(file, str):
        return file
    else:
        filename = secure_filename(file.filename)

        _img_name, _ext = os.path.splitext(filename)
        gen_random = secrets.token_hex(8)
        new_file_name = gen_random + _ext

        if file.filename == '':
            return 'No selected file'

        print("DEBUG FILE NAME: ", file.filename)
        file_path = os.path.join("static/images", new_file_name)
        
        # Save the file first
        file.save(file_path)
        
        # Compress the image to ~90KB
        compress_image(file_path, target_size_kb=90)

        # flash("File Upload Successful!!", "success")
        return new_file_name

#Google oauth configs
if os.path.exists('client.json'):
    appConfig = {
        "OAUTH2_CLIENT_ID" : creds['clientid'],
        "OAUTH2_CLIENT_SECRET":creds['clientps'],
        "OAUTH2_META_URL":"",
        "FLASK_SECRET": app.config['SECRET_KEY'], #"sdsdjsdsdjfe832j2rj_32jfesdsdjfe832j2rj32j832",
        "FLASK_PORT": 5000  
    }


    oauth.register("appenda_oauth",
                client_id = appConfig.get("OAUTH2_CLIENT_ID"),
                client_secret = appConfig.get("OAUTH2_CLIENT_SECRET"),
                    api_base_url='https://www.googleapis.com/',
                    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo', 
                client_kwargs={ "scope" : "openid email profile"},
                server_metadata_url= 'https://accounts.google.com/.well-known/openid-configuration',
                jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
                )


ser = Serializer(app.config['SECRET_KEY']) 


#Database Tables Updates
def createall(db):
    db.create_all()


#Password Encryption
encrypt_password = Bcrypt()


# Define a custom filter
@app.template_filter('file_exists')
def file_exists_filter(filepath):
    return os.path.exists(filepath)


#Populating variables across all routes
@app.context_processor
def inject_ser():  
    

    return dict(ser=ser,os=os,home=False,comments_obj=Image_comments) #universal



@app.route("/", methods=['POST','GET'])
def home():

    images=None
    layout = None
    db.create_all()
    al = request.args.get("al") #All Images
    cat = request.args.get("cat") #categry
    comment_req = request.args.get("img_id") 
    chck_len=True
    home=True
    liked_images=None
    comments_form = CommentsForm()
    img_comments = None

    # Generate a token and store it in a session
    session["token"] = secrets.token_hex(16)

    keys = ["id","usr_id","img_id","comment","comment_by","timestamp"]
    dictn = {}

    if comment_req:
        img_comments = db.session.query(Image_comments).filter_by(img_id=comment_req).first()#db.session.get(Image_comments,comment_req)
        # print("COMMENTS OBJ: ",dir(Image_comments.__table__))
        # print("COMMENTS OBJ: ",Image_comments.__table__.columns)
        for key in keys:
            value = img_comments.__dict__.get(key)
            dictn[key] = value 
        print("Dictionary: ",dictn)

        return img_comments
    

    if current_user.is_authenticated:
        liked_images = [image.id for image in current_user.liked_images]  # List of image IDs the user has liked

    if cat:
        images = Images.query.filter_by(image_category=cat).all()
    elif al:
        images = Images.query.all()
    else:
        images = Images.query.all()

    categories= {app.image_category for app in Images.query.all()}

    if request.args.get('icon'):
        layout = request.args.get('icon')

    return render_template("index.html", images=images, layout=layout, categories=categories,usr_obj=User,chck_len=chck_len,home=home,
                           liked_images=liked_images,comments_form=comments_form,img_comments=img_comments)



@app.route('/comments', methods=['GET'])
def fetch_comments():
    # Get the img_id from query parameters
    img_id = int(request.args.get("img_id")) # Ensure it's parsed as an integer
    

    if not img_id:
        return jsonify({"error": "Invalid or missing img_id"}), 400  # Return error for invalid input

    try:
        # Fetch all comments for the given img_id
        comments = db.session.query(Image_comments).filter_by(img_id=img_id).all()

        # If no comments found
        if not comments:
            return jsonify({"comments": []})  # Return empty list if no comments exist for the image

        # Convert comments to a JSON-serializable format
        comments_list = [
            {
                "id": comment.id,
                "comment": comment.comment,
                "timestamp": comment.timestamp,
                "comment_by": comment.comment_by,
                "user_name": comment.user.name if comment.user else "Unknown",
                "user_image": comment.user.image if comment.user else "static/images/default.png",
                "deletable": current_user.is_authenticated and current_user.id == comment.comment_by
            }
            for comment in comments
        ]

        print("DEBUG ID SERVER_CODE: ", img_id)

        # Return the comments as JSON
        return jsonify({"comments": comments_list})

    except Exception as e:
        # Log the error and return a generic error response
        print(f"Error fetching comments: {e}")
        return jsonify({"error": "An error occurred while fetching comments"}), 500


@app.route('/terms_conditions')
def terms():

    return render_template("terms_conditions.html")


@app.route('/faqs')
def faq():

    return render_template("faqs.html")



#Delete Files in Thumbnail Folder
def delete_files_thmb(file):

    file_path = os.path.join(app.config["THUMBS"],file) 

    try:
        os.remove(file_path)
        flash(f"{file_path} has been deleted.")
        return True
    except FileNotFoundError:
        # flash(f"The file {file_path} does not exist.")
        return False
    except PermissionError:
        # logging.error(f"Permission denied: Unable to delete {file_path}.")
        return False
    except Exception as e:
        # logging.error(f"An error occurred: {e}")
        return False


# logging.basicConfig(level=logging.INFO)


# Function to delete files in the main directory
def delete_files_maindir(file):
    file_path = os.path.join(app.config["UPLOADED"], file)

    try:
        os.remove(file_path)
        flash(f"{file_path} has been deleted.")
        return True
    except FileNotFoundError:
        flash(f"The file {file_path} does not exist.")
        return False
    except PermissionError:
        flash(f"Permission denied: Unable to delete {file_path}.")
        return False
    except Exception as e:
        flash(f"An error occurred: {e}")
        return False


@app.route('/delete-file', methods=['GET'])
@login_required
def delete_file():

    # Primary Origin Layer 
    csrf_token = request.args.get('tkn')
    if csrf_token != session.get('token'):
        print("Token Mismatch: ",csrf_token, session.get('token'))
        return "Invalid Token", 403
    
    # Add an additional check for Referer/Origin
    origin = request.headers.get('Origin') or request.headers.get('Referer')
    if origin and "https://appenda.techxolutions.com/" not in origin:
        print("Origin: ",csrf_token,origin)
        abort(403, description="Invalid request origin")

    im_id =  request.args.get('im')
    req_img = None

    if im_id:
        req_img = ser.loads(im_id)['data']

    if not req_img:
        return jsonify({"Error": "A parameter is missing"}), 400

    img = Images.query.get(req_img)
    if not img:
        return jsonify({"Error": f"No image found with ID {req_img}"}), 404

    # Delete the image from the database
    db.session.delete(img)
    db.session.commit()

    # Delete the associated file from the filesystem
    if delete_files_maindir(img.image_thumbnail) and delete_files_thmb(img.image_thumbnail):
        return jsonify({"Success": "Image Deleted Successfully"})
    elif delete_files_maindir(img.image_thumbnail) or delete_files_thmb(img.image_thumbnail):
        return jsonify({"Success": "Image Deleted"})
    else:
        return jsonify({"Error": "Failed to delete the image file from the file system."}), 500


@app.route('/download_img', methods=['POST',"GET"])
@login_required
def download():

    img = request.args.get("img_id")
    print("DEBUG: ", img)
    images = Images.query.filter_by(id=img).first()

    return render_template("download.html", image=images, user=User)

@app.route('/logout')
def log_out():

    logout_user()

    return redirect(url_for('home'))

@app.route('/track_click', methods=['POST'])
def track_click():
    data = request.get_json()
    clicked_link = data.get('clicked_link')
    appnm = data.get('appnm')

    user_agents_str = request.headers.get('User-agent')
    user_data=user_agents.parse(user_agents_str)
    usr_addr=request.remote_addr

    if clicked_link:
        stats = stats_image_dlink(
            app_name=appnm,download_link=clicked_link,user_addr=usr_addr,device=user_data.get_device(),
            browser=user_data.get_browser(),timestamp=datetime.now()
        )

        db.session.add(stats)
        db.session.commit()
        # print(f'User clicked the link: {clicked_link}')
        # print(f'...and Name: {appnm}')
        # You can perform logging, analytics, or any other processing here

    return jsonify(success=True)

@app.route("/about", methods=['POST','GET'])
def about():

    return render_template("about.html")


def send_email(app_info,emails=None):
    
    def send_veri_mail():

        app.config["MAIL_SERVER"] = "smtp.googlemail.com"
        app.config["MAIL_PORT"] = 587
        app.config["MAIL_USE_TLS"] = True
        # Creditentials saved in environmental variables
        em = app.config["MAIL_USERNAME"] ='pro.dignitron@gmail.com' # os.getenv("MAIL")  creds.get('email')
        pwd = app.config["MAIL_PASSWORD"] = creds.get('gpass') # os.getenv("PWD")
        app.config["MAIL_DEFAULT_SENDER"] = "thabo@techxolutions.com"

        mail = Mail(app)
        ser = Serializer(app.config['SECRET_KEY']) 
        token = ser.dumps({"data":app_info.id})

        try:
            app_access=App_Access_Credits.query.filter_by(app_id=app_info.id).first()
            if app_access:
                app_access.token=token
                db.session.commit()
            else:
                db.session.add(App_Access_Credits(app_id=app_info.id,token=token))
                db.session.commit()

        except IntegrityError:
            db.session.rollback()
        
        msg = Message(subject="Promote Your Mobile App", sender="thabo@techxolutions.com", recipients=["thabo@techxolutions.com",emails])

        msg.html = f"""<html> 
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <style>
           
           body{{background-color: #e0e0e0;font-family: "Roboto" ,"Times New Roman";}}
           .mail-container{{width:60%;background-color: #ffffff;border-radius: 20px;margin:20px auto;  padding: 25px;}}
           .header{{height:100px;display: flex;justify-content: space-around;padding:15px;margin-bottom:80px ;}}
           .sub-titles{{background-color: #c4c4c4;color:white;padding:5px 10px;border-radius: 15px;font-weight: 600;font-size: 16px;}}
           p,label,small{{color:rgb(53, 53, 53)}}
           .content{{color:rgb(53, 53, 53)}}
           .scroll-container{{display: flex;justify-content: flex-start;gap:10px;align-items:center;width:max-content;}}
           .app-container{{display: flex;justify-content: center;align-items: center;flex-direction: column;width:200px;min-height: 200px;
                            gap:5px;padding:25px;border:1px solid grey;border-radius: 25px;}}
            .icon-cont img{{width:100%;border: 1px solid rgb(235, 235, 235);}}
            .app-name{{font-weight:500;font-size:23px;text-align: center;}}
            .owner-name{{font-weight:500;font-size:16px;color:#134f72;display: flex;align-items: center;}}
            .icon-imgs{{transition: all 0.3s ease;height: 30px;}}
            .icon-imgs:hover{{transform:scale(1.5)}}
            .description{{font-size:12px;color:#606060;text-align: center;}}
            .btns{{padding:10px;color:coral;border-radius:20px;border:1px solid coral;font-size: 16px;background: none;min-width:70px;  
                text-align: center;}}
            .btns:hover{{border:1px solid rgb(117, 117, 117) !important;color:rgb(117, 117, 117) !important;cursor: pointer;}}
            a{{text-decoration: none;}}
            .bolden{{font-weight:600}}
            img{{border-radius: 15px;}}
            .general-flex{{display:flex;justify-content:flex-start;align-items:center;gap:10px;flex-wrap:wrap;}}
            .mail-links{{display: flex;align-items: center;}}
            .mail-links span{{font-weight:600;font-size: 13px;color:#134f72}}
            .sign-column{{}}
            .email-sign-cont{{background-color: #f7f6f6;border-radius: 20px;padding:15px}}
            .div-line{{background-color: white;border-radius: 10px;width:7px;height:150px}}
            .services{{font-weight: 600;color:#134f72;font-size: 20px;}}
            .service{{font-weight: 500;color:#49565e}}
            .app-container {{width: 200px;min-height: 200px;border: 1px solid grey;border-radius: 25px;padding: 25px;background-color: #fff;
                overflow: hidden; /* Clear floats within the container */
            }}
            .app-cell {{
            text-align: center; /* Center the text */
        }}
        </style>
    </head>
    <body>
        <div style="width:60%;background-color: #ffffff;border-radius: 20px;margin:20px auto;  padding: 25px;"  class="mail-container">
            <!-- Header Title  -->
            <div class="header">
                <img style="height: inherit;" src="https://techxolutions.com/images/logo.png" alt="Image"" /> <img style="height: inherit;" src="https://techxolutions.com/images/eswatini_flag.png" /> 
            </div>

            <!-- Subject  -->
            <div class="subject">
               <span class="sub-titles" style="background-color: #c4c4c4;color:white;padding:5px 10px;border-radius: 15px;font-weight: 600;font-size: 16px;">Subject</span> <span style="font-size: large;">Showcase Your App on Our New Platform!</span>
            </div><br><br>

            <!-- Body Message  -->
            <section style="flex-wrap: nowrap;padding:10px" class="">
                <!-- Greeting Message  -->
                <h3 style="color:#00a550;">Good day,</h3>
                <div style="color:rgb(53, 53, 53)" class="content">My name is Thabo Maziya, and I am reaching 
                    out on behalf of Tech Xolutions(TechX). We are launching a new initiative "TechConnectPlus" aimed at enhancing
                    the visibility and accessibility of mobile applications developed in Eswatini, with a focus on better service delivery for EmaSwati.
                </div><br>

                <div style="color:rgb(53, 53, 53)" class="content"> We believe that your app <span class="bolden"> {app_info.name} </span>significantly contributes to the needs of Eswatini
                    community and would like to feature it prominently on our centralized platform. Many Mobile Apps developed locally take some time to get recognition across the whole community of EmaSwati.
    
                    This platform serve as a repository where users can easily discover and explore mobile applications 
                    that cater to their service requirements. 
                </div>
                
                <!-- Link  -->
                <div style="margin:20px auto;width:max-content"><span>Please Visit TechConnect Plus here:</span><a href="https://prelaunch.techxolutions.com" target="_blank"><span style="background-color: #00a550;color:white;padding:5px 10px;border-radius: 15px;font-weight: 600;font-size: 16px;" class="sub-titles">website</span></div></a>
                <br>
                <div style="width:60%;margin:10px auto" class="content objectives">
                    <!-- Sub Topic  -->
                    <h2 style="color:coral">Key Objects of the Project</h2>
                    <p style="vertical-align: top;"><span><img style="height:20px" src="https://techxolutions.com/images/tick-icon.png" /></span>
                        <span style="" class="bolden">Increased Awareness:</span><span >Our goal is to promote awareness among EmaSwati about diverse mobile applications, encouraging user engagement with these essential digital solutions.
                        </span></p>
                    <p><span><img style="height:20px" src="https://techxolutions.com/images/tick-icon.png" /></span>
                        <span class="bolden">Centralized Hub:</span> <span>Users will have streamlined access to a variety of apps, making it easy for them to locate the resources they need.<br>
                        <span style="color:blue"><a href="{url_for('about',  _external=True)}"> ...read more</a></span>
                    </span></p><br><br>
                <!-- Sub Topic  -->
                <h2 style="color:coral">App Verification Details</h2>
                <p  class="bolden">We invite you to verify and enhance the details of your app as it will be listed on our site. Should you wish to modify any information or links associated with your app and should you opt to<span style="color:blue"><a href="{url_for('app_form_edit', token=token, _external=True)}"> unpublish</a></span> it from this site, we have provided
                  a link below necessary to do so.
                </p>
                <!-- List  -->
                <div>
                <p style="vertical-align: top;"><span><img style="height:20px" src="https://techxolutions.com/images/tick-icon.png" /></span>
                <span style="" class="bolden">App Name:</span><span >{app_info.name}</span></p>
                </div>
                <div>
                <p style="vertical-align: top;"><span><img style="height:20px" src="https://techxolutions.com/images/tick-icon.png" /></span>
                    <span style="" class="bolden">Category:</span><span >{app_info.app_category}</span></p>
                </div>
                <div>
                <p style="vertical-align: top;"><span><img style="height:20px" src="https://techxolutions.com/images/tick-icon.png" /></span>
                    <span style="" class="bolden">Description:</span><span >{app_info.description}</span></p>
                </div>
                <div>
                <p style="vertical-align: top;"><span><img style="height:20px" src="https://techxolutions.com/images/tick-icon.png" /></span>
                    <span style="" class="bolden">Google PlayStore Link:</span><span >{app_info.playstore_link}</span></p>
                    </div><br>
                <!-- Link  -->
                <div style="margin:20px auto;width:"><span>Edit App Details Here:</span><a style="text-decoration:none" href="{url_for('app_form_edit', token=token, _external=True)}">
                <span style="background-color: #00a550;color:white;padding:5px 10px;border-radius: 15px;font-weight: 600;font-size: 16px;" class="sub-titles">App Info</span></a></div>
                <!-- Footer / Email Signature -->
                <p style="font-weight:600;font-size:13px">Note:<span style="font-weight:400">App Name, Description, Icon, and Links are sourced from Google Play Store.</span></p>
                <p style="font-weight:500;font-size:13px"><span style="font-weight:400"><span style="color:blue"><a href="{url_for('app_form',  _external=True)}"> Publising </a></span> Your App with TechConnectPlus is Free of Charge</span></p>
                <p style="font-weight:500;font-size:13px"><span style="font-weight:400"><span style="color:blue">App Access Code in TechConnect+: </span> {app_info.app_code}</span></p>
                
                </div><br><br>


                <p  class="">Kind Regards,</p> 
                <table style="font-size: medium;background-color: #f1f1f1;width:100% !important;background-color: #f7f6f6;border-radius: 20px;padding:15px" class="email-sign-cont ">
                    <tr style="font-size: medium;width:100% !important" >
                        <td style="vertical-align: top;" class="sign-column">
                            <span style="font-size: large;font-weight: 600;color:#606060">Thabo Maziya</span>
                            <span style="font-size: large;font-weight: 600;color:#606060"></span>
                            <div class="mail-links"><img style="height:25px" src="http://techxolutions.com/images/email_icon.png"/><span>thabo@techxolutions.com</span></div>
                            <div class="mail-links"><img style="height:25px" src="http://techxolutions.com/images/telephone_icon.png"/><span>(+268) 7641 2255</span></div>
                        </td>
                        <td style="vertical-align: top;" class="sign-column">
                            <div style="font-weight: 600;color:#134f72;font-size: 20px;" class="services">Tech Xolutions(TechX)</div>
                            <div class="services">Our Services</div>
                            <div class="service">Web Design & Development</div>
                            <div class="service">Graphic Design</div>
                            <div class="service">Engraving</div>
                        </td>
                        <td style="vertical-align: top;" class="sign-column">
                            <img style="height:150px;width:180px" src="http://techxolutions.com/images/Techx_logo.png" />
                        </td>
                    </tr>
                </table><br><br>
                
            </section>
            <div style="" class="email-signature">

            </div>
        </div>

        <script>
        
        </script>
    </body>
"""

        try:
            mail.send(msg)
            flash(f'Email Sent Successfully!', 'success')
            return "Email Sent"
        except Exception as e:
            flash(f'Email not sent here', 'error')
            return "The mail was not sent"

    # try:
    send_veri_mail() 


@app.route("/send_email", methods=['POST','GET'])
def email():
    app_name_rq = None
    email_form = SendEmailForm()

    if request.method == "POST":
        app_name = email_form.app_name.data

        if app_name:
            app_name_rq = App_Info.query.filter_by(name=app_name).first()
            emails = email_form.emails.data

        if app_name_rq:
            send_email(app_name_rq,emails=emails)
        else:
            return jsonify({"Error":f"App Name {app_name} Does Not Exists in the System"})

    return render_template("send_email.html",email_form=email_form)


@app.route("/comments", methods=['POST','GET'])
@login_required
def comments():

    comments_form = CommentsForm()

    if request.method == "POST":

        id = int(ser.loads(comments_form.img_id.data)['data'])
        image = db.session.get(Images, id)

        comment = Image_comments(
            #image owner
            usr_id = image.uid,
            img_id = id,
            comment = comments_form.comment.data,
            comment_by = current_user.id, #Current_user who is commenting
            timestamp = datetime.now(),
        )

        db.session.add(comment)
        db.session.commit()

        flash("Comment Sent Successfully", "success")

        return redirect(url_for('comments'))

    return f'' # render_template("comments.html",comments_form=comments_form)


@app.route("/image_form", methods=['POST','GET'])
@login_required
def image_form():

    app_form = ImagesForm()
    timestamp=None

    if request.method == "POST":

        image_info = Images(
            img_name=app_form.name.data.strip(),description=app_form.description.data.strip(),
            image_category=app_form.image_category.data,timestamp=datetime.now(),uid=current_user.id,alias=app_form.alias.data.strip(),
            hint=app_form.hint.data,comments_bool=bool(app_form.comments_bool.data)
            )

        if app_form.image.data:
            image_info.image_thumbnail = process_file(app_form.image.data,current_user)

        db.session.add(image_info)
        db.session.commit()
        # print()
        # img = Images.query.filter_by(timestamp=timestamp).first()
        # zero_likes = Likes(img_id=img.id,liker_id=current_user.id,timestamp=timestamp,num_likes=0)
        # db.session.add(zero_likes)
        # db.session.commit()

        # flash("Upload was Successful👍","success")
        return jsonify({"Success":"Thank You!, You can check your image 5 minutes from now"})

    return render_template("image_form.html",app_form=app_form)


# Route to handle likes
@app.route("/like", methods=["GET", "POST"])
@login_required
def like_image():
    # Get the image ID from the query parameter
    img_id = request.args.get("im", type=int)
    
    # Query the image from the database
    image = Images.query.get_or_404(img_id)

    # Check if the user has already liked the image
    if current_user in image.likers:
        # User has already liked the image; unlike it (remove from relationship)
        image.likers.remove(current_user)
        db.session.commit()
        return jsonify({"status": "unliked", "likes_count": len(image.likers)})
    else:
        # User has not liked the image; add the like
        image.likers.append(current_user)
        db.session.commit()
        return jsonify({"status": "liked", "likes_count": len(image.likers)})


@app.route("/edit_app", methods=['POST','GET'])
def edit_app():

    edit_app = EditAppInfoForm()

        # if request.args.get('id'): se
    if request.method == 'POST':

        print("Debeug Get Req. from form: ",edit_app.app_code.data ," ",edit_app.app_name.data)

        code_ = ser.dumps({"data":edit_app.app_code.data})

        # print("Debeug Get Req. from form: ",code_)

        return redirect(url_for("app_form_editor",app_name=edit_app.app_name.data,code=code_))

    return render_template("edit_app.html",edit_app=edit_app)


class Save_Values:
    app_obj=None

# Create a custom Jinja2 filter to remove special characters
@app.template_filter('remove_special_chars')
def remove_special_chars(s):
    return re.sub(r'[^a-zA-Z0-9\s]', '', s)


# app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=7)  # Duration for "remember me" cookies
# app.config["SESSION_PERMANENT"] = False  # Temporary sessions unless 'remember=True'

# Flask-Login callback to load user
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))


@app.route("/signup", methods=["POST","GET"])
def sign_up():

    register = Register()
    user = None
    home=True
 
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':

        if register.validate_on_submit():    

            hashd_pwd = encrypt_password.generate_password_hash(register.password.data).decode('utf-8')

            user = gen_user(
                    name=register.name.data, email=register.email.data, password=hashd_pwd,
                    confirm_password=hashd_pwd,image="default.png",timestamp=datetime.now().strftime("%d-%m-%y %H:%M:%S")
                    )

            if not Register().validate_email(register.email.data):
                db.session.add(user)
                db.session.commit()
                print('Sign up successful!')
                flash(f"Account Successfully Created for {register.name.data}", "success")
                # Automatically log the user in after signup
                login_user(user, remember=True)  # Set 'remember=True' to keep logged in
            else:
                flash(f"Something went wrong, check for errors", "error")
                print('Sign up unsuccessful')

            return redirect(url_for('login'))

        elif register.errors:
            flash(f"Account Creation Unsuccessful ", "error")
            print(register.errors)

    # from myproject.models import user
    return render_template("signup_form.html",register=register,home=home)


# User Account
@app.route("/account", methods=["POST", "GET"])
def user_account():

    usr_account=gen_user.query.get(current_user.id)
    account_form = AccountForm(obj=usr_account)

    if account_form.validate_on_submit():

        if request.method == 'POST':

            usr_account.contacts=account_form.contacts.data
            usr_account.town=account_form.town.data
            usr_account.address=account_form.address.data
            
            if account_form.image.data:
                usr_account.image = process_profile(account_form.image.data,usr_account)

            # try:
            db.session.commit()
            flash(f"Update Successful!", "success")
            print("Update Successful!")
            return redirect(url_for('user_account'))
    else:
        if account_form.errors:
            for error in account_form:
                print("ERROR: ",error)

    return render_template('account.html',account_form =account_form, usr_account=usr_account)


# @app.route("/login_auto", methods=["POST","GET"])
# def login():

#     login = Login()

#     # Get the stored device token from the incoming cookies
#     device_token = request.cookies.get('device_token')
#     username = request.cookies.get('username')
#     usrs_dev_token = db.session.query(user_devices).filter_by(device_token=device_token).first()

#     if usrs_dev_token:
#         if username == usrs_dev_token.user.email:
#             login_user(db.session.get(User, usrs_dev_token.uid))
#         else:
#             return redirect(url_for('login'))

#     return render_template("login.html",login=login,home=True)


@app.route("/login", methods=["POST","GET"])
def login():

    if current_user.is_authenticated:
        flash(f"Welcome {current_user.name}","success")
        return redirect(url_for('home'))

    login = Login()

    if login.validate_on_submit():

        if request.method == 'POST':

            user_login = User.query.filter_by(email=login.email.data).first()
            if user_login and encrypt_password.check_password_hash(user_login.password, login.password.data):
                login_user(user_login)
                # Generate a random token for the device
                device_token = secrets.token_hex(32)
                username = login.email.data
                response = make_response("Success!")
                # Store it in a secure HTTP-only cookie
                response.set_cookie('device_token', device_token, httponly=True, secure=True)
                response.set_cookie("username", username, httponly=True, secure=True)

                save_dv_token = user_devices(uid=current_user.id,device_token=device_token)
                db.session.add(save_dv_token)
                db.session.commit()

                # if not user_login.verified:
                #     login_user(user_login)
                #     return redirect(url_for('verification'))
                # else:
                # After login required prompt, take me to the page I requested earlier
                # login_user(user_login)
                # print("No Verification Needed: ", user_login.verified)

                
                flash(f"Welcome! {user_login.name.title()}", "success")

                req_page = request.args.get('next')
                return redirect(req_page) if req_page else redirect(url_for('home'))
                
            else:
                flash(f"Login Unsuccessful, please use correct email or password", "error")
                # print(login.errors)
    else:
        print("No Validation")
        if login.errors:
            for error in login.errors:
                print("Errors: ", error)
        else:
            print("No Errors found", login.email.data, login.password.data)

    return render_template("login.html",login=login,home=True)


@app.route('/search', methods=['GET'])
def search_in_table():

    apps_obj = Images()
    categories= {app.image_category for app in Images.query.all()}

    search_value = request.args.get('search_value')
    table_name = "images"  # request.args.get('table_name')

    # Database connection parameters
    db_config = {
        'user': creds['user'],
        'password': creds['db_pass'],
        'host': 'localhost',  # or your MySQL server address
        'database': 'techtlnf_images_hub_db' #
    }

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Use parameters to avoid SQL injection
    query = f"SELECT * FROM `{table_name}` WHERE CONCAT(COALESCE(img_name, ''), COALESCE(description, ''), COALESCE(image_category, '')) LIKE %s"
    cursor.execute(query, ('%' + search_value + '%',))
    rows = cursor.fetchall()

    

    # Convert the results to a list of dictionaries (depending on your needs)
    rows = [{'id': row[0], 'uid': row[1], 'img_name': row[2], 'description': row[3], 'category': row[4], 
             'image_thumbnail': row[6]} for row in rows]
    
    # Print results for debugging
    for row in rows:
        print("Car Make: ", row)

    cursor.close()
    conn.close()

    return render_template('search_results.html', images=rows, categories=categories,usr_obj=User,search_value=search_value)


@app.route("/google_signup", methods=["POST","GET"])
def google_signup():

    return render_template('google_signup.html')

#google login
@app.route("/google_login", methods=["POST","GET"])
def google_login():

    # Step 1: Generate a nonce and store it in the session for validation
    nonce = os.urandom(16).hex()  # Generate a random string
    session['nonce'] = nonce  # Save nonce to session


    return oauth.appenda_oauth.authorize_redirect(redirect_uri=url_for("google_signin",_external=True),nonce=nonce)


#login redirect
@app.route("/google_signin", methods=["POST","GET"])
def google_signin():

    # Step 1: Handle the OAuth2 callback and exchange the authorization code for an access token
    token = oauth.appenda_oauth.authorize_access_token()

    nonce = session.pop('nonce', None)

    if not nonce:
        return jsonify({'Error':"Something Went Missing With Your Sign in, Please Retry"})
    
    # Step 2: Parse the ID token from the response to get user information
    user_info = oauth.appenda_oauth.parse_id_token(token,nonce=nonce)
    
    # Step 3: Store user info in the Flask session for persistence
    session['user'] = user_info

    verified = user_info.get("email_verified")
    usr_email = user_info.get("email")
    usr_name=user_info.get("name")
    usr_athash=user_info.get("at_hash")

    if not verified:
        flash("Access Denied!, Your Email is not verified with Google")
        flash("Please, Set up your account manually")
        return redirect(url_for('sign_up'))
    
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    #Sign Up
    if not User.query.filter_by(email=usr_email).first():

        print("Email Not Found!, We will register")

        # context
        hashd_pwd = encrypt_password.generate_password_hash(usr_athash).decode('utf-8')
        user1 = gen_user(name=usr_name, email=usr_email, password=hashd_pwd,
                        confirm_password=hashd_pwd, image="default.jpg",timestamp=datetime.now(),verified=True)

        try:
            db.session.add(user1)
            db.session.commit()

            #Login user
            usr_obj = User.query.filter_by(email=usr_email).first()
            #Check if user have a church id
            login_user(usr_obj)
            flash(f"Welcome! {usr_obj.name.title()}", "success")

            req_page = request.args.get('next')
            return redirect(req_page) if req_page else redirect(url_for('home'))

        
        except IntegrityError:
            db.session.rollback()  # Rollback the session on error
            return jsonify({"message": "Email already exists"}), 409
        
        except Exception as e:
                db.session.rollback()  # Rollback on any other error
                return jsonify({"message": "An error occurred", "error": str(e)}), 500
        
    else:
        user_login = User.query.filter_by(email=usr_email).first()

        if not user_login.verified:
            login_user(user_login)
            return redirect(url_for('verification'))

        login_user(user_login)
        flash(f"welcome! {user_login.name.title()}", "success")


        req_page = request.args.get('next')
        return redirect(req_page) if req_page else redirect(url_for('home'))
    

# User info API for frontend
@app.route("/get_user_info", methods=["GET"])
def get_user_info():
    # Check if user is logged in
    user = session.get("user")
    if not user:
        return jsonify({"error": "User not logged in"}), 401  # Unauthorized

    # Return user information to the frontend
    return jsonify(user)

    # return redirect(url_for("home"))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


