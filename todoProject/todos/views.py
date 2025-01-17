from http.client import responses

from django.shortcuts import render
from django.http import JsonResponse
from django.core import serializers
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
from django.contrib.auth.models import User

from .models import Todo
from .serializers import TodosSerializer, UserSerializer, LoginSerializer

User = get_user_model()

# РЕГИСТРАЦИЯ НОВОГО USER

class CreateUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Пользователь успешно зарегистрирован."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# АВТОРИЗАЦИЯ LOGIN USER SIGN IN

class LoginUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def index(request):
    todos = Todo.objects.all()
    context = {
        'todos': todos,
        'title': 'Список дел'
    }

    # return render(request, 'index.html', context=context)

class TodosListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TodosSerializer  # Указываем сериализатор

    def get(self, request):
        user = request.user
        todos = Todo.objects.filter(author=user)
        serializer = TodosSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TodoCreateViews(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = TodosSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
