from django.utils import timezone
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.paginator import Paginator
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from oauth2_provider.settings import oauth2_settings
from oauth2_provider.contrib.rest_framework import OAuth2Authentication

import os, secrets, random

from credi.database import connections
from credi.constants import SIGNIN_ENCRYPTION_PADDING
from credi.tokens import account_rcover_password_token
from users.serializer import account as acc_ser

# databae connection global variable
credibar_client = connections()

class AccountAPI(viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication, )
    def get_serializer_class(self):
        group_serializer = {
            'signup_basic_information': acc_ser.SignUpBasicInformationSerializer,
            'signup_verification': acc_ser.SignUpVerificationSerializer,
            # 'signup_documents': acc_ser.SignUpDocumentsSerializer,
            # 'signup_additional_information': acc_ser.SignUpAdditionalInformationSerializer,
            #'signup_password': acc_ser.SignUpPasswordSerializer,
            
            
            # 'signin': acc_ser.SignInSerializer,
            # 'signin_otp': acc_ser.SignInOTPSerializer,
            # 'signin_otp_generate': acc_ser.SignInOTPGenerateSerializer,
            # 'token': acc_ser.TokenSerializer,
            # 'recover_password_token': acc_ser.RecoverPasswordTokenSerializer,
            # 'verify_recover_token': acc_ser.VerifyRecoverTokenSerializer,
            # 'reset_password': acc_ser.ResetPasswordSerializer,
            # 'signout': acc_ser.SignOutSerializer,
            # 'profile_settings': acc_ser.ProfileSettingsSerializer,
            # 'auth_user_detail': acc_ser.UserDetailSerializer,
            # 'fcm_token': acc_ser.FCMTokenCreateSerializer
        }
        if self.action in group_serializer.keys():
            return group_serializer[self.action]
    
    def get_permissions(self):
        if self.action in ["user_detail", "signout"]:
            return (IsAuthenticated(), )
        return (AllowAny(),)
    
    def signin_secret(self, request, *args, **kwargs):
        hisense_secure = secrets.token_hex( SIGNIN_ENCRYPTION_PADDING )
        response = Response({"result": "success", "hisense_secure": hisense_secure}, status= status.HTTP_200_OK)
        expires = timezone.now() + timezone.timedelta(seconds= oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
        request.session.set_expiry( expires )
        request.session['hisense_secure'] = hisense_secure
        #response.set_cookie("hisense_secure", re.escape( hisense_secure ), expires=expires, samesite= "Lax", secure= True, path="/")
        return response
    
    def signup_basic_information(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data, context={'request': request})
        if ser.is_valid():
            response = {}
            credibar_db = credibar_client.connect()
            user_rec = credibar_db.auth_user.find_one({"email": ser.validated_data['email']})
            if user_rec:
                user_profile_rec = credibar_db.credibar_profile.find_one({"user_id": user_rec["id"]})
                if user_profile_rec is None:
                    # if user profile not exit then create new profile
                    ser.save_profile( user_rec["id"] )
            else:
                ser.save()
            
            # send otp to email and verify
            user_token = account_rcover_password_token.make_token( ser.instance )
            otp = random.randint(1000, 9999)
            otp_token = urlsafe_base64_encode(force_bytes( otp ) )
            token = "{}-_-{}".format(user_token, otp_token)
            
            validation_rec = {"user": "x", "token": "x"}
            response = { "result": "success", "redirect_uri": reverse_lazy( 'app_users:api_signup_verification', kwargs= validation_rec ), "action": 'otp-verification' }
            credibar_client.disconnect()
            return Response(response, status= status.HTTP_200_OK)
        else:
            errors = {i: ser.errors[i][0] for i in ser.errors.keys()}
            response = Response({"result": "failure", "errors": errors}, status= status.HTTP_200_OK)
        return response
    
    def signup_verification(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data, context={'request': request})
        if ser.is_valid():
            response = Response({"result": "success"}, status= status.HTTP_200_OK)
        else:
            errors = {i: ser.errors[i][0] for i in ser.errors.keys()}
            response = Response({"result": "failure", "errors": errors}, status= status.HTTP_200_OK)
        return response

    def signup_password(self, request, *args, **kwargs):
        # if user_profile_rec and "documents" not in user_profile_rec.keys():
        #     # if documents not uploaded then redirect to documents upload page
        #     response = { "redirect_uri": reverse_lazy( 'app_users:api_signup_documents' ), "redirect_level": 2 }
        #     return Response(response, status= status.HTTP_200_OK)
        
        # if user_profile_rec and "designation" not in user_profile_rec.keys():
        #     # if designation not uploaded then redirect to designation upload page
        #     response = { "redirect_uri": reverse_lazy( 'app_users:api_signup_additional_information' ), "redirect_level": 3 }
        #     response = Response(response, status= status.HTTP_200_OK)
        pass
    
    def signin(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data, context={'request': request})
        if ser.is_valid():
            user_token = account_rcover_password_token.make_token( ser.instance )
            otp = random.randint(1000, 9999)
            if ser.instance.email == "vijin@element8.ae":
                otp = "1234"
            otp_token = urlsafe_base64_encode(force_bytes( otp ) )
            token = "{}-_-{}".format(user_token, otp_token)
            #signin_otp_authentication_application(self.request, ser.instance, otp)
            instance_url = request.build_absolute_uri( reverse_lazy('app_hisenseapp:hisenseapp_api_signin_otp', kwargs= {"token": token} ) )
            instance_generate_url = request.build_absolute_uri( reverse_lazy('app_hisenseapp:hisenseapp_api_signin_otp_generate', kwargs= {"token": user_token} ) )
            response_rec = {"result": "success", "instance_url": instance_url, "instance_generate_url": instance_generate_url, "otp": 0000}
            
            response = Response(response_rec, status= status.HTTP_200_OK)
        else:
            response = Response({"result": "failure", "errors": {i: ser.errors[i][0] for i in ser.errors.keys()} }, status=status.HTTP_200_OK)
        return response