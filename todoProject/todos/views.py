from http.client import responses

from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from django.http import HttpResponse
import logging
from django.conf import settings

from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
# Добавляем AllowAny

from .models import Todo
from .serializers import TodosSerializer, UserSerializer, CustomTokenObtainPairSerializer

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# РЕГИСТРАЦИЯ НОВОГО USER

@api_view(['POST'])
def signup_user(self, request):
    permission_classes = [AllowAny]
    # Используем сериализатор для валидации и обработки входящих данных
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():  # Проверяем, валидны ли данные
        serializer.save()  # Сохраняем нового пользователя в базе данных
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_201_CREATED)
        # Если данные валидны, возвращаем успешный ответ с сообщением и статусом 201
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # Если данные не валидны, возвращаем ошибки валидации с кодом 400

# АВТОРИЗАЦИЯ LOGIN USER SIGN IN

@api_view(['POST'])
def signin_user(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        ...
    else:
        # Return an 'invalid login' error message.
        ...


# ВЫХОД USER (LOGOUT)

class LogoutView(APIView):
    # Указываем, что доступ к этому представлению имеют только аутентифицированные пользователи
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            # Извлекаем refresh-токен из тела запроса
            refresh_token = request.data.get('refresh')
            # Создаем объект RefreshToken, чтобы работать с токеном
            token = RefreshToken(refresh_token)
            # Добавляем токен в черный список, делая его недействительным
            token.blacklist()
            return Response({'message': 'Successfully logged out!'}, status=status.HTTP_200_OK)
            # Возвращаем успешный ответ, если токен успешно добавлен в черный список
        except Exception as e:
            # Если возникает ошибка (например, токен уже недействителен), возвращаем сообщение об ошибке
            return Response({'error': 'Invalid token or already logged out!'}, status=status.HTTP_400_BAD_REQUEST)
            # Ответ с кодом 400 указывает, что токен некорректен или уже использован


def index(request):
    todos = Todo.objects.all()
    context = {
        'todos': todos,
        'title': 'Список дел'
    }

    return render(request, 'index.html', context=context)

class TodosListView(ListAPIView):
    # permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    queryset = Todo.objects.all()  # Добавляем атрибут queryset
    serializer_class = TodosSerializer  # Указываем сериализатор

@api_view(['POST'])
def create_todo(request):
    permission_classes = [IsAuthenticated]
    if request.method == 'POST':
        # Создаем сериализатор с данными из запроса
        serializer = TodosSerializer(data=request.data)

        # Проверяем, валидны ли данные
        if serializer.is_valid():
            # Сохраняем данные в базе
            serializer.save()
            # Возвращаем успешный ответ с созданным объектом
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Если данные невалидны, возвращаем ошибку
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
