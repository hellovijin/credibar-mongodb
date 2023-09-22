import os, sys, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "credibar.settings")

from django.conf import settings
sys.path.append( settings.BASE_DIR )
django.setup()

from pymongo.mongo_client import MongoClient
from pymongo import ReturnDocument
import uuid
from bson.objectid import ObjectId

from django.utils import timezone

uri = "mongodb+srv://vijin:c1iRTfUEf4QWkL2B@cluster.lwh6afe.mongodb.net/?retryWrites=true&w=majority&appName=AtlasApp"
mongodb_username = "vijin"
mongodb_password = "zfv4nVZFc1AHdzYq"
connection_uri = "mongodb+srv://{}:{}@credibar.nixkgbb.mongodb.net/".format( mongodb_username, mongodb_password)

# Create a new client and connect to the server
client = MongoClient( connection_uri )

# Send a ping to confirm a successful connection
#try:
credibar_db = client['credibar']

user_rec = credibar_db['auth_user'].find_one({"username": "vijin"})

print( user_rec )
current_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

html_content = """{% load static %}
<div id="wrapper" dir="ltr" style="margin: 0; -webkit-text-size-adjust: none !important; padding: 70px 0 70px 0; width: 100%; background-color: #ececec; height: 100vh;">
    <table id="template_container" style="box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important; padding: 20px 40px; border: 0; background-color: #c5cadf; margin: 0 auto; border-radius: 0 !important;" width="600" cellspacing="0" cellpadding="0">
        <tbody>
            <tr valign="top">
                <td style="padding: 0;" align="center">
                    <p style="margin: 0; padding: 0 0 15px 0;"><img src="{% static 'credibar/images/logo.webp' %}" width="146px" /></p>
                </td>
            </tr>
            <tr>
                <td>
                    <table style="border: 0; background-color: #fff; padding: 40px 35px 30px 35px;" width="100%" cellspacing="0" cellpadding="0">
                        <tbody>
                            <tr>
                                <td>
                                    <p style="margin: 0; padding: 0;">&nbsp;</p>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 0;" valign="top">
                                    <!-- Body -->
                                    <p style="font-weight: bold; font-family: Rubik, Helvetica Neue, Helvetica, Roboto, Arial, sans-serif; line-height: 22px; font-size: 18px; margin-bottom: 10px;"></p>
                                    <h1 style="margin: 0px; padding: 0px; color: #00a7e1; font-size: 22px; font-family: 'Open Sans', sans-serif; font-weight: 400; margin-bottom: 20px;">Dear {{name}}</h1>
                                    <p style="margin: 0px; padding: 0px; color: #242a38; font-family: Rubik, Helvetica Neue, Helvetica, Roboto, Arial, sans-serif; line-height: 20px; font-size: 13px; font-weight: 400;">Welcome to Credibar! We are delighted to have you as a member of our growing community. To ensure the security of your account and complete the sign-in process, we require you to verify your email address using a one-time password (OTP). This additional layer of security helps protect your account from unauthorized access.</p>
                                    <p style="color: #242a38; font-family: Rubik, Helvetica Neue, Helvetica, Roboto, Arial, sans-serif; line-height: 20px; font-size: 13px; margin-top: 10px;">Here is your one-time password (OTP): <strong>[{{otp}}]<strong></p>
                                    <hr style="border-color: #dddddd1f; margin: 35px 0">
                                    <p style="font-family: Rubik, Helvetica Neue, Helvetica, Roboto, Arial, sans-serif; line-height: 15px; font-size: 10px; color: #ada8a8;">This email and any attachments are confidential and may also be privileged. If you are not the intended recipient, please delete all copies and notify the sender immediately</p>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
            <tr>
                <td>
                    <p style="color: #ffffff; text-align: center; font-family: Rubik, Helvetica Neue, Helvetica, Roboto, Arial, sans-serif; line-height: 15px; font-size: 10px; margin: 0; padding-top: 20px;">Copyrights {% now 'Y' %}. All rights reserved <a style="color: #ffffff;" href="#">Unsubscribe</a> emails from Credibar</p>
                </td>
            </tr>
        </tbody>
    </table>
</div>
"""

email_rec = {"key_name": "email_verification_application", "name": "Signup - OTP", "subject": "Welcome to Credibar - Your One-Time Password (OTP)", "content": html_content, "is_active": True, "created_at": current_time, "updated_at": current_time}