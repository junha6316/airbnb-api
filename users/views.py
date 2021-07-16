import jwt

from django.conf import settings
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes

from django.shortcuts import render
from django.contrib.auth import authenticate

from users.serializers import UserSerializer
from rooms.models import Room
from rooms.serializers import RoomSerializer
from .models import User

class UsersView(APIView):

    def post(self, request):
        serializer = UserSerializer(request.data)
        if serializer.is_valid():
            new_user = serializer.save()
            return Response(UserSerializer(new_user).data)
        else:
            return Response(serializer.error, status=HTTP_400_BAD_REQUEST)

class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response()
        else:
            return Response(serializer.error, status=HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
        return Response(UserSerializer(user).data)
    except User.DoesNotExist:
        return Response(status=HTTP_400_BAD_REQUEST)


class FavsView(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = RoomSerializer(user.favs.all(), many=True).data
        print(serializer)
        return Response(serializer)

    def put(self, request):
        #update favs
        user = request.user
        pk = request.data.get("pk", None)
        if pk is not None:
            try:
                room = Room.objects.get(pk=pk)
                favs = user.favs.all()
                if room not in favs:
                    user.favs.add(room)
                else: 
                    user.favs.remove(room)
                return Response()
            except Room.DoesNotExist:
                return Response(status=HTTP_404_NOT_FOUND)
        else:
            return Response(status=HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(status=HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password) #유저가 있는지 확인하는 메서드
    if user is not None:
        encoded_jwt = jwt.encode({"pk": user.pk}, settings.SECRET_KEY, algorithm="HS256")
        return Response(data={"token":encoded_jwt})
        #jwt에 민감한 데이터를 넣어서는 안된다. 식별자 수준의 데이터만을 넣어야 한다.
        #token을 변경하지 않은 것을 확인한다.
    else:
        return Response(status=HTTP_401_UNAUTHORIZED)

    

    