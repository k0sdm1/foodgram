import base64
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from django.core.validators import EmailValidator
from django.forms import ValidationError
from rest_framework import serializers

from receipts.models import (
    Ingredient,
    IngredientInRecipe,
    Follow,
    Tag,
    Receipt,
    MAX_COOKING_TIME,
    MAX_INGREDIENT_AMOUNT,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
)
from users.models import (
    MAX_USERNAME_LENGTH,
    MAX_FIRSTNAME_LENGTH,
    MAX_LASTNAME_LENGTH,
    MAX_EMAIL_LENGTH,
    USERNAME_REGEX,
    FORBIDDEN_USERNAMES,
)


User = get_user_model()

RECIPES_IN_SUBSCRIPTION = 25


class Base64ImageField(serializers.ImageField):
    """Декодирует строку base64 в файл изображения."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class MyUserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор используемый для создания пользователя."""

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        validated_data["password"] = make_password(
            validated_data.get("password")
        )
        return super(MyUserCreateSerializer, self).create(validated_data)

    def validate_username(self, username):
        if len(username) > MAX_USERNAME_LENGTH:
            raise ValidationError(
                "Имя пользователя не должно быть больше "
                f"{MAX_USERNAME_LENGTH} символов."
            )
        if username in FORBIDDEN_USERNAMES:
            raise ValidationError(f"Запрещено использовать имя '{username}'.")
        if not re.match(USERNAME_REGEX, username):
            raise ValidationError(
                "Имя пользователя может содерджать только буквы, цифры, "
                "точки, _, @, +, или -"
            )
        return username

    def validate_email(self, email):
        if len(email) > MAX_EMAIL_LENGTH:
            raise ValidationError(
                "Email адрес не может быть больше "
                f"{MAX_EMAIL_LENGTH} символов."
            )
        if not EmailValidator(email):
            raise ValidationError("Указан некорректный email адрес.")
        return email

    def validate_first_name(self, name):
        if len(name) > MAX_FIRSTNAME_LENGTH:
            raise ValidationError(
                "Длина имени не может быть больше "
                f"{MAX_FIRSTNAME_LENGTH} символов."
            )
        return name

    def validate_last_name(self, name):
        if len(name) > MAX_LASTNAME_LENGTH:
            raise ValidationError(
                "Длина фамилии не может быть больше "
                f"{MAX_LASTNAME_LENGTH} символов."
            )
        return name


class MyUserSerializer(serializers.ModelSerializer):
    """Сериализатор для представления пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "is_subscribed",
            "avatar",
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def get_is_subscribed(self, obj):
        request = self.context.get("request", None)
        if request:
            current_user = request.user
            if not current_user.is_authenticated:
                return False
            return obj.followings.filter(
                user=current_user
            ).exists()
        return False

    def create(self, validated_data):
        validated_data["password"] = make_password(
            validated_data.get("password")
        )
        return super(MyUserSerializer, self).create(validated_data)

    def validate_username(self, username):
        if len(username) > MAX_USERNAME_LENGTH:
            raise ValidationError(
                "Имя пользователя не должно быть больше "
                f"{MAX_USERNAME_LENGTH} символов."
            )
        if username in FORBIDDEN_USERNAMES:
            raise ValidationError(f"Запрещено использовать имя '{username}'.")
        if not re.match(USERNAME_REGEX, username):
            raise ValidationError(
                "Имя пользователя может содерджать только буквы, цифры, "
                "точки, _, @, +, или -"
            )
        return username

    def validate_email(self, email):
        if len(email) > MAX_EMAIL_LENGTH:
            raise ValidationError(
                "Email адрес не может быть больше "
                f"{MAX_EMAIL_LENGTH} символов."
            )
        if not EmailValidator(email):
            raise ValidationError("Указан некорректный email адрес.")
        return email

    def get_or_create(self, validated_data):
        user, created = User.objects.get_or_create(
            username=validated_data["username"], email=validated_data["email"]
        )
        return user


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обработки аватара пользователя."""

    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ("avatar",)

    def validate(self, data):
        if not data.get("avatar"):
            raise ValidationError("Отсутствует аватар в переданных данных.")
        return super().validate(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""

    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания ингредиента в рецепте."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        max_value=MAX_INGREDIENT_AMOUNT, min_value=MIN_INGREDIENT_AMOUNT
    )

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "amount")


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор представления ингредиента в рецепте."""

    ingredient = IngredientSerializer()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ("ingredient", "amount")


class RecipeSerializerGetRequestBasic(serializers.ModelSerializer):
    """Базовый сериализатор рецепта для GET запроса."""

    class Meta:
        model = Receipt
        fields = ("id", "name", "image", "cooking_time")


class RecipeSerializerGetRequest(serializers.ModelSerializer):
    """Сериализатор для полной репрезентации рецепта."""

    author = MyUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Receipt
        fields = (
            "id",
            "author",
            "tags",
            "is_favorited",
            "is_in_shopping_cart",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_ingredients(self, obj):
        ingredients = obj.ingredientinrecipe.all()
        data = []
        for ingredient in ingredients:
            serializer = IngredientSerializer(instance=ingredient.ingredient)
            ingredient_dict = dict(serializer.data)
            ingredient_dict["amount"] = ingredient.amount
            data.append(ingredient_dict)
        return data

    def get_is_favorited(self, obj):
        request = self.context.get("request", None)
        if not request or not request.user.is_authenticated:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request", None)
        if not request or not request.user.is_authenticated:
            return False
        return obj.shopping_lists.filter(user=request.user).exists()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""

    ingredients = IngredientInRecipeCreateSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        max_value=MAX_COOKING_TIME, min_value=MIN_COOKING_TIME
    )

    class Meta:
        model = Receipt
        fields = (
            "tags",
            "ingredients",
            "cooking_time",
            "image",
            "name",
            "text",
        )

    def validate(self, data):
        ingredients = data.get("ingredients")
        if not ingredients:
            raise ValidationError("Ошибка списка ингредиентов.")
        ingredient_ids = [ingredient["id"] for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError(
                "Список ингредиентов содержит повторяющиеся ингредиенты."
            )
        tags = data.get("tags")
        if not tags:
            raise ValidationError("Ошибка списка тэгов.")
        if len(tags) != len(set(tags)):
            raise ValidationError(
                "Список тэгов содержит повторяющиеся ингредиенты."
            )
        return super().validate(data)

    def add_ingredients(self, recipe, ingredients):
        ingredients_to_add = []
        for ingredient in ingredients:
            ingredients_to_add.append(
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient=ingredient["id"],
                    amount=ingredient["amount"],
                )
            )
        return ingredients_to_add

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Receipt.objects.create(
            **validated_data, author=self.context["request"].user
        )
        recipe.tags.set(tags)
        ingredients_to_add = self.add_ingredients(recipe, ingredients)
        IngredientInRecipe.objects.bulk_create(ingredients_to_add)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет информацию в рецепте."""
        ingredients = validated_data.pop("ingredients")
        ingredients_to_add = self.add_ingredients(
            recipe=instance, ingredients=ingredients
        )
        instance.ingredientinrecipe.all().delete()
        IngredientInRecipe.objects.bulk_create(ingredients_to_add)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializerGetRequest(instance)
        return serializer.data


class SubscribeUserSerializer(MyUserSerializer):
    """Сериализатор репрезентации подписки."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(MyUserSerializer.Meta):
        model = User
        fields = MyUserSerializer.Meta.fields + ("recipes", "recipes_count")

    def get_recipes(self, obj):
        request = self.context.get("request", None)
        if request:
            limit = int(
                request.query_params.get(
                    "recipes_limit", RECIPES_IN_SUBSCRIPTION
                )
            )
        return RecipeSerializerGetRequestBasic(
            obj.recipes.all()[:limit], many=True
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializerGetRequestBasic(read_only=True)

    class Meta:
        model = Receipt
        fields = ("recipe",)
