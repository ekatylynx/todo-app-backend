from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import Todo, Category
import pytz

User = get_user_model()

# Create a new User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def create(self, validated_data):
        email = validated_data['email']
        username = email.split('@')[0]
        user = User.objects.create_user(email=email, username=username, password=validated_data['password'])
        # Создаем категорию с title='all' и привязываем её к пользователю
        Category.objects.create(title='all', author=user)
        return user

# Login a User

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Пользователь с таким email не существует.")

        user = User.objects.get(email=email)
        if not user.check_password(password):
            raise serializers.ValidationError("Неправильные данные.")

        data['user'] = user
        return data

class TodoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'priority', 'from_deadline', 'until_deadline', 'status']

    def create(self, validated_data):
        user = self.context['request'].user
        todo = Todo.objects.create(author=user, **validated_data)
        return todo

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
