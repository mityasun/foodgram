# Generated by Django 2.2.28 on 2022-11-13 15:04

from django.db import migrations, models
import recipes.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IngredientInRecipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(validators=[recipes.validators.validate_amount], verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'Количество ингредиента',
                'verbose_name_plural': 'Количество ингредиентов',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Ingredients',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=200, unique=True, verbose_name='Название')),
                ('measurement_unit', models.CharField(max_length=200, verbose_name='Ед. измерения')),
            ],
            options={
                'verbose_name': 'ингредиенты',
                'verbose_name_plural': 'ингредиент',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Recipes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название рецепта')),
                ('text', models.TextField(verbose_name='Описание')),
                ('image', models.ImageField(upload_to='recipes/%Y/%m/%d/', verbose_name='Картинка')),
                ('cooking_time', models.PositiveSmallIntegerField(validators=[recipes.validators.validate_cooking_time], verbose_name='Время приготовления')),
            ],
            options={
                'verbose_name': 'рецепт',
                'verbose_name_plural': 'рецепты',
                'ordering': ('-id',),
            },
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='Название тега')),
                ('color', models.CharField(max_length=7, unique=True, verbose_name='Цвет')),
                ('slug', models.SlugField(max_length=200, unique=True, validators=[recipes.validators.validate_slug], verbose_name='Ссылка')),
            ],
            options={
                'verbose_name': 'тэг',
                'verbose_name_plural': 'теги',
                'ordering': ('-id',),
            },
        ),
    ]