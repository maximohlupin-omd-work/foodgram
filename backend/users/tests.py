from rest_framework.test import APITestCase

from .models import User


class UsersTestCase(APITestCase):
    @classmethod
    def setUp(cls) -> None:
        super().setUpClass()
        user = User

        cls.user = user.objects.create_user(
            username="test_user_1",
            email="test_user_1@mail.ru",
        )

        cls.another_user = user.objects.create_user(
            username='another_author',
            email='another_author@gmail.com',
        )

    def test_sign_up(self):
        test_user_body = {
            "email": "t10st@nail.ry",
            "username": "usermane",
            "first_name": "1",
            "last_name": "2",
            "password": "12345678"
        }
        rspn = self.client.post('/users/', data=test_user_body)
        self.assertEqual(rspn.status_code, 201, "Некорректный HTTP STATUS")
        qset = User.objects.filter(email="t10st@nail.ry")
        self.assertTrue(qset.exists(), "Пользователь не был создан")
        user = qset.values()[0]
        for k, v in user.items():
            if k != "password":
                test_val = test_user_body.get(k)
                if test_val:
                    self.assertEqual(
                        test_val, v,
                        f"Поле {k} созданного пользователя не совпадают"
                    )

    # def test_login(self):
    #     ...
    #
    # def test_logout(self):
    #     ...
    #
    # def test_set_password(self):
    #     ...
    #
    # def test_users_list(self):
    #     ...
    #
    # def test_user_card(self):
    #     ...
    #
    # def test_user_me_card(self):
    #     ...
