from functools import partial
from django.db.models.base import Model
from django.shortcuts import render

from rest_framework import serializers, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND


from rooms.models import Room
from .serializers import RoomSerializer
from .permissions import IsOwner

class RoomViewSet(ModelViewSet):
    
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_permissions(self):
        if self.action == "list" or self.action == "retrieve":
            permissions_classes = [permissions.AllowAny]
        elif self.action == "create":
            permissions_classes = [permissions.IsAuthenticated]
        else:
            permissions_classes = [IsOwner]
        return [permission() for permission in permissions_classes]

    #name of the method => url
    @action(detail=False)
    def search(self, request):

        max_price = request.GET.get('max_price', None)
        min_price = request.GET.get('min_price', None)
        beds = request.GET.get('beds', None)
        bedrooms = request.GET.get('bedrooms', None)
        bathrooms = request.GET.get("bathrooms", None)
        lat = request.GET.get("lat", None)
        lng = request.GET.get("lng", None)

        filter_kwargs = {}
        if max_price is not None:
            filter_kwargs["price__lte"] = max_price
        
        if min_price is not None:
            filter_kwargs["price__gte"] = min_price

        if beds is not None:
            filter_kwargs["beds"] = beds

        if bedrooms is not None:
            filter_kwargs["bedrooms"] = bedrooms

        if bathrooms is not None:
            filter_kwargs["bathrooms"] = bathrooms
        
        if lat is not None and lng is not None:
            filter_kwargs["lat__gte"] = float(lat) - 0.005     
            filter_kwargs["lat__lte"] = float(lat) + 0.005 
            filter_kwargs["lng__gte"] = float(lng) - 0.005 
            filter_kwargs["lng__lte"] = float(lng) + 0.005 

        paginator = self.paginator
        paginator.page_size = 10
        try:
            rooms = Room.objects.filter(**filter_kwargs) #unpacking
        except ValueError:
            rooms = Room.objects.all()
        results = paginator.paginate_queryset(rooms, request)
        serializer = RoomSerializer(results, many=True)
        return paginator.get_paginated_response(serializer.data)

    








