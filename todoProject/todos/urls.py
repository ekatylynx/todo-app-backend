# from todos.views import index
from django.urls import path, include
from .views import CreateUser, LoginUserView, TodoCreateViews, UserCategoriesListView, TodoFilterByCategoryView, \
    CategoryCreateView, TodoUpdateStatusView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [
    path('api/register/', CreateUser.as_view(), name='RegisterUser'), # Регистрация нового пользователя
    # path('signin/', LoginUserView.as_view(), name='LoginUser'),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('todos/', views.TodosListView.as_view(), name='GetTodos'),
    path('todos/create/', TodoCreateViews.as_view(), name='CreateTodo'),
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),  # Сброс пароля
    path('todos/categories/', UserCategoriesListView.as_view(), name='GetAllCategoriesUser'),
    path('todos/category/<int:category_id>/', TodoFilterByCategoryView.as_view(), name='FilterCategories'),
    path('todos/categories/create/', CategoryCreateView.as_view(), name='create-category'),
    path('todos/<int:pk>/update-status/', TodoUpdateStatusView.as_view(), name='todo_update_status'),
]