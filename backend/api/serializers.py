import base64
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.validators import EmailValidator
from django.core.files.base import ContentFile
from django.db import IntegrityError
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator

from receipts.models import (
    Tag,
    Favorite,
    Follow,
    Receipt,
    Ingredient,
    IngredientInRecipe,
    ShoppingList
)
from users.models import (
    MAX_USERNAME_LENGTH,
    MAX_FIRSTNAME_LENGTH,
    MAX_LASTNAME_LENGTH,
    MAX_EMAIL_LENGTH,
    USERNAME_REGEX,
    FORBIDDEN_USERNAMES
)


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Декодирует строку base64 в файл изображения."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class MyUserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор используемый для создания пользователя."""

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'password')
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password'))
        return super(MyUserCreateSerializer, self).create(validated_data)

    def validate_username(self, username):
        if len(username) > MAX_USERNAME_LENGTH:
            raise ValidationError(
                'Имя пользователя не должно быть больше '
                f'{MAX_USERNAME_LENGTH} символов.')
        if username in FORBIDDEN_USERNAMES:
            raise ValidationError(
                f'Запрещено использовать имя "{username}".')
        if not re.match(USERNAME_REGEX, username):
            raise ValidationError(
                'Имя пользователя может содерджать только буквы, цифры, '
                'точки, _, @, +, или -')
        return username

    def validate_email(self, email):
        if len(email) > MAX_EMAIL_LENGTH:
            raise ValidationError(
                'Email адрес не может быть больше '
                f'{MAX_EMAIL_LENGTH} символов.')
        if not EmailValidator(email):
            raise ValidationError(
                'Указан некорректный email адрес.')
        return email

    def validate_first_name(self, name):
        if len(name) > MAX_FIRSTNAME_LENGTH:
            raise ValidationError(
                'Длина имени не может быть больше '
                f'{MAX_FIRSTNAME_LENGTH} символов.')
        return name

    def validate_last_name(self, name):
        if len(name) > MAX_LASTNAME_LENGTH:
            raise ValidationError(
                'Длина фамилии не может быть больше '
                f'{MAX_LASTNAME_LENGTH} символов.')
        return name


class MyUserSerializer(serializers.ModelSerializer):
    """Сериализатор для представления пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name',
            'last_name', 'password', 'is_subscribed', 'avatar')
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_is_subscribed(self, obj):
        request = self.context.get('request', None)
        if request:
            current_user = request.user
            if not current_user.is_authenticated:
                return False
            return Follow.objects.filter(
                user=current_user, following=obj).exists()
        return False

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password'))
        return super(MyUserSerializer, self).create(validated_data)

    def validate_username(self, username):
        if len(username) > MAX_USERNAME_LENGTH:
            raise ValidationError(
                'Имя пользователя не должно быть больше '
                f'{MAX_USERNAME_LENGTH} символов.')
        if username in FORBIDDEN_USERNAMES:
            raise ValidationError(
                f'Запрещено использовать имя "{username}".')
        if not re.match(USERNAME_REGEX, username):
            raise ValidationError(
                'Имя пользователя может содерджать только буквы, цифры, '
                'точки, _, @, +, или -')
        return username

    def validate_email(self, email):
        if len(email) > MAX_EMAIL_LENGTH:
            raise ValidationError(
                'Email адрес не может быть больше '
                f'{MAX_EMAIL_LENGTH} символов.')
        if not EmailValidator(email):
            raise ValidationError(
                'Указан некорректный email адрес.')
        return email

    def get_or_create(self, validated_data):
        user, created = User.objects.get_or_create(
            username=validated_data['username'],
            email=validated_data['email'])
        return user


class UserAvatarSerializer(serializers.ModelSerializer): # MyUserSerializer
    """Сериализатор для обработки аватара пользователя."""

    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, data):
        if not data.get('avatar'):
            raise ValidationError(
                'Отсутствует аватар в переданных данных.'
            )
        return super().validate(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тэгов."""

    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания ингредиента в рецепте."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')

    def validate_amount(self, amount):
        if amount < 1:
            raise ValidationError(
                'Количество ингредиента в рецепте должно быть 1 или больше')
        return amount


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор представления ингредиента в рецепте."""

    ingredient = IngredientSerializer()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('ingredient', 'amount')


class RecipeSerializerGetRequestBasic(serializers.ModelSerializer):
    """Базовый сериализатор рецепта для GET запроса."""

    class Meta:
        model = Receipt
        fields = ('id', 'name', 'image', 'cooking_time')


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
            'id',
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time')

    def get_ingredients(self, obj):
        ingredients = obj.ingredientinrecipe.all()
        data = []
        for ingredient in ingredients:
            serializer = IngredientSerializer(instance=ingredient.ingredient)
            ingredient_dict = dict(serializer.data)
            ingredient_dict['amount'] = ingredient.amount
            data.append(ingredient_dict)
        return data

    def get_is_favorited(self, obj):
        request = self.context.get('request', None)
        if request:
            if not request.user.is_authenticated:
                return False
            return Favorite.objects.filter(
                receipt=obj, user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request', None)
        if request:
            if not request.user.is_authenticated:
                return False
            return ShoppingList.objects.filter(
                receipt=obj, user=request.user).exists()
        return False


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""

    ingredients = IngredientInRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Receipt
        fields = (
            'tags',
            'ingredients',
            'cooking_time',
            'image',
            'name',
            'text')

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients or len(ingredients) < 1:
            raise ValidationError(
                'Ошибка списка ингредиентов.'
            )
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise ValidationError(
                'Список ингредиентов содержит повторяющиеся ингредиенты.')
        tags = data.get('tags')
        if not tags or len(tags) < 1:
            raise ValidationError(
                'Ошибка списка тэгов.'
            )
        if len(tags) != len(set(tags)):
            raise ValidationError(
                'Список тэгов содержит повторяющиеся ингредиенты.')
        return super().validate(data)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Receipt.objects.create(
            **validated_data, author=self.context['request'].user)
        recipe.tags.set(tags)
        ingredients_to_add = []
        for ingredient in ingredients:
            ingredients_to_add.append(IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ))
        IngredientInRecipe.objects.bulk_create(ingredients_to_add)
        return recipe

    def update(self, instance, validated_data):
        """Обновляет информацию в рецепте без лишних удалений
        существующих ингредиентов в рецепте."""
        ingredients = validated_data.pop('ingredients')
        ingredients_dict = {ingredient['id']: ingredient['amount']
                            for ingredient in ingredients}

        all_ingredients_in_recipe = instance.ingredientinrecipe.all()
        all_ingredients_in_recipe_ids = {
            ingredient.ingredient.id for ingredient
            in all_ingredients_in_recipe}

        ingredients_to_remove_pks = [
            ingredient.pk for ingredient in all_ingredients_in_recipe
            if ingredient.ingredient not in ingredients_dict.keys()]
        ingredients_to_update = [
            ingredient for ingredient in all_ingredients_in_recipe
            if ingredient.ingredient in ingredients_dict.keys()
            and ingredient.amount != ingredients_dict[ingredient.ingredient]]
        ingredients_to_add = [
            ingredient for ingredient
            in ingredients_dict.keys()
            if ingredient.id not in all_ingredients_in_recipe_ids]

        added_ingredients = [IngredientInRecipe(
            recipe=instance,
            ingredient=ingredient,
            amount=ingredients_dict[ingredient])
            for ingredient in ingredients_to_add]
        IngredientInRecipe.objects.bulk_create(added_ingredients)

        for ingredient_in_recipe in ingredients_to_update:
            ingredient_in_recipe.amount = ingredients_dict[
                ingredient_in_recipe.ingredient]
            ingredient_in_recipe.save()

        IngredientInRecipe.objects.filter(
            pk__in=ingredients_to_remove_pks).delete()

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
        fields = MyUserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        request = self.context.get('request', None)
        limit = 999
        if request:
            limit = int(request.query_params.get('recipes_limit', 999))
        return RecipeSerializerGetRequestBasic(obj.recipes.all()[:limit],
                                               many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializerGetRequestBasic(read_only=True)

    class Meta:
        model = Receipt
        fields = ('recipe', )
