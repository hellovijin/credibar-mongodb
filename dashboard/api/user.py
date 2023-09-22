from django.utils import timezone
from django.urls import reverse_lazy
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from oauth2_provider.contrib.rest_framework import OAuth2Authentication

from credi.database import connections

from dashboard.serializer import user as acc_ser

credibar_client = connections()

class UserDesignationAPI(viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication, )

    def get_serializer_class(self):
        group_serializer = {
            'list': acc_ser.UserDesignationListSerializer,
            'create': acc_ser.UserDesignationCreateSerializer,
            'update': acc_ser.UserDesignationUpdateSerializer,
            'retrieve': acc_ser.UserDesignationRetrieveSerializer,
            'destroy': acc_ser.UserDesignationDestroySerializer,
        }
        if self.action in group_serializer.keys():
            return group_serializer[self.action]
    
    # def get_permissions(self):
    #     if self.action in ["create", "update", "retrieve", "destroy"]:
    #         return (IsAuthenticated(), )

    def list(self, request, *args, **kwargs):
        limit = request.GET.get('limit', 10)
        page = request.GET.get('page', 1)

        credibar_db = credibar_client.connect()
        condition = {"is_delete": False}
        records_all = credibar_db.credibar_user_designation.find(condition )
        records = records_all.limit( limit ).skip( (int(page) - 1) * int(limit) )
        response = Response({"result": "success", "records": list( records ), "total": records_all.count()}, status= status.HTTP_200_OK)
        credibar_client.disconnect()
        return response
    
    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data, context={"request": request})
        if ser.is_valid():
            ser.save()
            response = Response({"result": "success"}, status= status.HTTP_200_OK)
        else:
            errors = {i: ser.errors[i][0] for i in ser.errors.keys()}
            response = Response({"result": "failure", "errors": errors}, status= status.HTTP_200_OK)
        return response

    def update(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data, context={"request": request})
        if ser.is_valid():
            #ser.save()
            response = Response({"result": "success"}, status= status.HTTP_200_OK)
        else:
            errors = {i: ser.errors[i][0] for i in ser.errors.keys()}
            response = Response({"result": "failure", "errors": errors}, status= status.HTTP_200_OK)
        return response
    
    def retrieve(self, request, *args, **kwargs):
        credibar_db = credibar_client.connect()
        instance_id = kwargs['pk']
        record = credibar_db.credibar_user_designation.find_one({ "id": instance_id })
        record = self.get_serializer(record, context= {"request": request}).data
        response = Response({"result": "success", "record": record}, status= status.HTTP_200_OK)
        credibar_client.disconnect()
        return response
    
    def destroy(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data, context={"request": request})
        if ser.is_valid():
            ser.save()
            response = Response({"result": "success"}, status= status.HTTP_200_OK)
        else:
            errors = {i: ser.errors[i][0] for i in ser.errors.keys()}
            response = Response({"result": "failure", "errors": errors}, status= status.HTTP_200_OK)
        return response