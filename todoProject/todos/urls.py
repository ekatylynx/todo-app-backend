# from todos.views import index
from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from .views import signup_user, LogoutView
from todos.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
# from todos.views import TodosListView
from . import views

urlpatterns = [
    path('todos/', views.TodosListView.as_view(), name='todos-list'),
    path('todos/create/', views.create_todo, name='create_todo'),

    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path('signup/', views.signup_user), # Регистрация нового пользователя
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),  # Вход
    # path('refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Обновление access token
    path('logout/', LogoutView.as_view(), name='logout'),  # Выход
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),  # Сброс пароля
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

# path('', views.index),
# path('api/', include('Todos.urls')),
# path('todos/', include('todos.urls')),