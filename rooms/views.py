from functools import partial
from django.shortcuts import render

from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, parser_classes
from rest_framework import serializers

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from rooms.models import Room
from .serializers import RoomSerializer

class RoomsView(APIView):

    def get(self, request):
        
        paginator = PageNumberPagination()
        paginator.page_size = 20
        rooms = Room.objects.all()
        results = paginator.paginate_queryset(rooms, request)
        serialized_rooms = RoomSerializer(results, many=True, context={'request': request}).data
        return paginator.get_paginated_response(serialized_rooms.data)
        return Response(serialized_rooms)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(status=HTTP_401_UNAUTHORIZED)
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save(user=request.user) # save 메서드가 데이터를 업데이트 하는지 생성하는지 판단한다. 
            room_serializer = RoomSerializer(room).data
            return Response(data=room_serializer, status=HTTP_200_OK)
        else:
            
            return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)

class RoomView(APIView):

    def get_room(self, pk):
        try:
            room = Room.objects.get(id=pk)
            return room
        except:
            return None

    def get(self, request, pk):
        room = self.get_room(pk)
        if room:
            serializer = RoomSerializer(room).data
            return Response(serializer)
        else:
            return Response(status=HTTP_404_NOT_FOUND)

    def put(self, request):
        room = self.get_room(pk)
        if room:
            if room.user != request.user:
                return Response(status=HTTP_403_FORBIDDEN)
            # serializer = CreateRoomSerializer(data=request.data) : create
            # serializer = CreateRoomSerializer(room, data=request.data) : update
            serializer = RoomSerializer(room, data=request.data, partial=True) #partial : 데이터의 일부만 보내겠다.
            if serializer.is_valid():
                room=serializer.save()
                return Response(data=RoomSerializer(room).data)
            else:
                return Response(data=serializer.errors, status=HTTP_400_BAD_REQUEST)
            
        else: 
            return Response(status=HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        room = self.get_room(pk)
        if room.user != request.user:
            return Response(status=HTTP_403_FORBIDDEN)
        if room is not None:
            room.delete()
            return Response(status=HTTP_200_OK)
        else:
            return Response(status=HTTP_404_NOT_FOUND)

@api_view(["GET"])
def room_search(request):

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

    paginator = PageNumberPagination()
    paginator.page_size = 10
    try:
        rooms = Room.objects.filter(**filter_kwargs) #unpacking
    except ValueError:
        rooms = Room.objects.all()
    results = paginator.paginate_queryset(rooms, request)
    serializer = RoomSerializer(results, many=True)
    return paginator.get_paginated_response(serializer.data)

    








