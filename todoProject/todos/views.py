from http.client import responses

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.generics import ListAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema

from .models import Todo, Category
from .serializers import TodosSerializer, TodoCreateSerializer, UserSerializer, LoginSerializer, CategorySerializer, \
    CategoryCreateSerializer, TodoUpdateStatusSerializer
from django.utils import timezone

User = get_user_model()

# РЕГИСТРАЦИЯ НОВОГО USER

# @swagger_auto_schema(method='get', operation_description="Create a new user")
class CreateUser(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            201: "User successfully created",
            400: "Bad request, validation error"
        },
        operation_description="Create a new user with the provided data."
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration was successful."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# АВТОРИЗАЦИЯ LOGIN USER SIGN IN

class LoginUserView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={
            200: "Successful login, returns access and refresh tokens",
            400: "Bad request, validation error"
        },
        operation_description="Log in a user with the provided credentials."
    )
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

    @swagger_auto_schema(
        responses={
            200: "Successful data",
            400: "Bad request, validation error"
        },
        operation_description="Get all todo for user"
    )
    def get(self, request):
        user = request.user
        todos = Todo.objects.filter(author=user)
        # print(f'Object retrieved: {request.user}')
        serializer = TodosSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TodoCreateViews(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=TodoCreateSerializer,
        responses={
            201: "Todo successfully created",
            400: "Bad request, validation error"
        },
        operation_description="Create a new todo with the provided data."
    )
    def post(self, request):
        serializer = TodoCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserCategoriesListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CategorySerializer

    @swagger_auto_schema(
        responses={
            200: "Successful data",
            400: "Bad request, validation error"
        },
        operation_description="Get all categories todo for user"
    )
    def get_queryset(self):
        return Category.objects.filter(author=self.request.user)

# Фильтрация задач по категориям
class TodoFilterByCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: "Successful filter data",
            400: "Bad request, validation error",
            404: "Category not found or does not belong to you."
        },
        operation_description="Get all filter todo by categories for user"
    )
    def get(self, request, category_id):
        # Получаем текущего пользователя
        user = request.user

        # Проверяем, что категория принадлежит пользователю
        try:
            category = Category.objects.get(id=category_id, author=user)
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found or does not belong to you."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Фильтруем задачи по категории
        # Чтобы избежать проблемы N+1 - prefetch_related
        todos = Todo.objects.filter(categories=category, author=user).prefetch_related('categories')

        # Сериализуем данные
        serializer = TodosSerializer(todos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CategoryCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=CategoryCreateSerializer,
        responses={
            201: "Category successfully created",
            400: "Bad request, validation error"
        },
        operation_description="Create a new category with the provided data."
    )
    def post(self, request):
        serializer = CategoryCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TodoUpdateStatusView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TodoUpdateStatusSerializer
    queryset = Todo.objects.all()

    @swagger_auto_schema(
        request_body=TodoUpdateStatusSerializer,
        responses={
            201: "Todo status update successfully",
            400: "Bad request, validation error",
            403: "You do not have permission to update this todo."
        },
        operation_description="Todo status update."
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Проверка, является ли текущий пользователь автором задачи
        if instance.author != request.user:
            return Response({"detail": "You do not have permission to update this todo."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)