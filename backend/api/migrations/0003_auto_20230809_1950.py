# Generated by Django 3.2 on 2023-08-09 19:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Должно быть больше 1'), django.core.validators.MaxValueValidator(32000, 'Должно быть меньше 32000')], verbose_name='время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Должно быть больше 1'), django.core.validators.MaxValueValidator(32000, 'Должно быть меньше 32000')], verbose_name='количество'),
        ),
    ]
