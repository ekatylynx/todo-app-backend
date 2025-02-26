from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import Todo, Category, User

class TodosAdmin(admin.ModelAdmin):
    list_display = ('author', 'id', 'get_categories', 'get_category_count', 'status', 'title','description', 'priority', 'from_deadline', 'until_deadline', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'status', 'created_at')
    list_filter = ('status', 'id', 'categories')
    list_editable = ['status']

    # Метод для отображения категорий
    def get_categories(self, obj):
        return ", ".join([str(category.id) for category in obj.categories.all()])
        # return ", ".join([category.title for category in obj.categories.all()]) ДЛЯ ОТОБРАЖЕНИЯ НАЗВАНИЙ КАТЕГОРИЙ
    get_categories.short_description = 'Категории (ID)'

    # Метод для отображения количества категорий
    def get_category_count(self, obj):
        return obj.categories.count()
    get_category_count.short_description = 'Количество категорий'

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author')
    list_display_links = ('id', 'title')

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'name', 'avatar', 'is_active', 'is_superuser', 'date_joined')
    list_filter = ('is_active', 'is_superuser')

admin.site.register(Todo, TodosAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User, UserAdmin)