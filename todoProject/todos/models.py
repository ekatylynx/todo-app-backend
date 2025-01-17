from django.contrib.auth.models import AbstractUser
from django.db import models

# Наследуемся от AbstractUser для расширения стандартной модели User
class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=255)
    name = models.TextField(null=True, blank=True, verbose_name="Имя", max_length=100)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user'
    )

    # Указываем, что email будет использоваться в качестве уникального идентификатора
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    def __str__(self):
        return self.email

class Todo(models.Model):
    TOP_PRIORITY = "P1"
    MIDDLE_PRIORITY = "P2"
    NORMAL_PRIORITY = "P3"
    LOW_PRIORITY = "P4"
    PRIORITY_TASK_CHOICES = {
        TOP_PRIORITY: "Top priority",
        MIDDLE_PRIORITY: "Medium priority",
        NORMAL_PRIORITY: "Normal priority",
        LOW_PRIORITY: "Low priority",
    }

    title = models.CharField(max_length=200, verbose_name='Название задачи', null=False)
    description = models.TextField(blank=True, verbose_name='Описание задачи')
    priority = models.CharField(max_length=2, choices=PRIORITY_TASK_CHOICES, default=NORMAL_PRIORITY)
    from_deadline = models.DateTimeField(null=True, blank=True, verbose_name='Срок выполнения (от)')
    until_deadline = models.DateTimeField(null=True, blank=True, verbose_name='До срока выполнения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Время изменения')
    status = models.BooleanField(default=False, verbose_name='Статус задачи')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField('Category', verbose_name='Категория')
    # Связь один ко многим между User и Todo (у одного user много todo, у одного todo - один user)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

class Category(models.Model):
    title = models.CharField(max_length=150, db_index=True, verbose_name='Категория')
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']