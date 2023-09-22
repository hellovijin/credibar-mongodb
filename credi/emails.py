from django.conf import settings
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils import timezone

from credi.database import connections

# databae connection global variable
credibar_client = connections()

def credibar_send_email(email_to, email_subject= "#hello", message="#m", attachments=[], **extras_):
    if settings.APP_PRODUCTION == False:
        email_to=['vijin@element8.ae']
    # else:
    #     email_to=['itadmin.dubai@hisense.com']
    if email_to:
        try:
            email = EmailMessage(
                subject=email_subject,
                body=message,
                from_email = settings.EMAIL_FROM,
                to=email_to
            )
            if settings.APP_PRODUCTION == True:
                if "cc" in extras_.keys():
                    email.cc = extras_["cc"]
                if "bcc" in extras_.keys():
                    email.cc = extras_["bcc"]
            for att in attachments:
                email.attach(att['name'], att['file'] )
            email.content_subtype = "html"
            email_stat = email.send()
        except Exception as e:
            email_stat = str( e )
        try:
            credibar_db = credibar_client.connect()
            email_status = "success" if email_stat == 1 else "failure"
            email_stat_rec = { "action": "email", "action_id": "", "status": email_status, "message": email_stat, "subject": email_subject, "email": email_to, "created_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S") }
            if "key_name" in extras_.keys():
                email_stat_rec["key_name"] = extras_["key_name"]
            if "user_id" in extras_.keys():
                email_stat_rec["user_id"] = extras_["user_id"]

            credibar_db.credibar_useractivity.insert_one( email_stat_rec )
            credibar_client.disconnect()
        except Exception as e:
            pass

def application_email_verification(request, instance, otp_):
    key_name = "application_email_verification"
    email_subject = "Welcome to Credibar - Your One-Time Password (OTP)"
    credibar_db = credibar_client.connect()
    email_template = credibar_db.credibar_email_template.find_one({"key_name": key_name})
    if email_template.get('is_active', False) == False:
        credibar_client.disconnect()
        return False
    
    email_template = email_template['content']
    absolute_static_uri = request.build_absolute_uri( settings.STATIC_URL )
    template_rec = {"name": instance.first_name, "absolute_static_uri": absolute_static_uri, "otp": otp_}
    message_template = email_template.format( **template_rec )
    extras_ = {"key_name": key_name, "user": instance}
    credibar_send_email(email_to= [instance.email], email_subject= email_subject, message= message_template, **extras_)
    return True