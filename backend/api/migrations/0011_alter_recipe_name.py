# Generated by Django 4.0 on 2022-01-03 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0010_alter_follow_options_alter_recipe_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="name",
            field=models.CharField(max_length=200, verbose_name="Название"),
        ),
    ]
