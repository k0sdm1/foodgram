# Generated by Django 3.2.3 on 2024-07-12 12:52

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'избранный рецепт',
                'verbose_name_plural': 'Избранные рецепты',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'подписка',
                'verbose_name_plural': 'Подписки',
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Максимально 128 символов', max_length=128, verbose_name='Ингредиент')),
                ('measurement_unit', models.CharField(help_text='Максимально 64 символов', max_length=64, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Максимально 256 символов', max_length=256, verbose_name='Название')),
                ('text', models.TextField(help_text='Описание рецепта, максимум 2000 символов', max_length=2000, verbose_name='Описание')),
                ('image', models.ImageField(default=None, null=True, upload_to='recipes/images/')),
                ('cooking_time', models.IntegerField(help_text='Выражается в минутах', validators=[django.core.validators.MinValueValidator(1, 'Значение должно быть ≥ 1')], verbose_name='Время приготовления')),
            ],
            options={
                'verbose_name': 'рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Тэг для рецепта, 32 символа максимум', max_length=32, verbose_name='Тэг')),
                ('slug', models.SlugField(help_text='Слаг тэга рецепта, 32 символа максимум', max_length=32, verbose_name='Слаг')),
            ],
            options={
                'verbose_name': 'тэг',
                'verbose_name_plural': 'Тэги',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receipt', models.ForeignKey(help_text='Обязательное поле', on_delete=django.db.models.deletion.CASCADE, related_name='shopping_lists', to='receipts.receipt', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'список покупок',
                'verbose_name_plural': 'Списки покупок',
                'ordering': ('id',),
            },
        ),
    ]
