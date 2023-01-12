import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from tests.common import create_users_api


class Test01UserRegistration:
    url_signup = '/api/users/'
    url_token = '/api/auth/token/login/'
    valid_username = 'TestUser'
    valid_email = 'test@foodgram.fake'
    valid_first_name = 'First name'
    valid_last_name = 'Last name'
    valid_password = '1234567Test'

    @pytest.mark.django_db(transaction=True)
    def test_00_nodata_signup(self, client):
        response = client.post(self.url_signup)

        assert response.status_code != status.HTTP_404_NOT_FOUND, (
            f'Страница {self.url_signup} не найдена статус '
            f'{status.HTTP_404_NOT_FOUND}'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'проверьте, что POST запрос на {self.url_signup} без параметров '
            f'не создает пользователя и возвращается статус '
            f'{status.HTTP_400_BAD_REQUEST}'
        )

        response_json = response.json()
        empty_fields = [
            'email', 'username', 'first_name', 'last_name', 'password'
        ]
        for field in empty_fields:
            assert (field in response_json.keys()
                    and isinstance(response_json[field], list)), (
                f'Проверьте, что при POST запросе {self.url_signup} без '
                f'параметров в ответе есть сообщение о том, какие поля пустые'
            )

    @pytest.mark.django_db(transaction=True)
    def test_01_invalid_data_signup(self, client):

        invalid_data = {
            'email': 'invalid_email',
            'username': 'invalid_username@foodgram.fake'
        }
        response = client.post(self.url_signup, data=invalid_data)

        assert response.status_code != status.HTTP_404_NOT_FOUND, (
            f'Страница `{self.url_signup}` не найдена '
            f'{status.HTTP_404_NOT_FOUND}'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'Проверьте, что POST запрос на {self.url_signup} с невалидными '
            f'данными не создает пользователь и возвращается '
            f'статус {status.HTTP_400_BAD_REQUEST}'
        )

        response_json = response.json()
        invalid_fields = ['email']
        for field in invalid_fields:
            assert (field in response_json.keys()
                    and isinstance(response_json[field], list)), (
                f'Проверьте, что в POST запросе {self.url_signup} с '
                f'невалидными данными, в ответе есть сообщение о том, '
                f'какие поля заполнены неправильно'
            )

        valid_data = {
            'email': self.valid_email,
            'username': self.valid_username,
            'first_name': self.valid_first_name,
            'last_name': self.valid_last_name,
            'password': self.valid_password
        }
        response = client.post(self.url_signup, data=valid_data)
        response_json = response.json()
        for field in valid_data.keys():
            assert field in response_json.keys(), (
                f'Проверьте, что регистрация невозможна без поля {field}'
            )
            assert response.status_code == 201, (
                f'Проверьте, что POST запрос {self.url_signup} без поля '
                f'{field} возвращается статус {status.HTTP_400_BAD_REQUEST}'
            )

    @pytest.mark.django_db(transaction=True)
    def test_02_registration_same_fields_restricted(self, admin_client, client):

        user = create_users_api(admin_client)

        duplicate_email_data = {
            'email': self.valid_email,
            'username': 'valid_username_2',
            'first_name': self.valid_first_name,
            'last_name': self.valid_last_name,
            'password': self.valid_password
        }
        response = client.post(self.url_signup, data=duplicate_email_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'Проверьте, что POST запрос на {self.url_signup}'
            f'не создает пользователя, email которого уже зарегистрирован и '
            f'возвращается статус {status.HTTP_400_BAD_REQUEST}'
        )
        duplicate_username_data = {
            'email': 'test_duplicate@foodgram.fake',
            'username': self.valid_username,
            'first_name': self.valid_first_name,
            'last_name': self.valid_last_name,
            'password': self.valid_password
        }
        response = client.post(self.url_signup, data=duplicate_username_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'Проверьте, что POST запрос на {self.url_signup} '
            f'не создает пользователя, username которого уже зарегистрирован и '
            f'возвращается статус {status.HTTP_400_BAD_REQUEST}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_03_registration_me_username_restricted(self, client):

        valid_data = {
            'email': self.valid_email,
            'username': 'me',
            'first_name': self.valid_first_name,
            'last_name': self.valid_last_name,
            'password': self.valid_password
        }
        response = client.post(self.url_signup, data=valid_data)
        assert response.status_code != status.HTTP_404_NOT_FOUND, (
            f'Страница `{self.url_signup}` не найдена '
            f'{status.HTTP_404_NOT_FOUND}'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'Проверьте, что POST запрос на {self.url_signup}'
            f'не создает пользователя с username "me" и возвращается статус '
            f'{status.HTTP_400_BAD_REQUEST}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_04_valid_user_registration(self, client):

        valid_data = {
            'email': self.valid_email,
            'username': self.valid_username,
            'first_name': self.valid_first_name,
            'last_name': self.valid_last_name,
            'password': self.valid_password
        }
        response = client.post(self.url_signup, data=valid_data)
        user = get_user_model().objects.get(username=self.valid_username)
        data = response.json()
        assert response.status_code != status.HTTP_404_NOT_FOUND, (
            f'Страница `{self.url_signup}` не найдена '
            f'{status.HTTP_404_NOT_FOUND}'
        )
        assert response.status_code == status.HTTP_201_CREATED, (
            f'Проверьте, что при POST запросе на {self.url_signup} можно '
            f'создать пользователя с валидными данными и возвращается '
            f'статус {status.HTTP_201_CREATED}'
        )
        assert type(data) == dict, (
            f'Проверьте, что при POST запросе {self.url_signup} '
            f'возвращаете словарь с данными пользователя'
        )
        assert 'id' in data and data['id'] == user.id, (
            f'Проверьте, что при POST запросе {self.url_signup} '
            f'возвращаете id пользователя'
        )
        assert 'email' in data and data['email'] == user.email, (
            f'Проверьте, что при POST запросе {self.url_signup} '
            f'возвращаете email пользователя'
        )
        assert 'username' in data and data['username'] == user.username, (
            f'Проверьте, что при POST запросе {self.url_signup} '
            f'возвращаете username пользователя'
        )
        assert 'first_name' in data and data[
            'first_name'] == user.first_name, (
            f'Проверьте, что при POST запросе {self.url_signup} '
            f'возвращаете first_name пользователя'
        )
        assert 'last_name' in data and data[
            'last_name'] == user.last_name, (
            f'Проверьте, что при POST запросе {self.url_signup} '
            f'возвращаете last_name пользователя'
        )
        assert 'password' in data and data['password'] == user.password, (
            f'Проверьте, что при POST запросе {self.url_signup} '
            f'возвращаете password пользователя'
        )

    @pytest.mark.django_db(transaction=True)
    def test_05_token_invalid_data(self, admin_client, client):
        response = client.post(self.url_token)
        assert response.status_code != status.HTTP_404_NOT_FOUND, (
            f'Страница `{self.url_token}` не найдена '
            f'{status.HTTP_404_NOT_FOUND}'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'Проверьте, что POST запрос на {self.url_token}'
            f'без параметров возвращается статус {status.HTTP_400_BAD_REQUEST}'
        )

        invalid_data = {
            'password': self.valid_password
        }
        response = client.post(self.url_token, data=invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'Проверьте, что POST запрос на {self.url_signup}'
            f'без email возвращается статус {status.HTTP_400_BAD_REQUEST}'
        )

        invalid_data = {
            'email': 'unexisting_email@foodgram.fake',
            'password': self.valid_password
        }
        response = client.post(self.url_token, data=invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'Проверьте, что POST запрос  на {self.url_token}'
            f'с несуществующим email, возвращается статус '
            f'{status.HTTP_400_BAD_REQUEST}'
        )

        user = create_users_api(admin_client)
        valid_data = {
            'email': self.valid_email,
            'password': self.valid_password
        }
        response = client.post(self.url_token, data=valid_data)
        assert response.status_code == status.HTTP_200_OK, (
            f'Проверьте, что POST запрос на {self.url_token} с валидными '
            f'данными возвращает токен и статус {status.HTTP_200_OK}'
        )
