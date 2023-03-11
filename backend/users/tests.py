from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .models import User


class UsersTestCase(APITestCase):
    @classmethod
    def setUp(cls) -> None:
        print("--- Run UsersTestCase ---")
        super().setUpClass()
        user = User

        cls.user = user.objects.create_user(
            username='test_user_1',
            email='test_user_1@mail.ru',
            password='12345678'
        )

        cls.another_user = user.objects.create_user(
            username='another_author',
            email='another_author@gmail.com',
            password='12345678'
        )

    def _login_request(self, password: str = None):
        if not password:
            password = '12345678'
        test_login_body = {
            'email': self.user.email,
            'password': password
        }
        return self.client.post(
            '/auth/token/login/',
            data=test_login_body
        )

    def _set_pass_request(self, current_password: str, new_password: str):
        token = self.user.auth_token
        test_set_password_body = {
            'current_password': current_password,
            'new_password': new_password
        }
        return self.client.post(
            '/users/set_password/',
            data=test_set_password_body,
            HTTP_AUTHORIZATION=f'Token {token}'
        )

    def _logout_request(self):
        token = self.user.auth_token.key
        return self.client.post(
            '/auth/token/logout/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )

    def _assert_paginated_data(self, data):
        keys = ['count', 'next', 'previous', 'results']
        self.assertEqual(list(data.keys()), keys)
        for _obj in data['results']:
            self._assert_user_card(_obj)

    def _assert_user_card(self, data):
        keys = [
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        ]
        for k in keys:
            self.assertNotEqual(
                data.get(k), None, f'Ключ {k} отсутсвует в карточке'
            )

    def test_sign_up(self):
        test_user_body = {
            'email': 't10st@nail.ry',
            'username': 'usermane',
            'first_name': '1',
            'last_name': '2',
            'password': '12345678'
        }
        rspn = self.client.post('/users/', data=test_user_body)
        self.assertEqual(rspn.status_code, 201, 'Некорректный HTTP STATUS')
        qset = User.objects.filter(email='t10st@nail.ry')
        self.assertTrue(qset.exists(), 'Пользователь не был создан')
        user = qset.values()[0]
        for k, v in user.items():
            if k != 'password':
                test_val = test_user_body.get(k)
                if test_val:
                    self.assertEqual(
                        test_val, v,
                        f'Поле {k} созданного пользователя не совпадают'
                    )

    def test_login(self):
        false_auth = self._login_request(password='87654321')
        self.assertNotEqual(false_auth.status_code, 200)
        login = self._login_request()
        data = login.data
        token = data.get('auth_token')
        token_exists = Token.objects.filter(key=token).exists()
        auth_key = self.user.is_authenticated
        self.assertEqual(login.status_code, 200, 'Некорректный HTTP STATUS')
        self.assertTrue(token, 'Некоректное тело ответа при авторизации')
        self.assertTrue(token_exists, 'Токен не был создан')
        self.assertTrue(auth_key, 'Пользователь не авторизирован')

    def test_logout(self):
        self._login_request()
        logout = self._logout_request()
        token_key = Token.objects.filter(user=self.user).exists()
        self.assertEqual(logout.status_code, 204, 'Некорректный HTTP STATUS')
        self.assertFalse(token_key, 'Токен не был удален!')
        self.assertFalse(
            self.user.is_authenticated, 'Пользователь все еще авторизирован!'
        )

    def test_set_password(self):
        new_password = '87654321'
        current_password = '12345678'
        self._login_request()
        set_pass = self._set_pass_request(current_password, new_password)
        self.assertEqual(set_pass.status_code, 204, 'Некорректный HTTP STATUS')
        new_login = self._login_request(new_password)
        data = new_login.data
        token = data.get('auth_token')
        token_exists = Token.objects.filter(key=token).exists()
        auth_key = self.user.is_authenticated
        self.assertEqual(
            new_login.status_code, 200, 'Некорректный HTTP STATUS'
        )
        self.assertTrue(token, 'Некоректное тело ответа при авторизации')
        self.assertTrue(token_exists, 'Токен не был создан')
        self.assertTrue(auth_key, 'Пользователь не авторизирован')

    def test_users_list(self):
        users_list = self.client.get(
            '/users/'
        )
        self.assertEqual(
            users_list.status_code, 200, 'Некорректный HTTP STATUS'
        )
        data = users_list.data
        self._assert_paginated_data(data)

    def test_user_card(self):
        self._login_request()
        token = self.user.auth_token
        user_card = self.client.get(
            f'/users/{self.another_user.pk}/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(
            user_card.status_code, 200, 'Некорректный HTTP STATUS'
        )
        self._assert_user_card(user_card.data)

    def test_user_me_card(self):
        self._login_request()
        token = self.user.auth_token
        user_card = self.client.get(
            f'/users/me/',
            HTTP_AUTHORIZATION=f'Token {token}',
        )
        self.assertEqual(
            user_card.status_code, 200, 'Некорректный HTTP STATUS'
        )
        self._assert_user_card(user_card.data)
