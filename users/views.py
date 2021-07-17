import jwt

from django.conf import settings
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, action

from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.viewsets import ModelViewSet

from users.serializers import UserSerializer
from rooms.models import Room
from rooms.serializers import RoomSerializer

from .models import User
from .permissions import IsSelf

class UsersViewSet(ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [IsAdminUser]
        elif self.action == "create" or self.action == "retrieve":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsSelf]
        
        return [permission() for permission in permission_classes]

    @action(detail=False , methods=["POST"])
    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(status=HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password) #유저가 있는지 확인하는 메서드
        if user is not None:
            encoded_jwt = jwt.encode({"pk": user.pk}, settings.SECRET_KEY, algorithm="HS256")
            return Response(data={"token":encoded_jwt, "pk": user.pk})
            #jwt에 민감한 데이터를 넣어서는 안된다. 식별자 수준의 데이터만을 넣어야 한다.
            #token을 변경하지 않은 것을 확인한다.
        else:
            return Response(status=HTTP_401_UNAUTHORIZED)

    @action(detail=True, methods=["GET"])
    def favs(self, request, pk):
        user = self.get_object()
        serializer = RoomSerializer(user.favs.all(), many=True).data

    @favs.mapping.put
    def toggle_favs(self, request, pk):
        if pk is not None:
            user = request.user
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

@api_view(["GET"])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
        return Response(UserSerializer(user).data)
    except User.DoesNotExist:
        return Response(status=HTTP_400_BAD_REQUEST)


    