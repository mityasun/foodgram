from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


def create_users_api(admin_client):
    valid_data = {
        'email': 'test@foodgram.fake',
        'username': 'TestUser',
        'first_name': 'First name',
        'last_name': 'Last name',
        'password': '1234567Test'
    }
    admin_client.post('/api/users/', data=valid_data)
    user = get_user_model().objects.get(email=valid_data['email'])
    return user


def auth_client(user):
    from rest_framework.authtoken.models import Token
    token = Token.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    return client
