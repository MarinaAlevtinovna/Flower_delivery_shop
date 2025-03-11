from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.routers import DefaultRouter
from .views import register, UserViewSet, get_user_by_telegram_id, profile

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="users")

urlpatterns = [
    path("api/", include(router.urls)),
    path("register/", register, name="register"),
    path("login/", LoginView.as_view(template_name="users/login.html", redirect_authenticated_user=True), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("get_user/", get_user_by_telegram_id, name="get-user"),
    path("profile/", profile, name="profile")
]
urlpatterns += router.urls