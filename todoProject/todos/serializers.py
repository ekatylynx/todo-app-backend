# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
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
            raise serializers.ValidationError("A user with this email already exists.")
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
            raise serializers.ValidationError("A user with this email does not exist.")

        user = User.objects.get(email=email)
        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect data.")

        data['user'] = user
        return data

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

# Сериализатор для создания задач
class TodoCreateSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        required=False
    )
    # из-за этой конструкции даже верные id категорий воспринимаются как неверные
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     user = self.context.get('request').user
    #     self.fields['categories'].queryset = Category.objects.filter(author=user)

    class Meta:
        model = Todo
        fields = ['id', 'title', 'description', 'priority', 'from_deadline', 'until_deadline', 'status', 'categories', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_categories(self, value):
        user = self.context['request'].user
        for category in value:
            if category.author != user:
                raise serializers.ValidationError(
                    f"Category '{category.title}' (id {category.id}) does not belong to you."
                )
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        categories = validated_data.pop('categories', [])
        if not categories:
            categories = [Category.objects.get(title='all', author=user)]
        todo = Todo.objects.create(author=user, **validated_data)
        todo.categories.set(categories)
        return todo

class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title']

    def validate_title(self, value):
        user = self.context['request'].user

        # Запрещаем создание категории с названием 'all'
        if value.lower() == 'all':
            raise serializers.ValidationError("Category title 'all' is reserved and cannot be used.")

        # Проверяем, что категория с таким названием уже не существует у пользователя
        if Category.objects.filter(title__iexact=value, author=user).exists():
            raise serializers.ValidationError("You already have a category with this title.")
        return value

    def create(self, validated_data):
        # Автоматически добавляем текущего пользователя в поле author
        user = self.context['request'].user
        validated_data['author'] = user
        return super().create(validated_data)

class TodoUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['status']

class UserProfileSerializer(serializers.ModelSerializer):
    date_joined_readable = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'name', 'avatar', 'date_joined', 'date_joined_readable']
        read_only_fields = ['email', 'date_joined']  # Эти поля не должны изменяться через этот эндпоинт

    def get_date_joined_readable(self, obj):
        if obj.date_joined:
            moscow_tz = pytz.timezone('Europe/Moscow')
            localized_date = obj.date_joined.astimezone(moscow_tz)
            return localized_date.strftime('%Y-%m-%d %H:%M:%S')
        return None

    def validate_avatar(self, value):
        if value:
            max_size = 2 * 1024 * 1024  # 2MB
            if value.size > max_size:
                raise serializers.ValidationError("Avatar file size should not exceed 2MB")
        return value

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
