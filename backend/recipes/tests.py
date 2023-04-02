import json

from rest_framework.test import APITestCase

from tags.models import Tag

from users.models import User

from .models import IngredientUnit
from .models import Recipe


class RecipeTestCase(APITestCase):
    @classmethod
    def setUp(cls) -> None:
        super().setUpClass()

        user = User.objects.create_user(
            username='test_user_1',
            email='test_user_1@mail.ru',
            password='12345678'
        )

        another_user = User.objects.create_user(
            username='another_author',
            email='another_author@gmail.com',
            password='12345678'
        )
        cls.user = user
        cls.another_user = another_user

        cls.recipe_model_fields = [
            x.name for x in getattr(Recipe, '_meta').fields
        ]

        cls.ingredient_unit_model_fields = [
            x.name for x in getattr(IngredientUnit, '_meta').fields
        ]

        cls.ingredients = [
            IngredientUnit.objects.create(
                name=name, measurement_unit=unit
            ) for name, unit in (
                ('Крупа', 'г'),
                ('Картошка', 'кг')
            )
        ]

        cls.tags = [
            Tag.objects.create(name=n, slug=s) for n, s in (
                ('Популярный', 'popular'),
                ('Ужин', 'dinner')
            )
        ]

        addit_recipe_data = {
            'author': user,
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==',
            'name': 'string',
            'text': 'string',
            'cooking_time': 1
        }

        cls.recipe_1 = Recipe.objects.create(
            **addit_recipe_data
        )

        cls.recipe_1.tags.add(cls.tags[0])

        cls.recipe_2 = Recipe.objects.create(
            **addit_recipe_data,
        )

        addit_recipe_data["author"] = another_user
        cls.recipe_3 = Recipe.objects.create(
            **addit_recipe_data,
        )

    def _login_request(self):
        test_login_body = {
            'email': self.user.email,
            'password': '12345678'
        }
        return self.client.post(
            '/auth/token/login/',
            data=test_login_body
        )

    def _logout_request(self):
        token = self.user.auth_token.key
        return self.client.post(
            '/auth/token/logout/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )

    def _assert_paginated_data(self, data):
        keys = ['count', 'next', 'previous', 'results']
        self.assertEqual(list(data.keys()), keys,
                         "Отсутсвует пагинация в списке рецептов")

    def _assert_not_paginated_data(self, data):
        keys = ['count', 'next', 'previous', 'results']
        self.assertNotEqual(list(data.keys()), keys,
                            "Пагинация не должна присутсвовать в ответе")

    def _assert_recipe_item(self, item):
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_in_shopping_cart', 'is_favorited',
            'name', 'image', 'text', 'cooking_time'
        )
        self.assertEqual(tuple(item.keys()), fields,
                         "Некорректный вывод элемента списка рецептов")

    def test_create_recipe(self):
        addit_recipe_data = {
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==',
            'name': 'string',
            'text': 'string',
            'cooking_time': 1
        }
        false_response = self.client.post(
            '/recipes/',
            data=addit_recipe_data
        )
        self.assertEqual(
            401,
            false_response.status_code,
            'Неккорректный статус код при создании рецепта не авторизированным пользователем'
        )
        self._login_request()
        token = self.user.auth_token
        recipe_body_create = json.dumps(
            dict(
                **addit_recipe_data,
                tags=[1, 2],
                ingredients=[
                    dict(id=1, amount=1),
                    dict(id=2, amount=1),
                ]
            )
        )
        create_response = self.client.post(
            '/recipes/',
            content_type='application/json',
            data=recipe_body_create,
            HTTP_AUTHORIZATION=f'Token {token}'

        )
        self.assertEqual(
            201,
            create_response.status_code,
            'Некорректный HTTP - статус при создании пользователя'
        )

        recipes = Recipe.objects.all()
        count_recipes = recipes.count()
        recipe = Recipe.objects.get(id=create_response.data["id"])
        self.assertEqual(count_recipes, 4, 'Рецепт не создался')
        self.assertEqual(
            recipe.author.id, self.user.id,
            'Автор рецепта некорректный'
        )

    def test_in_shopping_list(self):
        false_response = self.client.post(
            '/recipes/1/shopping_cart/'
        )
        self.assertEqual(
            401,
            false_response.status_code,
            'Неккорректный статус код при добавлении рецепта'
            ' в список покупок не авторизированным пользователем'
        )

        self._login_request()
        token = self.user.auth_token
        response = self.client.post(
            '/recipes/1/shopping_cart/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )

        self.assertEqual(response.status_code, 201,
                         "Некорректный запрос при добавлении в список покупок")

        in_list_key = self.user.shop_list.recipes.filter(id=1).exists()

        self.assertTrue(in_list_key, "Рецепт не добавлен")

        delete_response = self.client.delete(
            '/recipes/1/shopping_cart/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )

        self.assertEqual(delete_response.status_code, 204,
                         "Некорректный запрос при удалении из списка покупок")

        in_list_key = self.user.shop_list.recipes.filter(id=1).exists()
        self.assertFalse(in_list_key, "Рецепт не удален из списка покупок")

    def test_in_favorites(self):
        false_response = self.client.post(
            '/recipes/1/favorite/'
        )
        self.assertEqual(
            401,
            false_response.status_code,
            'Неккорректный статус код при добавлении рецепта'
            ' в избранное не авторизированным пользователем'
        )

        self._login_request()
        token = self.user.auth_token
        response = self.client.post(
            '/recipes/1/favorite/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )

        self.assertEqual(response.status_code, 201,
                         "Некорректный запрос при добавлении в избранное")

        in_list_key = self.user.favorite.recipes.filter(id=1).exists()

        self.assertTrue(in_list_key, "Рецепт не добавлен")

        delete_response = self.client.delete(
            '/recipes/1/favorite/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )

        self.assertEqual(delete_response.status_code, 204,
                         "Некорректный запрос при удалении из избранных")

        in_list_key = self.user.shop_list.recipes.filter(id=1).exists()
        self.assertFalse(in_list_key, "Рецепт не удален из избранных")

    def test_delete_recipe(self):
        false_response = self.client.delete(
            '/recipes/1/'
        )
        self.assertEqual(
            401,
            false_response.status_code,
            'Неккорректный статус код при удалении рецепта'
            ' не авторизированным пользователем'
        )
        token = self.another_user.auth_token
        false_response = self.client.delete(
            '/recipes/1/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(
            403,
            false_response.status_code,
            'Неккорректный статус код при удалении рецепта'
            ' пользователем не являющимся автором'
        )
        token = self.user.auth_token
        response = self.client.delete(
            '/recipes/1/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )

        self.assertEqual(
            204,
            response.status_code,
            "Некорректный HTTP-статус при удалении рецепта"
        )

        delete_key = Recipe.objects.filter(id=1).exists()
        count_recipes = Recipe.objects.all().count()
        self.assertFalse(delete_key, "Рецепт не удален")
        self.assertEqual(2, count_recipes, "Рецепт не удален")

    def test_update_recipe(self):
        false_response = self.client.patch(
            '/recipes/1/'
        )
        self.assertEqual(
            401,
            false_response.status_code,
            'Неккорректный статус код при обновлении рецепта'
            ' не авторизированным пользователем'
        )
        token = self.another_user.auth_token
        false_response = self.client.patch(
            '/recipes/1/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(
            403,
            false_response.status_code,
            'Неккорректный статус код при обновлении рецепта'
            ' пользователем не являющимся автором'
        )

        token = self.user.auth_token
        name = self.recipe_1.name
        tags = [x['id'] for x in self.recipe_1.tags.values("id")]
        ingredients = [
            x['ingredient_unit__id'] for x in self.recipe_1.ingredients.values(
                'ingredient_unit__id'
            )
        ]
        response = self.client.patch(
            '/recipes/1/',
            HTTP_AUTHORIZATION=f'Token {token}',
            content_type='application/json',
            data=json.dumps(
                dict(
                    name='name',
                    tags=[1, 2],
                    ingredients=[
                        dict(
                            id=1,
                            amount=1,
                        ),
                        dict(
                            id=1,
                            amount=1
                        )
                    ]
                )
            )
        )

        self.assertEqual(
            response.status_code,
            200,
            "Некорректный статус при обновлении рецепта"
        )

        new_tags = [x['id'] for x in self.recipe_1.tags.values("id")]
        new_ingredients = [
            x['ingredient_unit__id'] for x in self.recipe_1.ingredients.values(
                'ingredient_unit__id'
            )
        ]
        self.assertNotEqual(tags, new_tags, "Рецепт не обновился")
        self.assertNotEqual(
            ingredients, new_ingredients, "Рецепт не обновился"
        )
        new_name = Recipe.objects.get(id=1).name
        self.assertNotEqual(name, new_name, "Рецепт не обновился")

    def test_get_recipe_unit(self):
        self._login_request()
        token = self.user.auth_token
        self.user.shop_list.recipes.add(self.recipe_1)
        self.user.favorite.recipes.add(self.recipe_1)

        request = self.client.get(
            '/recipes/1/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )

        self.assertEqual(
            request.status_code, 200,
            "Некорректный статус при запросе рецепта"
        )

        data = request.data
        self._assert_not_paginated_data(data)
        self._assert_recipe_item(data)
        self.assertTrue(
            data['is_in_shopping_cart'],
            "Некорректное значение в поле is_in_shopping_cart"
        )
        self.assertTrue(
            data['is_favorited'],
            "Некорректное значение в поле is_favorited"
        )

    def test_get_recipe_list(self):
        guest_response = self.client.get(
            '/recipes/?tags=popular'
        )
        self.assertEqual(200, guest_response.status_code,
                         "Некорректный статус при запросе списка рецептов")
        self._assert_paginated_data(guest_response.data)
        data = guest_response.data['results']
        self.assertEqual(len(data), 1)
        for item in data:
            self._assert_recipe_item(item)
            self.assertFalse(
                item['is_in_shopping_cart'],
                "Некорректное значение в поле is_in_shopping_cart"
            )
            self.assertFalse(
                item['is_favorited'],
                "Некорректное значение в поле is_favorited"
            )
        guest_response = self.client.get(
            '/recipes/'
        )
        data = guest_response.data['results']
        self.assertEqual(
            len(data),
            3,
            'Некорректное значение вывода списка рецептов'
        )

    def test_recipes_filters(self):
        author = self.another_user.id

        author_filter = self.client.get(
            f'/recipes/?author={author}'
        )
        self.assertEqual(
            len(author_filter.data['results']),
            1,
            'Некорректное значение вывода списка рецептов с фильтром по автору'
        )

        self._login_request()

        self.user.shop_list.recipes.add(self.recipe_1)
        token = self.user.auth_token.key
        in_shop_cart_filter = self.client.get(
            '/recipes/?is_in_shopping_cart=1',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(
            len(in_shop_cart_filter.data["results"]),
            1,
            'Некорректное значение вывода списка рецептов с фильтром по списку покупок'
        )

        self.user.favorite.recipes.add(self.recipe_1)
        in_favorite_filter = self.client.get(
            '/recipes/?is_favorited=1',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(
            len(in_favorite_filter.data["results"]),
            1,
            'Некорректное значение вывода списка рецептов с фильтром по избранному'
        )
