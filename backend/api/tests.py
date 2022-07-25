import json
from http import HTTPStatus
from random import choice, choices, randint
from time import time

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import (
    Amount,
    Favorite,
    Follow,
    Ingredient,
    Recipe,
    Tag,
    TagRecipe,
    Trolley,
)
from users.models import User


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        client = APIClient()
        # Регистрация нового пользователя через эндпоинт.
        email = f"{cls.__name__}@yandex.ru"
        cls.password = "dsofniwjhfd87yr489384ur98reufhd"
        username = cls.__name__

        client.post(
            reverse("user-list"),
            {
                "email": email,
                "username": username,
                "first_name": "First",
                "last_name": "Second",
                "password": cls.password,
            },
            format="json",
        )
        # Получение токена.
        response = client.post(
            reverse("login"), {"email": email, "password": cls.password}, format="json"
        )
        # Извлечение токена из ответа.
        data = json.loads(response.content)
        cls.token = data.get("auth_token")
        cls.user = User.objects.get(username=username)

    def setUp(self):
        cls = self.__class__
        self.authorized = APIClient()
        self.authorized.credentials(HTTP_AUTHORIZATION="Token " + cls.token)
        self.anonime = APIClient()
        cache.clear()

    def in_or_equ(self, data, name, value=None):

        if value:
            self.assertEqual(data.get(name), value)
        else:
            self.assertIn(name, data)

    def page_paginated(self, data, count=None, next_page=None, prev_page=None):
        """Проверяет что шапка соответствует постраничной пагинации"""
        self.assertIsInstance(data, dict)
        self.in_or_equ(data, "count", count)
        self.in_or_equ(data, "next", next_page)
        self.in_or_equ(data, "previous", prev_page)
        self.assertIn("results", data)
        results = data.get("results")
        self.assertIsInstance(results, list)
        return results

    def is_instance(self, obj, model):
        """Проверяет что объект модели находится в БД"""
        self.assertTrue(model.objects.filter(**obj).exists())

    def is_instances(self, objects, model, count=None):
        """Проверяет что множество объектов модели находиться в БД"""
        self.assertIsInstance(objects, list)
        if count:
            self.assertEqual(len(objects), count)
        last = None
        for obj in objects:
            self.assertNotEqual(last, obj)
            last = obj
            self.is_instance(obj, model)

    def is_tag(self, tag):
        """Проверяет то что объект соответствует тэгу"""
        self.is_instance(tag, Tag)

    def is_tags(self, tags, count=None):
        """Проверяет что множество объектов модели находиться в БД"""
        self.is_instances(objects=tags, model=Tag, count=count)

    def is_ingredient(self, ingredient):
        """Проверяет то что объект соответствует ингредиенту"""
        self.is_instance(obj=ingredient, model=Ingredient)

    def is_ingredient_amount(self, ingredient, recipe_id):
        """
        Проверяет то что объект представляет собой смесь ингредиента и его
        количества.
        """

        ingr = Ingredient.objects.get(
            pk=ingredient.get("id"),
            name=ingredient.get("name"),
            measurement_unit=ingredient.get("measurement_unit"),
        )
        self.assertTrue(
            Amount.objects.filter(
                amount=ingredient.get("amount"), ingredient=ingr, recipe_id=recipe_id
            ).exists()
        )

    def is_ingredients(self, ingredients, count=None):
        """
        Проверяет что множество объектов модели ингредиенты находиться в БД
        """
        self.is_instances(objects=ingredients, model=Ingredient, count=count)

    def is_ingredients_amount(self, ingredients, recipe_id, count=None):
        """
        Проверяет что множество смешанных объектов моделей ингредиенты и
        количество ингредиентов находиться в БД
        """
        self.assertIsInstance(ingredients, list)
        if count:
            self.assertEqual(len(ingredients), count)
        last = None
        for ingredient in ingredients:
            self.assertNotEqual(last, ingredient)
            last = ingredient
            self.is_ingredient_amount(ingredient, recipe_id)

    def is_user(self, user, is_subscribed=None):
        """Проверяет то что объект соответствует пользователю"""
        if is_subscribed is None:
            user.pop("is_subscribed", None)
        else:
            self.assertEqual(user.pop("is_subscribed", None), is_subscribed)
        self.is_instance(obj=user, model=User)

    def is_users(self, users, is_subscribed=None, count=None):
        """
        Проверяет что множество объектов модели пользователи находиться в БД
        """
        self.assertIsInstance(users, list)
        if count:
            self.assertEqual(len(users), count)
        last = None
        for user in users:
            self.assertNotEqual(last, user)
            last = user
            self.is_user(user, is_subscribed)

    def is_recipes(self, recipes, count=None, limit=6):
        """
        Проверяет что множество объектов модели рецепты с вложенными объектами
        типа тэги и ингредиенты находиться в БД
        """
        self.assertIsInstance(recipes, list)
        if count:
            self.assertEqual(len(recipes), min(count, limit))
        last = None
        for recipe in recipes:
            self.assertNotEqual(last, recipe)
            last = recipe
            self.is_recipe(recipe)

    def is_recipe(self, recipe):
        """
        Проверяет то что объект соответствует рецепту с вложенными объектами
        типа тэги и ингредиенты
        """
        self.assertIsInstance(recipe, dict)
        recipe_id = recipe.get("id")

        tags = recipe.pop("tags", None)
        tags_count = TagRecipe.objects.filter(recipe_id=recipe_id).count()
        self.is_tags(tags, count=tags_count)

        author = recipe.pop("author", None)
        self.is_user(author)

        ingredients = recipe.pop("ingredients", None)
        amount_count = Amount.objects.filter(recipe_id=recipe_id).count()
        self.is_ingredients_amount(ingredients, recipe_id=recipe_id, count=amount_count)

        self.assertIsNotNone(recipe.pop("is_favorited", None))
        self.assertIsNotNone(recipe.pop("is_in_shopping_cart", None))

        self.assertIn("image", recipe)
        self.assertTrue(
            Recipe.objects.filter(
                pk=recipe.get("id"),
                name=recipe.get("name"),
                text=recipe.get("text"),
                cooking_time=recipe.get("cooking_time"),
            ).exists()
        )


class EndpointsTestCase(TestCase):
    def reverse(self, url_basename, kwargs=None):
        return reverse(url_basename, kwargs=kwargs).strip("/")

    def test_url_basenames(self):
        """Проверяет наличие всех эндпоинтов, соответствия именам."""
        urls_basename = (
            # users endpoints
            ("user-subscriptions", "api/users/subscriptions", None),
            ("user-subscribe", "api/users/1/subscribe", {"id": 1}),
            # tags endpoints
            ("tag-list", "api/tags", None),
            ("tag-detail", "api/tags/1", {"id": 1}),
            # recipes endpoints
            ("recipe-list", "api/recipes", None),
            ("recipe-detail", "api/recipes/1", {"id": 1}),
            (
                "recipe-download-shopping-cart",
                "api/recipes/download_shopping_cart",
                None,
            ),
            ("recipe-shopping-cart", "api/recipes/1/shopping_cart", {"id": 1}),
            ("recipe-favorite", "api/recipes/1/favorite", {"id": 1}),
            # ingredients endpoints
            ("ingredient-list", "api/ingredients", None),
            ("ingredient-detail", "api/ingredients/1", {"id": 1}),
        )

        for name, url, kwargs in urls_basename:
            url_reversed = self.reverse(name, kwargs=kwargs)
            with self.subTest(url=url, url_reversed=url_reversed):
                self.assertEqual(url_reversed, url)


class TagsTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tags = (
            {"id": 1, "name": "Завтрак", "color": "#FF0000", "slug": "zavtrak"},
            {"id": 2, "name": "Обед", "color": "#00FF00", "slug": "obed"},
            {"id": 3, "name": "Ужин", "color": "#0000FF", "slug": "uzhin"},
        )
        for tag in cls.tags:
            Tag.objects.create(**tag)

    def test_tags_list(self):
        """Проверяет получение списка тегов без авторизации"""
        url = reverse("tag-list")
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        count = Tag.objects.count()
        self.is_tags(data, count)

    def test_tags_id(self):
        """Проверяет получение тега по id без авторизации"""
        url = reverse("tag-detail", kwargs={"id": 2})
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.is_tag(data)
        self.assertEqual(data.get("id", None), 2)

    def test_tags_wrong_id(self):
        """Проверяет получение не верного тега по id без авторизации"""
        url = reverse("tag-detail", kwargs={"id": 200})
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        data = json.loads(response.content)
        self.assertEqual(data, {"detail": "Страница не найдена."})


class IngredientsTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ingredients = (
            {"id": 0, "name": "Абрикос", "measurement_unit": "кг"},
            {"id": 1, "name": "Капуста", "measurement_unit": "кг"},
            {"id": 2, "name": "Кактус", "measurement_unit": "кг"},
            {"id": 3, "name": "Качан", "measurement_unit": "кг"},
            {"id": 4, "name": "Карп", "measurement_unit": "кг"},
            {"id": 5, "name": "Палтус", "measurement_unit": "кг"},
            {"id": 6, "name": "Тусовка опят", "measurement_unit": "кг"},
            {"id": 7, "name": "яблоки", "measurement_unit": "кг"},
            {"id": 8, "name": "Картон", "measurement_unit": "кг"},
            {"id": 9, "name": "Лимон", "measurement_unit": "кг"},
        )
        for ingredient in cls.ingredients:
            Ingredient.objects.create(**ingredient)

    def test_ingredients_list(self):
        """Проверяет получение списка ингредиентов без авторизации"""
        url = reverse("ingredient-list")
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        count = Ingredient.objects.count()
        self.is_ingredients(data, count)

    def test_ingredients_id(self):
        """Проверяет получение ингредиента по id без авторизации"""
        url = reverse("ingredient-detail", kwargs={"id": 2})
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.is_ingredient(data)
        self.assertEqual(data.pop("id", None), 2)

    def test_ingredients_wrong_id(self):
        """Проверяет получение не верного ингредиента по id без авторизации"""
        url = reverse("ingredient-detail", kwargs={"id": 200})
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_ingredient_seach_by_name_part(self):
        """Проверяет получение списка ингредиентов по фрагменту имени."""
        url = reverse("ingredient-list")
        response = self.anonime.get(url, data={"name": "тус"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)


class UsersTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.users = (
            {
                "username": "user_subscribe",
                "email": "test@mail.ru",
                "first_name": "user_first_name",
                "last_name": "user_last_name",
            },
            {
                "username": "user_1",
                "email": "test_1@mail.ru",
                "first_name": "user_1_first_name",
                "last_name": "user_1_last_name",
            },
            {
                "username": "user_2",
                "email": "test_2@mail.ru",
                "first_name": "user_2_first_name",
                "last_name": "user_2_last_name",
            },
            {
                "username": "user_not_subscribe",
                "email": "test_3@mail.ru",
                "first_name": "user_3_first_name",
                "last_name": "user_3_last_name",
            },
        )
        cls.user0 = User.objects.create(
            **cls.users[0], password="password_lkgdoi32dgu7e6", is_active=True
        )
        user1 = User.objects.create(
            **cls.users[1], password="password_lkxznvcdsf7e94", is_active=True
        )
        user2 = User.objects.create(
            **cls.users[2], password="password_nvreiuhfglkdsn", is_active=True
        )

        image = None

        cls.recipes = (
            {
                "image": image,
                "author": user1,
                "name": "Рецепт 1",
                "text": "Рецепт 1",
                "cooking_time": 1,
            },
            {
                "image": image,
                "name": "Рецепт 2",
                "author": user1,
                "text": "Рецепт 2",
                "cooking_time": 2,
            },
            {
                "image": image,
                "name": "Рецепт 3",
                "author": user1,
                "text": "Рецепт 3",
                "cooking_time": 3,
            },
            {
                "image": image,
                "name": "Рецепт 4",
                "author": user1,
                "text": "Рецепт 4",
                "cooking_time": 4,
            },
            {
                "image": image,
                "name": "Рецепт 5",
                "author": user1,
                "text": "Рецепт 5",
                "cooking_time": 5,
            },
            {
                "image": image,
                "name": "Рецепт 6",
                "author": user1,
                "text": "Рецепт 6",
                "cooking_time": 6,
            },
            {
                "image": image,
                "author": user1,
                "name": "Рецепт 7",
                "text": "Рецепт 7",
                "cooking_time": 7,
            },
        )
        for recipe in cls.recipes:
            Recipe.objects.create(**recipe)

        cls.follows = (
            {
                "user": cls.user0,
                "author": user1,
            },
            {
                "user": cls.user0,
                "author": user2,
            },
            {
                "user": cls.user,
                "author": user1,
            },
            {
                "user": cls.user,
                "author": user2,
            },
        )
        for follow in cls.follows:
            Follow.objects.create(**follow)

    def test_users_subscriptions_list_anonime(self):
        """
        Проверяет возможность получить списка подписок анонимным пользователем.
        """
        url = reverse("user-subscriptions")
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def data_user_subscribe(self, data):
        """
        Проверяет данные подписанного пользователя
        """
        recipes_count = data.pop("recipes_count")
        self.assertTrue(data.pop("is_subscribed"))
        recipes = data.pop("recipes")
        self.assertIsInstance(recipes, list)
        user = User.objects.filter(**data).get()
        self.assertEqual(user.recipes.count(), recipes_count)
        for recipe in recipes:
            with self.subTest(recipe=recipe):
                self.assertIsInstance(recipe, dict)
                recipe.pop("image")
                self.assertTrue(Recipe.objects.filter(**recipe).exists())

    def test_users_subscriptions_list(self):
        """Проверяет список подписок пользователея."""
        url = reverse("user-subscriptions")
        response = self.authorized.get(
            url, data={"page": 1, "limit": 2, "recipes_limit": 4}
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
        count = Follow.objects.count()
        self.assertIn("count", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)
        results = data.get("results")
        self.assertIsInstance(results, list)
        showed = 2 if count >= 4 else 0 if count <= 2 else count - 2
        self.assertEqual(len(results), showed)
        for result in results:
            with self.subTest(result=result):
                self.data_user_subscribe(result)

    def test_users_subscribe_unsubscribe(self):
        """Проверяет возможность пользователя подписаться и отписаться."""
        count = Follow.objects.filter(user=self.__class__.user).count()
        user = User.objects.get(username="user_subscribe")
        url = reverse("user-subscribe", kwargs={"id": user.pk})
        response = self.authorized.post(url)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        new_count = Follow.objects.filter(user=self.__class__.user).count()
        self.assertEqual(count + 1, new_count)
        self.data_user_subscribe(json.loads(response.content))
        response = self.authorized.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_users_subscribe_anonime(self):
        """
        Проверяет возможность анонимного пользователя подписаться и отписаться.
        """
        count = Follow.objects.filter(user=self.__class__.user).count()
        user = User.objects.get(username="user_subscribe")
        url = reverse("user-subscribe", kwargs={"id": user.pk})
        response = self.anonime.post(url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        new_count = Follow.objects.filter(user=self.__class__.user).count()
        self.assertEqual(count, new_count)

    def test_users_unsubscribe_anonime(self):
        """
        Проверяет блокировку отписки анонимным пользователем.
        """
        count = Follow.objects.filter(user=self.__class__.user).count()
        user = User.objects.get(username="user_subscribe")
        url = reverse("user-subscribe", kwargs={"id": user.pk})
        response = self.anonime.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
        new_count = Follow.objects.filter(user=self.__class__.user).count()
        self.assertEqual(count, new_count)

    def test_users_subscribe_user_not_exist(self):
        """Проверяет подписку на не существующего пользователя."""
        wrong_id = User.objects.order_by("pk").last().pk + 1
        url = reverse("user-subscribe", kwargs={"id": wrong_id})
        response = self.authorized.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_users_unsubscribe_user_not_exist(self):
        """Проверяет отписку от не существующего пользователя."""
        wrong_id = User.objects.order_by("pk").last().pk + 1
        url = reverse("user-subscribe", kwargs={"id": wrong_id})
        response = self.authorized.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_users_subscribe_wrong_user(self):
        """Проверяет блокировку подписки на самого себя."""
        url = reverse("user-subscribe", kwargs={"id": self.__class__.user.pk})
        response = self.authorized.post(url)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("errors", json.loads(response.content))

    def test_users_unsubscribe_wrong_user(self):
        """
        Проверяет блокировку отписки от пользователя на которого не подписан.
        """
        unsubscribed_user = User.objects.create(
            username="user_not_subscribe",
            email="test_3@mail.ru",
            first_name="user_3_first_name",
            last_name="user_3_last_name",
            password="cbndskfdhkdsjfnu7",
            is_active=True,
        )
        url = reverse("user-subscribe", kwargs={"id": unsubscribed_user.pk})
        response = self.authorized.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("errors", json.loads(response.content))


class RecipeTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.users = (
            {
                "username": "user_subscribe",
                "email": "test@mail.ru",
                "first_name": "user_first_name",
                "last_name": "user_last_name",
            },
            {
                "username": "user_1",
                "email": "test_1@mail.ru",
                "first_name": "user_1_first_name",
                "last_name": "user_1_last_name",
            },
            {
                "username": "user_2",
                "email": "test_2@mail.ru",
                "first_name": "user_2_first_name",
                "last_name": "user_2_last_name",
            },
            {
                "username": "user_not_subscribe",
                "email": "test_3@mail.ru",
                "first_name": "user_3_first_name",
                "last_name": "user_3_last_name",
            },
        )
        cls.user0 = User.objects.create(
            **cls.users[0], password="password_lkgdoi32dgu7e6", is_active=True
        )
        user1 = User.objects.create(
            **cls.users[1], password="password_lkxznvcdsf7e94", is_active=True
        )
        User.objects.create(
            **cls.users[2], password="password_nvreiuhfglkdsn", is_active=True
        )

        for recipe in range(1, 8):
            Recipe.objects.create(
                image=None,
                author=user1,
                name=f"Рецепт {recipe}",
                text=f"Рецепт {recipe}",
                cooking_time=recipe,
            )
        for recipe in range(8, 17):
            Recipe.objects.create(
                image=None,
                author=cls.user,
                name=f"Рецепт {recipe}",
                text=f"Рецепт {recipe}",
                cooking_time=recipe,
            )

        cls.tags = (
            {"id": 1, "name": "Завтрак", "color": "#FF0000", "slug": "zavtrak"},
            {"id": 2, "name": "Обед", "color": "#00FF00", "slug": "obed"},
            {"id": 3, "name": "Ужин", "color": "#0000FF", "slug": "uzhin"},
        )
        for tag in cls.tags:
            Tag.objects.create(**tag)

        cls.ingredients = (
            "Абрикос",
            "Капуста",
            "Кактус",
            "Качан",
            "Карп",
            "Палтус",
            "Тусовка опят",
            "яблоки",
            "Картон",
            "Лимон",
        )
        for ingredient in cls.ingredients:
            Ingredient.objects.create(
                name=ingredient, measurement_unit=choice(("кг", "г", "шт"))
            )

        all_tags = Tag.objects.all()
        all_recipes = Recipe.objects.all()
        all_ingredients = Ingredient.objects.all()

        for recipe in all_recipes:
            for tag in set(choices(all_tags, k=randint(1, len(all_tags)))):
                TagRecipe.objects.create(tag=tag, recipe=recipe)
            for ingredient in set(
                choices(all_ingredients, k=randint(1, len(all_ingredients)))
            ):
                Amount.objects.create(
                    ingredient=ingredient, recipe=recipe, amount=randint(1, 10)
                )

        for recipe in set(choices(all_recipes, k=randint(1, len(all_recipes)))):
            Favorite.objects.create(recipe=recipe, user=cls.user)
            Trolley.objects.create(recipe=recipe, user=cls.user)

        for recipe in set(choices(all_recipes, k=randint(1, len(all_recipes)))):
            Favorite.objects.create(recipe=recipe, user=cls.user0)
            Trolley.objects.create(recipe=recipe, user=cls.user0)

    def test_receipes_list(self):
        """Проверяет получение списка рецептов."""
        url = reverse("recipe-list")
        response = self.anonime.get(url)
        data = json.loads(response.content)
        count = Recipe.objects.count()
        result = self.page_paginated(data, count=count)
        self.is_recipes(result, count=count)

    def test_recipes_filter(self):
        """Проверяет получение списка рецептов с применением фильтров."""

        def slug_in_tags(objects, slugs):
            for tag in objects:
                if tag.get("slug") in slugs:
                    return True
            return False

        all_recipes = Recipe.objects.all()
        cls = self.__class__
        url = reverse("recipe-list")

        for recipe in all_recipes:
            tags = tuple(
                tag.tag.slug
                for tag in TagRecipe.objects.filter(recipe=recipe).all()[:2]
            )
            is_favorite = (
                1
                if Favorite.objects.filter(recipe=recipe, user=cls.user).exists()
                else 0
            )
            is_in_shopping_cart = (
                1
                if Trolley.objects.filter(recipe=recipe, user=cls.user).exists()
                else 0
            )
            author_pk = recipe.author.pk

            response = self.authorized.get(
                url,
                data={
                    "tags": tags,
                    "is_favorited": is_favorite,
                    "is_in_shopping_cart": is_in_shopping_cart,
                    "author": author_pk,
                },
            )
            self.assertEqual(response.status_code, HTTPStatus.OK)
            data = json.loads(response.content)
            result = self.page_paginated(data)
            for record in result:
                with self.subTest(record=record):
                    rec_tags = record.get("tags")
                    self.assertIsInstance(rec_tags, list)
                    self.assertTrue(slug_in_tags(rec_tags, tags))
                    self.assertEqual(record.get("is_favorited"), is_favorite)
                    self.assertEqual(
                        record.get("is_in_shopping_cart"), is_in_shopping_cart
                    )

    def test_receipes_list_with_paginations(self):
        """Проверяет получение списка рецептов с пагинацией."""
        url = reverse("recipe-list")
        count = Recipe.objects.count()
        limit = count - 3
        response = self.anonime.get(url, data={"page": 2, "limit": limit})
        data = json.loads(response.content)
        result = self.page_paginated(data, count=count)
        self.is_recipes(result, count=3, limit=limit)

    def test_receipes_detail(self):
        """Проверяет возможность получить данные рецепта."""
        url = reverse("recipe-detail", kwargs={"id": 1})
        response = self.anonime.get(url)
        data = json.loads(response.content)
        self.is_recipe(data)
        self.assertEqual(data.get("id"), 1)

    def test_receipes_create(self):
        """Проверяет возможность создать рецепт."""
        url = reverse("recipe-list")
        ingredient = Ingredient.objects.first()
        tag = Tag.objects.first()
        response = self.authorized.post(
            url,
            data={
                "ingredients": (
                    {
                        "id": ingredient.pk,
                        "name": ingredient.name,
                        "measurement_unit": ingredient.measurement_unit,
                        "amount": 50,
                    },
                ),
                "tags": (tag.pk,),
                "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAA"
                "AUCAIAAAAC64paAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQ"
                "UAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAADnSURBVDhPnZFNCsIwEI"
                "U9iEvvoUsv5MpbuHDnRnDhUtEjCMWfnbjwAP6BUEGEUExMmTR9mf"
                "wUfDzKZOZ97YS2VFJCfLv9fdCz+bWExXL1GY0pzZRtc8agS1iTz3"
                "aHTAxpd3ixNHO9tuXpFVIqG+oBgHZgLBK3tY7CRSFZlHmT5dG1tR"
                "brBwPQOhD+MtW3u9D/gzHWOhCASXg8nt6D4RnJyfSi++G1yWYQVw"
                "3/oWY4sYID+7n0/vzO5lAJO37AwDESm37GgdnMP7JODdMTx6zGI8"
                "mBsdAiAG0GlfjawRDJ7xuY1Ag7I6V+eFybE9tlqTkAAAAASUVORK"
                "5CYII==",
                "name": "Добавленный рецепт 1",
                "text": "Добавленный рецепт 1",
                "cooking_time": 120,
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTPStatus.CREATED)

        data = json.loads(response.content)

        last_recipe = Recipe.objects.order_by("-pk").first()
        self.assertEqual(data.get("id"), last_recipe.pk)

        self.assertIn("tags", data)
        tags = data.get("tags")
        self.assertIsInstance(tags, list)
        self.assertEqual(tags[0].get("id"), tag.pk)

        self.assertIn("ingredients", data)
        ingredients = data.get("ingredients")
        self.assertIsInstance(ingredients, list)
        self.assertEqual(ingredients[0].get("id"), ingredient.pk)

    def test_receipes_create_validation_error(self):
        """Проверяет блокирование создания рецепта с некорректными данными."""
        url = reverse("recipe-list")
        ingredient = Ingredient.objects.first()
        tag = Tag.objects.first()
        response = self.authorized.post(
            url,
            data={
                "ingredients": (
                    {
                        "id": ingredient.pk,
                        "name": ingredient.name,
                        "measurement_unit": ingredient.measurement_unit,
                        "amount": 0,
                    },
                ),
                "tags": (tag.pk,),
                "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAA"
                "AUCAIAAAAC64paAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQ"
                "UAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAADnSURBVDhPnZFNCsIwEI"
                "U9iEvvoUsv5MpbuHDnRnDhUtEjCMWfnbjwAP6BUEGEUExMmTR9mf"
                "wUfDzKZOZ97YS2VFJCfLv9fdCz+bWExXL1GY0pzZRtc8agS1iTz3"
                "aHTAxpd3ixNHO9tuXpFVIqG+oBgHZgLBK3tY7CRSFZlHmT5dG1tR"
                "brBwPQOhD+MtW3u9D/gzHWOhCASXg8nt6D4RnJyfSi++G1yWYQVw"
                "3/oWY4sYID+7n0/vzO5lAJO37AwDESm37GgdnMP7JODdMTx6zGI8"
                "mBsdAiAG0GlfjawRDJ7xuY1Ag7I6V+eFybE9tlqTkAAAAASUVORK"
                "5CYII==",
                "name": "Добавленный рецепт 2",
                "text": "Добавленный рецепт 2",
                "cooking_time": 120,
            },
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_receipes_create_anonime(self):
        """
        Проверка блокировки попытки создать рецепт неавторизованным
        пользователем.
        """
        url = reverse("recipe-list")
        ingredient = Ingredient.objects.first()
        tag = Tag.objects.first()
        response = self.anonime.post(
            url,
            data={
                "ingredients": (
                    {
                        "id": ingredient.pk,
                        "name": ingredient.name,
                        "measurement_unit": ingredient.measurement_unit,
                        "amount": 0,
                    },
                ),
                "tags": (tag.pk,),
                "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAA"
                "AUCAIAAAAC64paAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQ"
                "UAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAADnSURBVDhPnZFNCsIwEI"
                "U9iEvvoUsv5MpbuHDnRnDhUtEjCMWfnbjwAP6BUEGEUExMmTR9mf"
                "wUfDzKZOZ97YS2VFJCfLv9fdCz+bWExXL1GY0pzZRtc8agS1iTz3"
                "aHTAxpd3ixNHO9tuXpFVIqG+oBgHZgLBK3tY7CRSFZlHmT5dG1tR"
                "brBwPQOhD+MtW3u9D/gzHWOhCASXg8nt6D4RnJyfSi++G1yWYQVw"
                "3/oWY4sYID+7n0/vzO5lAJO37AwDESm37GgdnMP7JODdMTx6zGI8"
                "mBsdAiAG0GlfjawRDJ7xuY1Ag7I6V+eFybE9tlqTkAAAAASUVORK"
                "5CYII==",
                "name": "Добавленный рецепт 2",
                "text": "Добавленный рецепт 2",
                "cooking_time": 120,
            },
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_receipes_create_wrong_id(self):
        """
        Проверяет блокирование создания рецепта с не существующим
        ингредиентом.
        """
        url = reverse("recipe-list")
        ingredient = Ingredient.objects.order_by("pk").last()
        tag = Tag.objects.first()
        response = self.authorized.post(
            url,
            data={
                "ingredients": (
                    {
                        "id": ingredient.pk + 1,
                        "name": ingredient.name,
                        "measurement_unit": ingredient.measurement_unit,
                        "amount": 10,
                    },
                ),
                "tags": (tag.pk,),
                "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAA"
                "AUCAIAAAAC64paAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQ"
                "UAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAADnSURBVDhPnZFNCsIwEI"
                "U9iEvvoUsv5MpbuHDnRnDhUtEjCMWfnbjwAP6BUEGEUExMmTR9mf"
                "wUfDzKZOZ97YS2VFJCfLv9fdCz+bWExXL1GY0pzZRtc8agS1iTz3"
                "aHTAxpd3ixNHO9tuXpFVIqG+oBgHZgLBK3tY7CRSFZlHmT5dG1tR"
                "brBwPQOhD+MtW3u9D/gzHWOhCASXg8nt6D4RnJyfSi++G1yWYQVw"
                "3/oWY4sYID+7n0/vzO5lAJO37AwDESm37GgdnMP7JODdMTx6zGI8"
                "mBsdAiAG0GlfjawRDJ7xuY1Ag7I6V+eFybE9tlqTkAAAAASUVORK"
                "5CYII==",
                "name": "Добавленный рецепт 4",
                "text": "Добавленный рецепт 4",
                "cooking_time": 120,
            },
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_receipes_patch(self):
        """Проверяет возможность изменения рецепта."""
        recipe = Recipe.objects.create(
            image=None,
            author=self.__class__.user,
            name="Рецепт для изменения",
            text="Рецепт для изменения",
            cooking_time=1,
        )
        url = reverse("recipe-detail", kwargs={"id": recipe.pk})
        ingredient = Ingredient.objects.first()
        tag = Tag.objects.first()
        response = self.authorized.patch(
            url,
            data={
                "ingredients": (
                    {
                        "id": ingredient.pk,
                        "name": ingredient.name,
                        "measurement_unit": ingredient.measurement_unit,
                        "amount": 50,
                    },
                ),
                "tags": (tag.pk,),
                "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAA"
                "AUCAIAAAAC64paAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQ"
                "UAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAADnSURBVDhPnZFNCsIwEI"
                "U9iEvvoUsv5MpbuHDnRnDhUtEjCMWfnbjwAP6BUEGEUExMmTR9mf"
                "wUfDzKZOZ97YS2VFJCfLv9fdCz+bWExXL1GY0pzZRtc8agS1iTz3"
                "aHTAxpd3ixNHO9tuXpFVIqG+oBgHZgLBK3tY7CRSFZlHmT5dG1tR"
                "brBwPQOhD+MtW3u9D/gzHWOhCASXg8nt6D4RnJyfSi++G1yWYQVw"
                "3/oWY4sYID+7n0/vzO5lAJO37AwDESm37GgdnMP7JODdMTx6zGI8"
                "mBsdAiAG0GlfjawRDJ7xuY1Ag7I6V+eFybE9tlqTkAAAAASUVORK"
                "5CYII==",
                "name": "Добавленный для изменений 2",
                "text": "Добавленный для изменений 2",
                "cooking_time": 120,
            },
            format="json",
        )

        data = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertEqual(data.get("id"), recipe.pk)

        changed_recipe = Recipe.objects.get(pk=recipe.pk)
        self.assertNotEqual(changed_recipe.name, recipe.name)

        self.assertIn("tags", data)
        tags = data.get("tags")
        self.assertIsInstance(tags, list)
        self.assertEqual(tags[0].get("id"), tag.pk)

        self.assertIn("ingredients", data)
        ingredients = data.get("ingredients")
        self.assertIsInstance(ingredients, list)
        self.assertEqual(ingredients[0].get("id"), ingredient.pk)

    def test_receipes_patch_multitest(self):
        """Проверяет возможность изменения рецептов в случайном порядке."""
        recipes = Recipe.objects.filter(author=self.__class__.user)

        ingredients = Ingredient.objects.all()
        ingr_count = Ingredient.objects.count()

        tags = Tag.objects.all()
        tags_count = Tag.objects.count()

        for recipe in recipes:
            with self.subTest(recipes=recipes):
                url = reverse("recipe-detail", kwargs={"id": recipe.pk})
                ctime = time()
                data = {
                    "ingredients": (
                        *(
                            {
                                "id": ingr.pk,
                                "name": ingr.name,
                                "measurement_unit": ingr.measurement_unit,
                                "amount": 50,
                            }
                            for ingr in set(
                                choices(ingredients, k=randint(1, ingr_count))
                            )
                        ),
                    ),
                    "tags": (
                        *(
                            tag.pk
                            for tag in set(choices(tags, k=randint(1, tags_count)))
                        ),
                    ),
                    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB"
                    "QAAAAUCAIAAAAC64paAAAAAXNSR0IArs4c6QAAAARnQU1BAA"
                    "Cxjwv8YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAADnSURBVD"
                    "hPnZFNCsIwEIU9iEvvoUsv5MpbuHDnRnDhUtEjCMWfnbjwAP"
                    "6BUEGEUExMmTR9mfwUfDzKZOZ97YS2VFJCfLv9fdCz+bWExX"
                    "L1GY0pzZRtc8agS1iTz3aHTAxpd3ixNHO9tuXpFVIqG+oBgH"
                    "ZgLBK3tY7CRSFZlHmT5dG1tRbrBwPQOhD+MtW3u9D/gzHWOh"
                    "CASXg8nt6D4RnJyfSi++G1yWYQVw3/oWY4sYID+7n0/vzO5l"
                    "AJO37AwDESm37GgdnMP7JODdMTx6zGI8mBsdAiAG0GlfjawR"
                    "DJ7xuY1Ag7I6V+eFybE9tlqTkAAAAASUVORK5CYII==",
                    "name": f"Изменён {ctime}",
                    "text": f"Изменён {ctime}",
                    "cooking_time": randint(1, 0xFFFF),
                }
                response = self.authorized.patch(url, data=data, format="json")
                json_data = json.loads(response.content)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertEqual(json_data.get("id"), recipe.pk)
                changed_recipe = Recipe.objects.get(pk=recipe.pk)
                self.assertNotEqual(changed_recipe.name, recipe.name)

    def test_receipes_patch_wrong_user(self):
        """Проверяет блокировку изменения чужого рецепта."""
        recipe = Recipe.objects.create(
            image=None,
            author=self.__class__.user0,
            name="Рецепт для изменения без прав",
            text="Рецепт для изменения без прав",
            cooking_time=1,
        )
        url = reverse("recipe-detail", kwargs={"id": recipe.pk})
        ingredient = Ingredient.objects.first()
        tag = Tag.objects.first()
        response = self.authorized.patch(
            url,
            data={
                "ingredients": (
                    {
                        "id": ingredient.pk,
                        "name": ingredient.name,
                        "measurement_unit": ingredient.measurement_unit,
                        "amount": 50,
                    },
                ),
                "tags": (tag.pk,),
                "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAA"
                "AUCAIAAAAC64paAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQ"
                "UAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAADnSURBVDhPnZFNCsIwEI"
                "U9iEvvoUsv5MpbuHDnRnDhUtEjCMWfnbjwAP6BUEGEUExMmTR9mf"
                "wUfDzKZOZ97YS2VFJCfLv9fdCz+bWExXL1GY0pzZRtc8agS1iTz3"
                "aHTAxpd3ixNHO9tuXpFVIqG+oBgHZgLBK3tY7CRSFZlHmT5dG1tR"
                "brBwPQOhD+MtW3u9D/gzHWOhCASXg8nt6D4RnJyfSi++G1yWYQVw"
                "3/oWY4sYID+7n0/vzO5lAJO37AwDESm37GgdnMP7JODdMTx6zGI8"
                "mBsdAiAG0GlfjawRDJ7xuY1Ag7I6V+eFybE9tlqTkAAAAASUVORK"
                "5CYII==",
                "name": "Добавленный для изменений 3",
                "text": "Добавленный для изменений 3",
                "cooking_time": 120,
            },
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_receipes_patch_validation_error(self):
        """Проверяет блокировку изменения рецепта с неверными данными."""
        recipe = Recipe.objects.create(
            image=None,
            author=self.__class__.user,
            name="Рецепт для попытки изменения",
            text="Рецепт для попытки изменения",
            cooking_time=1,
        )
        url = reverse("recipe-detail", kwargs={"id": recipe.pk})
        ingredient = Ingredient.objects.first()
        tag = Tag.objects.first()
        response = self.authorized.patch(
            url,
            data={
                "ingredients": (
                    {
                        "id": ingredient.pk,
                        "name": ingredient.name,
                        "measurement_unit": ingredient.measurement_unit,
                        "amount": 0,
                    },
                ),
                "tags": (tag.pk,),
                "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAA"
                "AUCAIAAAAC64paAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQ"
                "UAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAADnSURBVDhPnZFNCsIwEI"
                "U9iEvvoUsv5MpbuHDnRnDhUtEjCMWfnbjwAP6BUEGEUExMmTR9mf"
                "wUfDzKZOZ97YS2VFJCfLv9fdCz+bWExXL1GY0pzZRtc8agS1iTz3"
                "aHTAxpd3ixNHO9tuXpFVIqG+oBgHZgLBK3tY7CRSFZlHmT5dG1tR"
                "brBwPQOhD+MtW3u9D/gzHWOhCASXg8nt6D4RnJyfSi++G1yWYQVw"
                "3/oWY4sYID+7n0/vzO5lAJO37AwDESm37GgdnMP7JODdMTx6zGI8"
                "mBsdAiAG0GlfjawRDJ7xuY1Ag7I6V+eFybE9tlqTkAAAAASUVORK"
                "5CYII==",
                "name": "Добавленный для изменений 4",
                "text": "Добавленный для изменений 4",
                "cooking_time": 120,
            },
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_receipes_patch_anonime(self):
        """Проверяет блокировку изменения рецепта анонимным пользователем."""
        recipe = Recipe.objects.create(
            image=None,
            author=self.__class__.user,
            name="Изменения не авторизованным пользователем",
            text="Изменения не авторизованным пользователем",
            cooking_time=1,
        )
        url = reverse("recipe-detail", kwargs={"id": recipe.pk})
        ingredient = Ingredient.objects.first()
        tag = Tag.objects.first()
        response = self.anonime.patch(
            url,
            data={
                "ingredients": (
                    {
                        "id": ingredient.pk,
                        "name": ingredient.name,
                        "measurement_unit": ingredient.measurement_unit,
                        "amount": 50,
                    },
                ),
                "tags": (tag.pk,),
                "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAA"
                "AUCAIAAAAC64paAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQ"
                "UAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAADnSURBVDhPnZFNCsIwEI"
                "U9iEvvoUsv5MpbuHDnRnDhUtEjCMWfnbjwAP6BUEGEUExMmTR9mf"
                "wUfDzKZOZ97YS2VFJCfLv9fdCz+bWExXL1GY0pzZRtc8agS1iTz3"
                "aHTAxpd3ixNHO9tuXpFVIqG+oBgHZgLBK3tY7CRSFZlHmT5dG1tR"
                "brBwPQOhD+MtW3u9D/gzHWOhCASXg8nt6D4RnJyfSi++G1yWYQVw"
                "3/oWY4sYID+7n0/vzO5lAJO37AwDESm37GgdnMP7JODdMTx6zGI8"
                "mBsdAiAG0GlfjawRDJ7xuY1Ag7I6V+eFybE9tlqTkAAAAASUVORK"
                "5CYII==",
                "name": "Добавленный для изменений 5",
                "text": "Добавленный для изменений 5",
                "cooking_time": 120,
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_receipes_patch_wrong_pk(self):
        """Проверяет блокировку изменения рецепта с неверным id."""
        wrong_id = Recipe.objects.order_by("pk").last().id + 1
        url = reverse("recipe-detail", kwargs={"id": wrong_id})
        ingredient = Ingredient.objects.first()
        tag = Tag.objects.first()
        response = self.authorized.patch(
            url,
            data={
                "ingredients": (
                    {
                        "id": ingredient.pk,
                        "name": ingredient.name,
                        "measurement_unit": ingredient.measurement_unit,
                        "amount": 50,
                    },
                ),
                "tags": (tag.pk,),
                "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAA"
                "AUCAIAAAAC64paAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQ"
                "UAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAADnSURBVDhPnZFNCsIwEI"
                "U9iEvvoUsv5MpbuHDnRnDhUtEjCMWfnbjwAP6BUEGEUExMmTR9mf"
                "wUfDzKZOZ97YS2VFJCfLv9fdCz+bWExXL1GY0pzZRtc8agS1iTz3"
                "aHTAxpd3ixNHO9tuXpFVIqG+oBgHZgLBK3tY7CRSFZlHmT5dG1tR"
                "brBwPQOhD+MtW3u9D/gzHWOhCASXg8nt6D4RnJyfSi++G1yWYQVw"
                "3/oWY4sYID+7n0/vzO5lAJO37AwDESm37GgdnMP7JODdMTx6zGI8"
                "mBsdAiAG0GlfjawRDJ7xuY1Ag7I6V+eFybE9tlqTkAAAAASUVORK"
                "5CYII==",
                "name": "Добавленный для изменений 6",
                "text": "Добавленный для изменений 6",
                "cooking_time": 120,
            },
            format="json",
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_receipes_delete(self):
        """Проверяет возможность удаления рецепта."""
        recipe = Recipe.objects.create(
            image=None,
            author=self.__class__.user,
            name="Рецепт для удаления",
            text="Рецепт для удавления",
            cooking_time=1,
        )
        url = reverse("recipe-detail", kwargs={"id": recipe.pk})
        response = self.authorized.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(pk=recipe.pk).exists())

    def test_receipes_delete_anonime(self):
        """Проверяет блокировку удаления рецепта анонимным пользователем."""
        recipe = Recipe.objects.create(
            image=None,
            author=self.__class__.user,
            name="Рецепт для удаления анонимно",
            text="Рецепт для удавления анонимно",
            cooking_time=1,
        )
        url = reverse("recipe-detail", kwargs={"id": recipe.pk})
        response = self.anonime.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_receipes_delete_not_mine(self):
        """Проверяет блокировку удаления чужого рецепта."""
        recipe = Recipe.objects.create(
            image=None,
            author=self.__class__.user0,
            name="Рецепт для удаления чужого рецепта",
            text="Рецепт для удавления чужого рецепта",
            cooking_time=1,
        )
        url = reverse("recipe-detail", kwargs={"id": recipe.pk})
        response = self.authorized.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_receipes_delete_wrong_id(self):
        """Проверяет попытку удаления не существующего рецепта."""
        wrong_pk = Recipe.objects.order_by("pk").last().id + 1
        url = reverse("recipe-detail", kwargs={"id": wrong_pk})
        response = self.authorized.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_download_shopping_cart(self):
        """Проверяет доступность страници получения списка покупок."""
        url = reverse("recipe-download-shopping-cart")
        response = self.authorized.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_download_shopping_cart_anonime(self):
        """
        Проверяет блокировку попытки получения списка покупок анонимным
        пользователем.
        """
        url = reverse("recipe-download-shopping-cart")
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_shopping_cart(self):
        """
        Проверяет возможность добавления рецепта в список покупок.
        """
        recipe = Recipe.objects.create(
            image="test.img",
            author=self.__class__.user,
            name="Рецепт для добавления в список покупок",
            text="Рецепт для добавления в список покупок",
            cooking_time=1,
        )
        url = reverse("recipe-shopping-cart", kwargs={"id": recipe.pk})
        response = self.authorized.post(url)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(
            Trolley.objects.filter(
                recipe_id=recipe.pk, user=self.__class__.user
            ).exists()
        )
        data = json.loads(response.content)
        self.assertEqual(data.get("id"), recipe.pk)
        self.assertIsNotNone(data.pop("image", None))
        self.is_instance(data, Recipe)

    def test_shopping_cart_dublicate(self):
        """
        Проверяет блокировку добавления рецепта в список покупок повторно.
        """
        added = Trolley.objects.filter(user=self.__class__.user).last()
        url = reverse("recipe-shopping-cart", kwargs={"id": added.recipe_id})
        response = self.authorized.post(url)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_shopping_cart_anonime(self):
        """
        Проверяет блокировку добавления рецепта в список покупок анонимным
        пользователем.
        """
        url = reverse("recipe-shopping-cart", kwargs={"id": 1})
        response = self.anonime.post(url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_shopping_cart_delete(self):
        """
        Проверяет возможность удаления рецепта из списка покупок.
        """
        recipe = Recipe.objects.create(
            image="test.img",
            author=self.__class__.user,
            name="Рецепт для удаления из списка покупок",
            text="Рецепт для удаления из списка покупок",
            cooking_time=1,
        )
        trol = Trolley.objects.create(recipe_id=recipe.pk, user=self.__class__.user)
        url = reverse("recipe-shopping-cart", kwargs={"id": recipe.pk})
        response = self.authorized.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(Trolley.objects.filter(pk=trol.pk).exists())

    def test_shopping_cart_delete_wrong_id(self):
        """
        Проверяет блокировку возможности удаления рецепта с неверным id.
        """
        wrong_id = Recipe.objects.order_by("pk").last().pk + 1
        url = reverse("recipe-shopping-cart", kwargs={"id": wrong_id})
        response = self.authorized.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_shopping_cart_delete_anonime(self):
        """
        Проверяет блокировку удаления рецепта из списка покупок анонимным
        пользователем.
        """
        url = reverse("recipe-shopping-cart", kwargs={"id": 1})
        response = self.anonime.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_favorite_add(self):
        """
        Проверяет возможность добавления рецепта в список избранных рецептов.
        """
        recipe = Recipe.objects.create(
            image="test.img",
            author=self.__class__.user,
            name="Рецепт для добавления в список избранного",
            text="Рецепт для добавления в список избранного",
            cooking_time=1,
        )
        url = reverse("recipe-favorite", kwargs={"id": recipe.pk})
        response = self.authorized.post(url)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(
            Favorite.objects.filter(
                recipe_id=recipe.pk, user=self.__class__.user
            ).exists()
        )
        data = json.loads(response.content)
        self.assertEqual(data.get("id"), recipe.pk)
        self.assertIsNotNone(data.pop("image", None))
        self.is_instance(data, Recipe)

    def test_favorite_dublicate(self):
        """
        Проверяет блокировку повторного добавления рецепта в список избранных
        рецептов.
        """
        added = Favorite.objects.filter(user=self.__class__.user).last()
        url = reverse("recipe-favorite", kwargs={"id": added.recipe_id})
        response = self.authorized.post(url)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_favorite_anonime(self):
        """
        Проверяет блокировку добавления рецепта в список избранных рецептов
        анонимным пользователем.
        """
        url = reverse("recipe-favorite", kwargs={"id": 1})
        response = self.anonime.post(url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_favorite_delete(self):
        """
        Проверяет возможность удаления рецепта из списка избранных рецептов.
        """
        recipe = Recipe.objects.create(
            image="test.img",
            author=self.__class__.user,
            name="Рецепт для удаления из списка избранных 2",
            text="Рецепт для удаления из списка избранных 2",
            cooking_time=1,
        )
        favorite = Favorite.objects.create(
            recipe_id=recipe.pk, user=self.__class__.user
        )
        url = reverse("recipe-favorite", kwargs={"id": recipe.pk})
        response = self.authorized.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertFalse(Favorite.objects.filter(pk=favorite.pk).exists())
