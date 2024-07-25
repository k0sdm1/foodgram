# Generated by Django 3.2.3 on 2024-07-13 19:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0003_auto_20240713_2127'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='receipt',
            name='ingredients',
        ),
        migrations.AddField(
            model_name='ingredientinrecipe',
            name='recipe',
            field=models.ForeignKey(default=1, help_text='Обязательное поле', on_delete=django.db.models.deletion.CASCADE, related_name='ingredientinrecipe', to='receipts.receipt', verbose_name='Рецепт'),
            preserve_default=False,
        ),
    ]
