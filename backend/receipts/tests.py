from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


class FoodgramAPITestCase(TestCase):
    def setUp(self):
        user = get_user_model()
        self.user = user.objects.create_user(username='auth_user')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_users_list_exists(self):
        """Проверка доступности списка пользователей."""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tags_list_exists(self):
        """Проверка доступности списка тегов."""
        response = self.client.get('/api/tags/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_ingredients_list_exists(self):
        """Проверка доступности списка ингредиентов."""
        response = self.client.get('/api/ingredients/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_recipes_list_exists(self):
        """Проверка доступности списка рецептов."""
        response = self.client.get('/api/recipes/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
