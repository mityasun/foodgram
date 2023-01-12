import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from .common import auth_client, create_users_api


class Test01UserAPI:

    url_users = '/api/users/'
    url_me = '/api/users/me/'
    url_password = '/api/users/set_password/'
    url_token = '/api/auth/token/login/'
    url_logout = '/api/auth/token/logout/'
    valid_username = 'valid_username'
    valid_email = 'test@foodgram.fake'
    valid_first_name = 'First name'
    valid_last_name = 'Last name'
    valid_password = '1234567Test'

    @pytest.mark.django_db(transaction=True)
    def test_00_users_not_authenticated(self, admin_client, client):
        response = client.get(self.url_users)
        assert response.status_code != status.HTTP_404_NOT_FOUND, (
            f'Страница {self.url_users} не найдена, проверьте этот адрес '
            f'есть в urls.py'
        )
        assert response.status_code == status.HTTP_200_OK, (
            f'Проверьте, что при GET запросе на {self.url_users} '
            f'без токена авторизации возвращается статус {status.HTTP_200_OK}'
        )

        user = create_users_api(admin_client)
        response = client.get(f'/api/users/{user.id}/')
        assert response.status_code != status.HTTP_404_NOT_FOUND, (
            f'Страница /api/users/{user.id}/ не найдена, проверьте этот адрес '
            f'в urls.py'
        )
        assert response.status_code == status.HTTP_200_OK, (
            f'Проверьте, что при GET запросе /api/users/{user.id}/ без токена '
            f'авторизации возвращается статус {status.HTTP_200_OK}'
        )

        response = client.get(f'{self.url_me}')
        assert response.status_code != status.HTTP_404_NOT_FOUND, (
            f'Страница {self.url_me} не найдена, проверьте этот адрес '
            f'в urls.py'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, (
            f'Проверьте, что при GET запросе {self.url_me} без токена '
            f'авторизации возвращается статус {status.HTTP_401_UNAUTHORIZED}'
        )

        response = client.post(self.url_password)
        assert response.status_code != status.HTTP_404_NOT_FOUND, (
            f'Страница {self.url_password} не найдена, проверьте этот адрес '
            f'в urls.py'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, (
            f'Проверьте, что при POST запросе {self.url_password} '
            f'без токена авторизации возвращается статус '
            f'{status.HTTP_401_UNAUTHORIZED}'
        )

        response = client.post(self.url_token)
        assert response.status_code != status.HTTP_404_NOT_FOUND, (
            f'Страница {self.url_token} не найдена, проверьте этот адрес '
            f'в urls.py'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'Проверьте, что при POST запросе {self.url_token} '
            f'без email и пароля возвращается статус '
            f'{status.HTTP_400_BAD_REQUEST}'
        )

        response = client.post(self.url_logout)
        assert response.status_code != status.HTTP_404_NOT_FOUND, (
            f'Страница {self.url_logout} не найдена, проверьте этот адрес '
            f'в urls.py'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, (
            f'Проверьте, что при POST запросе {self.url_logout} '
            f'без токена авторизации возвращается статус '
            f'{status.HTTP_401_UNAUTHORIZED}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_01_get_users_list(self, admin, admin_client, client):
        user = create_users_api(admin_client)
        users = get_user_model().objects.all()
        client_user = auth_client(user)
        clients = (
            admin_client, client_user, client
        )
        for client in clients:
            response = client.get(self.url_users)
            assert response.status_code != status.HTTP_404_NOT_FOUND, (
                f'Страница {self.url_users} не найдена, проверьте этот адрес '
                f'в urls.py'
            )
            assert response.status_code == status.HTTP_200_OK, (
                f'Проверьте, что при GET запросе {self.url_users} с токеном '
                f'авторизации возвращается статус {status.HTTP_200_OK}'
            )
            data = response.json()
            assert 'count' in data, (
                f'Проверьте, что при GET запросе {self.url_users} возвращаете '
                f'данные с пагинацией. Не найден параметр count'
            )
            assert 'next' in data, (
                f'Проверьте, что при GET запросе {self.url_users} возвращаете '
                f'данные с пагинацией. Не найден параметр next'
            )
            assert 'previous' in data, (
                f'Проверьте, что при GET запросе {self.url_users} возвращаете '
                f'данные с пагинацией. Не найден параметр previous'
            )
            assert 'results' in data, (
                f'Проверьте, что при GET запросе {self.url_users} возвращаете '
                f'данные с пагинацией. Не найден параметр results'
            )
            assert data['count'] == users.count(), (
                f'Проверьте, что при GET запросе {self.url_users} возвращаете '
                f'данные с пагинацией. Значение параметра count не правильное'
            )
            assert type(data['results']) == list, (
                f'Проверьте, что при GET запросе {self.url_users} возвращаете '
                f'данные с пагинацией. Тип параметра results должен быть список'
            )
            assert len(data['results']) == users.count(), (
                f'Проверьте, что при GET запросе {self.url_users} возвращаете '
                f'данные с пагинацией. Значение параметра results не правильное'
            )
            assert data['results'][0].get('id') == admin.id, (
                f'Проверьте, что при GET запросе {self.url_users} возвращаете '
                f'id пользователей'
            )
            assert data['results'][0].get('email') == admin.email, (
                f'Проверьте, что при GET запросе {self.url_users} возвращаете '
                f'email пользователей'
            )
            assert data['results'][0].get('username') == admin.username, (
                f'Проверьте, что при GET запросе {self.url_users} возвращаете '
                f'username пользователей'
            )
            assert data['results'][0].get('first_name') == admin.first_name, (
                f'Проверьте, что при GET запросе {self.url_users} возвращаете '
                f'first_name пользователей'
            )
            assert data['results'][0].get('last_name') == admin.last_name, (
                f'Проверьте, что при GET запросе {self.url_users} возвращаете '
                f'last_name пользователей'
            )
            # assert data['results'][0].get(
            #     'is_subscribed') == admin.is_subscribed, (
            #     f'Проверьте, что при GET запросе {self.url_users} возвращаете '
            #     f'флаг is_subscribed пользователей'
            # )

    @pytest.mark.django_db(transaction=True)
    def test_02_get_user_by_id(self, admin_client, client):
        user = create_users_api(admin_client)
        client_user = auth_client(user)
        clients = (
            admin_client, client_user, client
        )
        for client in clients:
            response = client.get(f'{self.url_users}{user.id}/')
            assert response.status_code != status.HTTP_404_NOT_FOUND, (
                f'Страница {self.url_users}id/ не найдена, проверьте этот '
                f'адрес в urls.py'
            )
            assert response.status_code == status.HTTP_200_OK, (
                f'Проверьте, что при GET запросе {self.url_users}id/ с токеном '
                f'авторизации возвращается статус {status.HTTP_200_OK}'
            )
            data = response.json()
            assert type(data) == dict, (
                f'Проверьте, что при GET запросе {self.url_users}id/ '
                f'возвращаете словарь с данными пользователя'
            )
            assert 'id' in data and data['id'] == user.id, (
                f'Проверьте, что при GET запросе {self.url_users}id/ '
                f'возвращаете id пользователя'
            )
            assert 'email' in data and data['email'] == user.email, (
                f'Проверьте, что при GET запросе {self.url_users}id/ '
                f'возвращаете email пользователя'
            )
            assert 'username' in data and data['username'] == user.username, (
                f'Проверьте, что при GET запросе {self.url_users}id/ '
                f'возвращаете username пользователя'
            )
            assert 'first_name' in data and data[
                'first_name'] == user.first_name, (
                f'Проверьте, что при GET запросе {self.url_users}id/ '
                f'возвращаете first_name пользователя'
            )
            assert 'last_name' in data and data[
                'last_name'] == user.last_name, (
                f'Проверьте, что при GET запросе {self.url_users}id/ '
                f'возвращаете last_name пользователя'
            )
            # assert 'is_subscribed' in data and data[
            #     'is_subscribed'] == user.is_subscribed, (
            #     f'Проверьте, что при GET запросе {self.url_users}id/ '
            #     f'возвращаете флаг is_subscribed пользователя'
            # )

    @pytest.mark.django_db(transaction=True)
    def test_03_user_me_get_by_yourself(self, admin_client):
        user = create_users_api(admin_client)
        client_user = auth_client(user)
        response = client_user.get(self.url_me)
        assert response.status_code == status.HTTP_200_OK, (
            f'Проверьте, что при GET запросе {self.url_me} с токеном '
            f'авторизации возвращается статус {status.HTTP_200_OK}'
        )
        response_data = response.json()
        assert response_data.get('id') == user.id, (
            f'Проверьте, что при GET запросе на {self.url_me} '
            f'возвращаете id пользователя'
        )
        assert response_data.get('email') == user.email, (
            f'Проверьте, что при GET запросе на {self.url_me} '
            f'возвращаете email пользователя'
        )
        assert response_data.get('username') == user.username, (
            f'Проверьте, что при GET запросе на {self.url_me} '
            f'возвращаете username  пользователя'
        )
        assert response_data.get('first_name') == user.first_name, (
            f'Проверьте, что при GET запросе на {self.url_me} '
            f'возвращаете first_name  пользователя'
        )
        assert response_data.get('last_name') == user.last_name, (
            f'Проверьте, что при GET запросе на {self.url_me} '
            f'возвращаете last_name  пользователя'
        )
        # assert response_data.get('is_subscribed') == user.is_subscribed, (
        #     f'Проверьте, что при GET запросе на {self.url_me} '
        #     f'возвращаете флаг is_subscribed пользователя'
        # )

    @pytest.mark.django_db(transaction=True)
    def test_04_user_set_password_by_yourself(self, admin_client):
        user = create_users_api(admin_client)
        client_user = auth_client(user)
        response = client_user.post(self.url_password)
        response_data = response.json()

        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'Проверьте, что при POST запросе {self.url_password} без данных '
            f'статус {status.HTTP_400_BAD_REQUEST}'
        )
        info_fields = ['new_password', 'current_password']
        for field in info_fields:
            assert (field in response_data.keys()
                    and isinstance(response_data[field], list)), (
                'Проверьте, что при запросе без данных в ответе есть '
                'сообщение о том, какие поля пустые'
            )

        invalid_passwords = {
            'new_password': 'NewPassword123',
            'current_password': 'Test1234567'
        }
        response = client_user.post(self.url_password, data=invalid_passwords)
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'Проверьте, что при POST запросе {self.url_password} с неверным '
            f'старым паролем возвращается статус {status.HTTP_400_BAD_REQUEST}'
        )

        passwords = {
            'new_password': 'NewPassword123',
            'current_password': '1234567Test'
        }
        response = client_user.post(self.url_password, data=passwords)
        assert response.status_code == status.HTTP_204_NO_CONTENT, (
            f'Проверьте, что при POST запросе {self.url_password} с новым и '
            f'старым паролем возвращается статус {status.HTTP_204_NO_CONTENT}'
        )

        bad_passwords = {
            'new_password': 'newpassword',
            'current_password': '1234567Test'
        }
        response = client_user.post(self.url_password, data=bad_passwords)
        assert response.status_code == status.HTTP_400_BAD_REQUEST , (
            f'Проверьте, что при POST запросе {self.url_password} '
            f'с некорректным новым паролем возвращается статус '
            f'{status.HTTP_400_BAD_REQUEST}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_05_user_delete_token_by_yourself(self, admin_client):
        user = create_users_api(admin_client)
        client_user = auth_client(user)
        response = client_user.post(self.url_logout)

        assert response.status_code == status.HTTP_204_NO_CONTENT, (
            f'Проверьте, что при POST запросе {self.url_password} удаляется '
            f'токен и возвращается статус {status.HTTP_204_NO_CONTENT}'
        )
