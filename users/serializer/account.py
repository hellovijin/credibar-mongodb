from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_decode
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from oauth2_provider.models import Application, RefreshToken

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import secrets, base64, re, os

from credi.database import connections
from credi.validators import PasswordValidator, MobileValidator
from credi.utils import get_next_sequence

credibar_client = connections()

class TinyMCEUploadFileSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    
    def validate(self, attrs):
        ALLOWED_IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "bmp", "gif"]
        extension = os.path.splitext(attrs['file'].name)[1].replace(".", "")
        if extension.lower() not in ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError({"file": "image format not support"})
        return attrs

class SignUpBasicInformationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required= True, min_length= 3, max_length= 25, error_messages= {"required": "First name is required", "min_length": "First name must be at least 3 characters", "max_length": "First name may not be greater than 25 characters"})
    last_name = serializers.CharField(required= True, max_length= 25, error_messages= {"required": "Last name is required", "max_length": "Last name may not be greater than 25 characters"})
    email = serializers.EmailField(required= True, max_length= 50, error_messages= {"required": "Email is required", "max_length": "Email may not be greater than 50 characters"})
    mobile = serializers.CharField(required=True, validators=[MobileValidator()], error_messages= {"required": "Mobile number is required"})

    def validate(self, attrs):
        credibar_db = credibar_client.connect()
        user_rec = credibar_db.auth_user.find_one({"email": attrs['email']})
        if user_rec is not None:
            if user_rec["is_active"] == False:
                credibar_client.disconnect()
                raise ValidationError({"email": "Your account temporarily deactivated, Please contact support team"})
            
            user_profile_rec = credibar_db.credibar_profile.find_one({"user_id": user_rec["id"]})
            password_stat = user_profile_rec["password_stat"] if user_profile_rec and "password_stat" in user_profile_rec.keys() else ""
            if password_stat == "created":
                credibar_client.disconnect()
                raise ValidationError({"email": "User alredy exist with same email, Please try to login"})
        return attrs

    def save_profile(self, user_id):
        credibar_db = credibar_client.connect()
        user_profile_rec = credibar_db.credibar_profile.find_one({"user_id": user_id})
        if user_profile_rec is None:
            profile_rec = {"user_id": user_id, "email_stat": False, "mobile_stat": False, "status_key": "user_register", "created_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S")}
            profile_rec["id"] = get_next_sequence( "credibar_profile" )
            credibar_db.credibar_profile.insert_one( profile_rec )
        credibar_client.disconnect()
        return True
    
    def save(self):
        record = {i: self.validated_data[i] for i in self.validated_data.keys()}
        record['password'] = secrets.token_hex( 8 )
        record['is_active'] = True
        instance = User.objects.create_user(**record)
        self.save_profile( instance.id )
        return instance

class SignUpVerificationSerializer(serializers.Serializer):
    otp = serializers.CharField(required= True, max_length= 6, error_messages= {"required": "OTP is required"})

class SignInSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(required= True, min_length= 8, style={"input_type": "password"}, validators= [PasswordValidator()])
    hisense_secure = serializers.CharField(required= False, default= "")
    encryption = serializers.BooleanField(default= 0, required= False)
    token = serializers.CharField(required= True)
    primary = serializers.CharField(required= True)
    platform = serializers.CharField(required= True)
    manufacturer = serializers.CharField(required= True)
    model = serializers.CharField(required= True)

    def validate(self, attrs):
        request = self.context["request"]
        try:
            Application.objects.get(client_id= request.META['HTTP_CLIENT_ID'])
        except Exception as e:
            raise ValidationError({"account": "You don't have permission to access this portal"})
        
        email_decode = attrs['email']
        password_decode = attrs['password']
        
        if attrs['encryption']:
            hisense_secure = attrs['hisense_secure'] # request.session.get("hisense_secure", "")
            # if hisense_secure == "" or hisense_secure != attrs['hisense_secure']:
            #     raise ValidationError({"hisense_secure": "Encryption token Invalid"})
            try:
                cipher = AES.new( hisense_secure.encode('utf-8'), AES.MODE_ECB )
                email_encode = base64.b64decode( attrs['email'] )
                email_binary = unpad( cipher.decrypt( email_encode ), 16 )
                email_decode = email_binary.decode('utf-8')

                password_encode = base64.b64decode( attrs["password"] )
                password_binary = unpad( cipher.decrypt( password_encode ), 16 )
                password_decode = password_binary.decode('utf-8')
            except Exception as e:
                raise ValidationError({"hisense_secure": "Invalid Token"})
        try:
            instance = User.objects.get(email= email_decode, is_delete=False)
        except User.DoesNotExist:
            raise ValidationError({"email": "Given email does not exist"})
        except User.MultipleObjectsReturned:
            raise ValidationError({"email": "Given email with multiple account found enter valid password"})
        except Exception as e:
            raise ValidationError({"email": "Something went wrong, Please try again later"})

        try:
            user_authentication = authenticate(username= email_decode, password= password_decode )
            if instance.is_delete == True and user_authentication:
                raise ValidationError({"password": "Account not found"})
            if instance.is_active == False and user_authentication:
                raise ValidationError({"password": "Your account not active"})
            elif not user_authentication:
                raise ValidationError({"password": "Invalid password"})
        except Exception as e:
            raise ValidationError(e)
        self.instance = instance
        return attrs

    def login(self):
        request = self.context["request"]
        token = generate_oauth_token( request, self.instance, request.META['HTTP_CLIENT_ID'])
        return token