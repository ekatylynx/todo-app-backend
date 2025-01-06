from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import Todo
import pytz

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Mega (object):
        model = User
        fields = ['id', 'username', 'password', 'email']
    # password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Создаём токен для пользователя
        token = super().get_token(user)
        # Добавляем дополнительные данные в токен (например, email)
        token['email'] = user.email
        return token

    def validate(self, attrs):
        # Проверяем, существует ли пользователь и введены ли правильные данные
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(username=username, password=password)  # Аутентификация пользователя
        if not user:
            # Если пользователь не найден или пароль неверен
            raise serializers.ValidationError({"detail": "No active account found with the given credentials"})

        # Если всё корректно, вызываем стандартный метод `validate`
        data = super().validate(attrs)
        return data

class TodosSerializer(serializers.ModelSerializer):
    created_at_moscow = serializers.SerializerMethodField()
    updated_at_moscow = serializers.SerializerMethodField()

    created_at_unix = serializers.SerializerMethodField()
    created_at_readable = serializers.SerializerMethodField()

    updated_at_unix = serializers.SerializerMethodField()
    updated_at_readable = serializers.SerializerMethodField()

    from_deadline_unix = serializers.SerializerMethodField()
    from_deadline_readable = serializers.SerializerMethodField()

    until_deadline_unix = serializers.SerializerMethodField()
    until_deadline_readable = serializers.SerializerMethodField()

    class Meta:
        model = Todo
        fields = '__all__'

    # Универсальный метод для преобразования времени
    def _convert_to_timezone(self, datetime_obj):
        if datetime_obj:
            moscow_tz = pytz.timezone('Europe/Moscow')
            return datetime_obj.astimezone(moscow_tz)
        return None

    # Универсальный метод для преобразования времени в Unix
    def _to_unix(self, datetime_obj):
        if datetime_obj:
            return int(datetime_obj.timestamp())
        return None

    # Универсальный метод для преобразования времени в читаемый формат
    def _to_readable(self, datetime_obj):
        if datetime_obj:
            return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
        return None

    def get_created_at_moscow(self, obj):
        return self._to_readable(self._convert_to_timezone(obj.created_at))

    def get_updated_at_moscow(self, obj):
        return self._to_readable(self._convert_to_timezone(obj.updated_at))

    def get_created_at_unix(self, obj):
        return self._to_unix(obj.created_at)

    def get_created_at_readable(self, obj):
        return self._to_readable(obj.created_at)

    def get_updated_at_unix(self, obj):
        return self._to_unix(obj.updated_at)

    def get_updated_at_readable(self, obj):
        return self._to_readable(obj.updated_at)

    def get_from_deadline_unix(self, obj):
        return self._to_unix(obj.from_deadline)

    def get_from_deadline_readable(self, obj):
        return self._to_readable(obj.from_deadline)

    def get_until_deadline_unix(self, obj):
        return self._to_unix(obj.until_deadline)

    def get_until_deadline_readable(self, obj):
        return self._to_readable(obj.until_deadline)
