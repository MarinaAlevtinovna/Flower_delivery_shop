from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from users.models import CustomUser
from users.serializers import CustomUserSerializer
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()
    return render(request, "users/register.html", {"form": form})


class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
def get_user_by_telegram_id(request):
    telegram_id = request.GET.get('telegram_id')
    if not telegram_id:
        return Response({"error": "Telegram ID is required"}, status=400)

    user = CustomUser.objects.filter(telegram_id=telegram_id).first()
    if user:
        return Response(CustomUserSerializer(user).data)
    return Response({"error": "User not found"}, status=404)
