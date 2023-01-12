import pytest


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_user(
        username='TestAdmin', email='testadmin@yamdb.fake', first_name='Admin',
        last_name='Adminovich', password='1234567Admin',
        is_superuser=True, is_staff=True, is_active=True
    )


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser', email='test@test.ru', first_name='Test',
        last_name='Testovich', password='1234567Test'
    )


@pytest.fixture
def token_user(user):
    from rest_framework.authtoken.models import Token
    token = Token.objects.create(user=user)

    return {
        'auth_token': str(token)
    }


@pytest.fixture
def user_client(token_user):
    from rest_framework.test import APIClient
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_user}')
    return client


@pytest.fixture
def another_user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUserAnother', email='test3@test.ru',
        first_name='TestAnother', last_name='TestAnother',
        password='1234567Test'
    )
