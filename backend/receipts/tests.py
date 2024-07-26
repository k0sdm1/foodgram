from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from receipts.models import Ingredient, Tag


class BaseTestData(TestCase):
    def setUp(self):
        user = get_user_model()
        self.user = user.objects.create_user(username="auth_user")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.firstIndredient = Ingredient.objects.create(
            name="хлеб", measurement_unit="г"
        )
        self.secondIndredient = Ingredient.objects.create(
            name="масло", measurement_unit="г"
        )
        self.tag = Tag.objects.create(slug="breakfast", name="завтрак")


class FoodgramAPITestCase(BaseTestData):
    def setUp(self):
        super().setUp()

    def test_users_list_exists(self):
        """Проверка доступности списка пользователей."""
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tags_list_exists(self):
        """Проверка доступности списка тегов."""
        response = self.client.get("/api/tags/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_ingredients_list_exists(self):
        """Проверка доступности списка ингредиентов."""
        response = self.client.get("/api/ingredients/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_recipes_list_exists(self):
        """Проверка доступности списка рецептов."""
        response = self.client.get("/api/recipes/")
        self.assertEqual(response.status_code, HTTPStatus.OK)


class IngredientAPITests(BaseTestData):
    recipe_endpoint = "/api/recipes/"

    def setUp(self):
        super().setUp()

    def test_post_create_recipe(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            self.recipe_endpoint,
            data={
                "ingredients": [
                    {"id": self.firstIndredient.id, "amount": 12},
                    {"id": self.secondIndredient.id, "amount": 6},
                ],
                "tags": [self.tag.id],
                "image": (
                    "data:image/png;base64,"
                    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVB"
                    "MVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAA"
                    "AACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=="
                ),
                "name": "Бутерброд",
                "text": "Тестовое описание",
                "cooking_time": 1,
            },
            format="json",
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.CREATED,
            msg="Код статуса ответа должен быть 201.",
        )
