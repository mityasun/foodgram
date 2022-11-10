from djoser.serializers import UserCreateSerializer, UserSerializer

from users.models import User
from users.validators import ValidateUsername


class CustomUserSerializer(UserSerializer):
    """Сериализатор модели User"""

    class Meta(UserSerializer.Meta):
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name']


class CustomUserCreateSerializer(UserCreateSerializer, ValidateUsername):
    """Сериализатор регистрации юзеров"""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'password'
        ]
