from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import (
    MinValueValidator
)
from django.db.models import F, Q


User = get_user_model()

MAX_SYMBOLS_ALLOWED = 2000


class Tag(models.Model):
    """Модель тэга рецепта."""

    name = models.CharField(
        max_length=32,
        verbose_name='Тэг',
        help_text='Тэг для рецепта, 32 символа максимум'
    )
    slug = models.SlugField(
        max_length=32,
        verbose_name='Слаг',
        help_text='Слаг тэга рецепта, 32 символа максимум'
    )

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        max_length=128,
        verbose_name='Ингредиент',
        help_text='Максимально 128 символов'
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Единица измерения',
        help_text='Максимально 64 символов'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Receipt(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        help_text='Обязательное поле',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
        help_text='Максимально 256 символов'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание рецепта, максимум 2000 символов',
        max_length=MAX_SYMBOLS_ALLOWED
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        verbose_name='Изображение блюда',
        help_text='Обязательное поле'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        help_text='Выражается в минутах',
        validators=(
            MinValueValidator(1, 'Значение должно быть ≥ 1'),
        )
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        help_text='Обязательно к заполнению',
        related_name='recipes'
    )
    publish_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время публикации',
        help_text='Заполняется автоматически'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('publish_time',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Модель ингредиента в конкретном рецепте."""

    recipe = models.ForeignKey(
        Receipt,
        related_name='ingredientinrecipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        help_text='Обязательное поле'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент в рецепте',
        help_text='Значение должно быть ≥ 1'
    )
    amount = models.IntegerField(
        validators=(MinValueValidator(1, 'Значение должно быть ≥ 1'),),
        verbose_name='Количество ингредиента в рецепте',
        help_text='Значение должно быть ≥ 1',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='ingredient_in_recipe_unique'),
        )
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        ordering = ('id',)

    def __str__(self):
        return (
            f'Ингредиент {self.ingredient} '
            f'в рецепте {self.recipe} '
            f'в количестве {self.amount} '
            f'{self.ingredient.measurement_unit}.')


class ShoppingList(models.Model):
    """Модель списка покупок пользователя."""

    user = models.ForeignKey(
        User,
        verbose_name='Владелец списка покупок',
        on_delete=models.CASCADE,
        help_text='Обязательное поле',
        related_name='shopping_lists'
    )
    receipt = models.ForeignKey(
        Receipt,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        help_text='Обязательное поле',
        related_name='shopping_lists'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'receipt'),
                name='user_receipt_in_shopping_unique'),
        )
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('id',)

    def __str__(self):
        return f'{self.receipt} в списке покупок у {self.user}'


class Favorite(models.Model):
    """Модель избранных рецептов пользователя."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        help_text='Обязательное поле',
        related_name='favorites'
    )
    receipt = models.ForeignKey(
        Receipt,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        help_text='Обязательное поле',
        related_name='favorites'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'receipt'),
                name='user_receipt_in_favorites_unique'),
        )
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('id',)

    def __str__(self):
        return f'{self.receipt} в избранном у пользователя {self.user}'


class Follow(models.Model):
    """Модель подписки пользователя на другого пользователя."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        help_text='Обязательное поле',
        related_name='followers'
    )
    following = models.ForeignKey(
        User,
        verbose_name='На кого подписан',
        on_delete=models.CASCADE,
        help_text='Обязательное поле',
        related_name='followings'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='user_following_unique'),
            models.CheckConstraint(
                check=~Q(user=F('following')),
                name='user_following_not_same')
        )
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
