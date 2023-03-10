from rest_framework.test import APITestCase
from rest_framework.utils.serializer_helpers import ReturnList

from .models import Tag


class TagTestCase(APITestCase):
    @classmethod
    def setUp(cls) -> None:
        super().setUpClass()

        cls.tag_model_fields = [
            x.name for x in getattr(Tag, '_meta').fields
        ]

        cls.first_tag = Tag.objects.create(
            name='First Tag',
            slug='first_tag_slug'
        )

        cls.second_tag = Tag.objects.create(
            name='Second Tag',
            slug='second_tag_slug'
        )

    def _assert_tag_card(self, data):
        for key in self.tag_model_fields:
            self.assertIsNotNone(
                data.get(key), f'Отсутсвует {key} в карточке тэга'
            )

    def _assert_not_paginated_data(self, data):
        self.assertTrue(
            isinstance(data, ReturnList),
            "Ответ не должен содержать пагинацию"
        )

    def test_tag_list(self):
        tag_list = self.client.get(
            '/tags/'
        )
        data = tag_list.data
        self.assertEqual(tag_list.status_code, 200, 'Некорректный HTTP STATUS')
        self._assert_not_paginated_data(data)
        for x in data:
            self._assert_tag_card(x)

    def test_tag_item(self):
        tag_id = self.first_tag.id
        tag_item = self.client.get(
            f'/tags/{tag_id}/'
        )
        data = tag_item.data
        self.assertEqual(tag_item.status_code, 200, 'Некорректный HTTP STATUS')
        self._assert_tag_card(data)
