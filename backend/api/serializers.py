from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Tags, Ingredients
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


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов"""

    class Meta:
        model = Ingredients
        fields = '__all__'
        lookup_field = ('name',)


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов"""

    class Meta:
        model = Tags
        fields = '__all__'
