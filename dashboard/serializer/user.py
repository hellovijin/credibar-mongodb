from django.core.exceptions import ValidationError
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework import serializers

from credi.database import connections
from credi.utils import get_next_sequence
from credi.validators import UniqueFiledValidator

credibar_client = connections()

class UserDesignationListSerializer(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.IntegerField()

class UserDesignationCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required= True, min_length= 3, max_length= 50, error_messages= {"required": "Name is required", "max_length": "Name should not be more than 50 characters", "min_length": "Name should not be less than 3 characters"})
    is_active = serializers.BooleanField(required= True, error_messages= {"required": "Status is required"})

    def validate(self, attrs):
        credibar_db = credibar_client.connect()
        user_designation_rec = credibar_db.credibar_user_designation.find_one({"name": attrs['name'], "is_delete": False})
        if user_designation_rec is not None:
            credibar_client.disconnect()
            raise ValidationError({"name": "User designation already exist with same name"})
        return attrs

    def save(self):
        credibar_db = credibar_client.connect()
        user_designation_rec = {"name": self.validated_data['name'], "is_active": self.validated_data['is_active'], "created_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S"), "updated_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S"), "is_delete": False}
        user_designation_rec["id"] = get_next_sequence( "credibar_user_designation" )
        credibar_db.credibar_user_designation.insert_one( user_designation_rec )
        credibar_client.disconnect()
        return user_designation_rec["id"]

class UserDesignationUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required= True, min_length= 3, max_length= 50, error_messages= {"required": "Name is required", "max_length": "Name should not be more than 50 characters", "min_length": "Name should not be less than 3 characters"})
    is_active = serializers.BooleanField(required= True, error_messages= {"required": "Status is required"})

    def validate(self, attrs):
        credibar_db = credibar_client.connect()
        instance_id = self.context['request'].parser_context['kwargs']['pk']
        user_designation_rec = credibar_db.credibar_user_designation.find_one({ "id": instance_id })
        if user_designation_rec is None:
            credibar_client.disconnect()
            raise ValidationError({"name": "User designation not found"})
        
        user_designation_rec = credibar_db.credibar_user_designation.find({ "id": {"$ne": instance_id }, "name": attrs['name'], "is_delete": False}).count()
        if user_designation_rec:
            credibar_client.disconnect()
            raise ValidationError({"name": "User designation already exist with same name"})
        return attrs
    
    def save(self, **kwargs):
        credibar_db = credibar_client.connect()
        instance_id = self.context['request'].parser_context['kwargs']['pk']
        credibar_db.credibar_user_designation.update({"id": instance_id}, {"$set": {"name": self.validated_data['name'], "is_active": self.validated_data['is_active'], "updated_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S")}})
        credibar_client.disconnect()
        return instance_id

class UserDesignationRetrieveSerializer(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.IntegerField()
    is_active = serializers.BooleanField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        return naturaltime( obj['created_at'] )

    def get_updated_at(self, obj):
        return naturaltime( obj['updated_at'] )

class UserDesignationDestroySerializer(serializers.Serializer):
    def validate(self, attrs):
        credibar_db = credibar_client.connect()
        instance_id = self.context['request'].parser_context['kwargs']['pk']
        user_designation_rec = credibar_db.credibar_user_designation.find_one({ "id": instance_id })
        if user_designation_rec is None:
            credibar_client.disconnect()
            raise ValidationError({"name": "User designation not found"})
        return attrs

    def save(self, **kwargs):
        credibar_db = credibar_client.connect()
        instance_id = self.context['request'].parser_context['kwargs']['pk']
        user_designation_rec = {"is_delete": False, "updated_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S")}
        #user_designation_rec["deleted_by"] = self.context['request'].user.id
        credibar_db.credibar_user_designation.update({"id": instance_id}, {"$set": user_designation_rec })
        credibar_client.disconnect()
        return instance_id