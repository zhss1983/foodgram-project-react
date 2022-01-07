import json
from http import HTTPStatus
from os import path
from shutil import rmtree
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Recipe, Tag, Follow, Favorite, Trolley, TagRecipe, Amount, Ingredient
from users.models import User


class EndpointsTestCase(TestCase):  # BaseTestCase

    def reverse(self, url_basename, kwargs=None):
        return reverse(url_basename, kwargs=kwargs).strip('/')

    def test_url_basenames(self):
        """Проверка наличия всех эндпоинтов, соответствия именам."""
        urls_basename = (
            # djoser.urls.authtoken
            ('login', 'api/auth/token/login', None),
            ('logout', 'api/auth/token/logout', None),
            # djoser.urls and my users endpoints
            ('user-list', 'api/users', None),
            ('user-detail', 'api/users/1', {'id': 1}),
            ('user-me', 'api/users/me', None),
            ('user-set-password', 'api/users/set_password', None),
            ('user-subscriptions', 'api/users/subscriptions', None),
            ('user-subscribe', 'api/users/1/subscribe', {'id': 1}),
            # tags endpoints
            ('tag-list', 'api/tags', None),
            ('tag-detail', 'api/tags/1', {'id': 1}),
            # recipes endpoints
            ('recipe-list', 'api/recipes', None),
            ('recipe-detail', 'api/recipes/1', {'id': 1}),
            ('recipe-download-shopping-cart',
             'api/recipes/download_shopping_cart', None),
            ('recipe-shopping-cart',
             'api/recipes/1/shopping_cart', {'id': 1}),
            ('recipe-favorite',
             'api/recipes/1/favorite', {'id': 1}),
            # ingredients endpoints
            ('ingredient-list', 'api/ingredients', None),
            ('ingredient-detail', 'api/ingredients/1', {'id': 1}),
        )

        for name, url, kwargs in urls_basename:
            url_reversed = self.reverse(name, kwargs=kwargs)
            with self.subTest(url=url, url_reversed=url_reversed):
                self.assertEqual(url_reversed, url)


class TagsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tags = (
            {
                'id': 1,
                'name': 'Завтрак',
                'color': '#FF0000',
                'slug': 'zavtrak'
            },
            {
                'id': 2,
                'name': 'Обед',
                'color': '#00FF00',
                'slug': 'obed'
            },
            {
                'id': 3,
                'name': 'Ужин',
                'color': '#0000FF',
                'slug': 'uzhin'
            },
        )
        for tag in cls.tags:
            Tag.objects.create(**tag)
        super().setUpClass()

    def setUp(self):
        self.anonime = APIClient()
        cache.clear()

    def test_tags_list(self):
        """Проверка получения списка тегов без авторизации"""
        url = reverse('tag-list')
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0], self.__class__.tags[0])

    def test_tags_id(self):
        """Проверка получения тега по id без авторизации"""
        url = reverse('tag-detail', kwargs={'id': 2})
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.assertEqual(data, self.__class__.tags[1])

    def test_tags_wrong_id(self):
        """Проверка получения не верного тега по id без авторизации"""
        url = reverse('tag-detail', kwargs={'id': 200})
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        data = json.loads(response.content)
        self.assertEqual(data, {'detail': 'Страница не найдена.'})


class IngredientsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ingredients = (
            {
                'id': 0,
                'name': 'Капуста0',
                'measurement_unit': 'кг'
            },
            {
                'id': 1,
                'name': 'Капуста',
                'measurement_unit': 'кг'
            },
            {
                'id': 2,
                'name': 'Кактус',
                'measurement_unit': 'кг'
            },
            {
                'id': 3,
                'name': 'Качан',
                'measurement_unit': 'кг'
            },
            {
                'id': 4,
                'name': 'Карп',
                'measurement_unit': 'кг'
            },
            {
                'id': 5,
                'name': 'Палтус',
                'measurement_unit': 'кг'
            },
            {
                'id': 6,
                'name': 'Тусовка опят',
                'measurement_unit': 'кг'
            },
            {
                'id': 7,
                'name': 'яблоки',
                'measurement_unit': 'кг'
            },
            {
                'id': 8,
                'name': 'Картон',
                'measurement_unit': 'кг'
            },
            {
                'id': 9,
                'name': 'Лимон',
                'measurement_unit': 'кг'
            },
        )
        for ingredient in cls.ingredients:
            Ingredient.objects.create(**ingredient)
        super().setUpClass()

    def setUp(self):
        self.anonime = APIClient()
        cache.clear()

    def test_ingredients_list(self):
        """Проверка получения списка ингредиентов без авторизации"""
        url = reverse('ingredient-list')
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 10)
        self.assertEqual(data[0], self.__class__.ingredients[0])

    def test_ingredients_id(self):
        """Проверка получения ингредиента по id без авторизации"""
        url = reverse('ingredient-detail', kwargs={'id': 2})
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.assertEqual(data, self.__class__.ingredients[1])

    def test_ingredients_wrong_id(self):
        """Проверка получения не верного ингредиента по id без авторизации"""
        url = reverse('ingredient-detail', kwargs={'id': 200})
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_ingredient_seach_by_name_part(self):
        """Проверка получения списка ингредиентов по фрагменту имени."""
        url = reverse('ingredient-list')
        response = self.anonime.get(url, data={'name': 'тус'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)


class UsersTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.users = (
            {
                'username': 'user_authorized',
                'email': 'test@mail.ru',
                'first_name': 'user_first_name',
                'last_name': 'user_last_name'
            },
            {
                'username': 'user_1',
                'email': 'test_1@mail.ru',
                'first_name': 'user_1_first_name',
                'last_name': 'user_1_last_name'
            },
            {
                'username': 'user_2',
                'email': 'test_2@mail.ru',
                'first_name': 'user_2_first_name',
                'last_name': 'user_2_last_name'
            }
        )
        #for user in cls.users:
        #    User.objects.create(**user, password='password', is_active=True)
        user0 = User.objects.create(**cls.users[0], password='password', is_active=True)
        user1 = User.objects.create(**cls.users[1], password='password', is_active=True)
        user2 = User.objects.create(**cls.users[2], password='password', is_active=True)

        image = ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAIAAA'
                 'AC64paAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAEn'
                 'QAABJ0Ad5mH3gAAADnSURBVDhPnZFNCsIwEIU9iEvvoUsv5MpbuHDnRnDhUt'
                 'EjCMWfnbjwAP6BUEGEUExMmTR9mfwUfDzKZOZ97YS2VFJCfLv9fdCz+bWExX'
                 'L1GY0pzZRtc8agS1iTz3aHTAxpd3ixNHO9tuXpFVIqG+oBgHZgLBK3tY7CRS'
                 'FZlHmT5dG1tRbrBwPQOhD+MtW3u9D/gzHWOhCASXg8nt6D4RnJyfSi++G1yW'
                 'YQVw3/oWY4sYID+7n0/vzO5lAJO37AwDESm37GgdnMP7JODdMTx6zGI8mBsd'
                 'AiAG0GlfjawRDJ7xuY1Ag7I6V+eFybE9tlqTkAAAAASUVORK5CYII=="')
        image = None
        cls.recipes = (
            {
                'image': image,
                'author': user1,
                'name': 'Рецепт 1',
                'text': 'Рецепт 1',
                'cooking_time': 1
            },
            {
                'image': image,
                'name': 'Рецепт 2',
                'author': user1,
                'text': 'Рецепт 2',
                'cooking_time': 2
            },
            {
                'image': image,
                'name': 'Рецепт 3',
                'author': user1,
                'text': 'Рецепт 3',
                'cooking_time': 3
            },
            {
                'image': image,
                'name': 'Рецепт 4',
                'author': user1,
                'text': 'Рецепт 4',
                'cooking_time': 4
            },
            {
                'image': image,
                'name': 'Рецепт 5',
                'author': user1,
                'text': 'Рецепт 5',
                'cooking_time': 5
            },
            {
                'image': image,
                'name': 'Рецепт 6',
                'author': user1,
                'text': 'Рецепт 6',
                'cooking_time': 6
            },
            {
                'image': image,
                'author': user1,
                'name': 'Рецепт 7',
                'text': 'Рецепт 7',
                'cooking_time': 7
            }
        )
        for recipe in cls.recipes:
            Recipe.objects.create(**recipe)

        cls.follows = (
            {
                'user': user0,
                'author': user1,
            },
            {
                'user': user0,
                'author': user2,
            }
        )
        for follow in cls.follows:
            Follow.objects.create(**follow)







        client = APIClient()

        # Регистрация нового пользователя через эндпоинт.
        email = f'{cls.__name__}@yandex.ru'
        cls.password = 'dsofniwjhfd87yr489384ur98reufhd'
        username = cls.__name__

        response = client.post(
            reverse('user-list'),
            {
                'email': email,
                'username': username,
                'first_name': 'First',
                'last_name': 'Second',
                'password': cls.password
            },
            format='json'
        )

        # Получение токена.
        response = client.post(
            reverse('login'),
            {'email': email, 'password': cls.password},
            format='json'
        )

        # Извлечение токена из ответа.
        data = json.loads(response.content)
        cls.token = data.get('auth_token')
        cls.user = User.objects.get(username=username)

        cls.follows = (
            {
                'user': cls.user,
                'author': user1,
            },
            {
                'user': cls.user,
                'author': user2,
            }
        )
        for follow in cls.follows:
            Follow.objects.create(**follow)


    def setUp(self):
        cls = self.__class__
        self.authorized = APIClient()
        self.authorized.credentials(HTTP_AUTHORIZATION='Token ' + cls.token)
        self.anonime = APIClient()
        cache.clear()

    def test_users_list(self):
        """Проверка получения списка пользователей без авторизации"""
        url = reverse('user-list')
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
        count = User.objects.all().count()
        self.assertEqual(data.get('count'), count)
        self.assertIn('next', data)
        self.assertIn('previous', data)
        userlist = data.get('results')
        self.assertIsInstance(userlist, list)
        self.assertEqual(len(userlist), count)
        lastuser = None
        for user in userlist:
            with self.subTest(user=user):
                self.assertFalse(user.pop('is_subscribed'))
                self.assertNotEqual(lastuser, user)
                lastuser = user
                self.assertTrue(User.objects.filter(**user).exists())

    def test_users_list_with_pagination(self):
        """Проверка получения списка пользователей с пагинацией"""
        url = reverse('user-list')
        response = self.anonime.get(url, data={'page': 2, 'limit': 2})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
        count = User.objects.all().count()
        self.assertEqual(data.get('count'), count)
        self.assertIn('next', data)
        self.assertIsNotNone(data.get('previous'))
        userlist = data.get('results')
        self.assertIsInstance(userlist, list)
        showed = 2 if count >= 4 else 0 if count <= 2 else count - 2
        self.assertEqual(len(userlist), showed)

    def test_users_profile_unauthorized(self):
        """
        Проверка получения данных пользователя не авторизованным пользователем.
        """
        url = reverse('user-detail', kwargs={'id': 1})
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_users_profile_not_found(self):
        """
        Проверка получения данных о несуществующем пользователе.
        """
        url = reverse('user-detail', kwargs={'id': 200})
        response = self.authorized.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_users_profile_authorized(self):
        """
        Проверка получения данных пользователя авторизованным пользователем.
        """
        url = reverse('user-detail', kwargs={'id': self.__class__.user.pk})
        response = self.authorized.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
        self.assertFalse(data.pop('is_subscribed'))
        self.assertTrue(User.objects.filter(**data).exists())

    def test_users_me_authorized(self):
        """
        Проверка получения данных о текущем пользователе.
        """
        url = reverse('user-me')
        response = self.authorized.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
        self.assertFalse(data.pop('is_subscribed'))
        self.assertEqual(User.objects.filter().last(), self.__class__.user)

    def test_users_me_unauthorized(self):
        """
        Проверка получения данных о текущем пользователе не авторизованным
        пользовыателем.
        """
        url = reverse('user-me')
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_users_add_new_user_max_len_parameters(self):
        response = self.anonime.post(
            reverse('user-list'),
            {
                'email': 'a'*246 + '@mail.ru',
                'username': 'b'*150,
                'first_name': 'c'*150,
                'last_name': 'd'*150,
                'password': 'e'*150
            },
            format='json'
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
        self.assertEqual(data.pop('email'), 'a'*246 + '@mail.ru')
        self.assertEqual(data.pop('username'), 'b'*150)
        self.assertEqual(data.pop('first_name'), 'c'*150)
        self.assertEqual(data.pop('last_name'), 'd'*150)

    def test_users_add_new_wrong_fields(self):
        wrong_user = [
            {
                'email': 'a' * 247 + '@mail.ru',
                'username': 'b' * 150,
                'first_name': 'c' * 150,
                'last_name': 'd' * 150,
                'password': 'e' * 150
            },
            {
                'email': 'a' * 246 + '@mail.ru',
                'username': 'b' * 151,
                'first_name': 'c' * 150,
                'last_name': 'd' * 150,
                'password': 'e' * 150
            },
            {
                'email': 'a' * 246 + '@mail.ru',
                'username': 'b' * 150,
                'first_name': 'c' * 151,
                'last_name': 'd' * 150,
                'password': 'e' * 150
            },
            {
                'email': 'a' * 246 + '@mail.ru',
                'username': 'b' * 150,
                'first_name': 'c' * 150,
                'last_name': 'd' * 151,
                'password': 'e' * 150
            },
            {
                'email': 'a' * 246 + '@mail.ru',
                'username': 'b' * 150,
                'first_name': 'c' * 150,
                'last_name': 'd' * 150,
                'password': 'e' * 151
            },
        ]
        url = reverse('user-list')
        for user in wrong_user:
            with self.subTest(user=user):
                response = self.anonime.post(url, **user, format='json')
                self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_users_set_password(self):
        response = self.authorized.post(
            reverse('user-set-password'),
            {
                'new_password': self.__class__.password + '_new',
                'current_password': self.__class__.password
            },
            format='json'
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.authorized.post(
            reverse('user-set-password'),
            {
                'new_password': self.__class__.password,
                'current_password': self.__class__.password + '_new'
            },
            format='json'
        )

    def test_users_set_password_unauthorized(self):
        response = self.anonime.post(
            reverse('user-set-password'),
            {
                'new_password': self.__class__.password + '_new',
                'current_password': self.__class__.password
            },
            format='json'
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_users_set_password_wrong_field(self):
        response = self.authorized.post(
            reverse('user-set-password'),
            {
                'new_password': self.__class__.password + '_new',
                'current_wrong_password': self.__class__.password
            },
            format='json'
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_users_subscriptions_list_anonime(self):
        url = reverse('user-subscriptions')
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_users_subscriptions_list(self):
        url = reverse('user-subscriptions')
        response = self.authorized.get(
            url, data={'page': 1, 'limit': 2, 'recipes_limit': 4})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.assertIsInstance(data, dict)
        count = Follow.objects.all().count()
        self.assertEqual(data.get('count'), 2)
        self.assertIn('next', data)
        self.assertIn('previous', data)
        results = data.get('results')

        self.assertIsInstance(results, list)
        showed = 2 if count >= 4 else 0 if count <= 2 else count - 2
        self.assertEqual(len(results), showed)

        follows_count = Follow.objects.filter(user=self.__class__.user).count()
        self.assertEqual(len(results), follows_count)

        result = results[0]

        recipes_count = result.pop('recipes_count')
        self.assertTrue(result.pop('is_subscribed'))
        recipes = result.pop('recipes')
        self.assertIsInstance(recipes, list)

        user = User.objects.filter(**result).get()

        user_recipe_count = user.recipes.count()  # Recipe.objects.filter(author=user).count()
        self.assertEqual(user_recipe_count, recipes_count)

        recipe = recipes[0]

        self.assertIsInstance(recipe, dict)

        recipe.pop('image')

        self.assertTrue(Recipe.objects.filter(**recipe).exists())




#('user-subscriptions', 'api/users/subscriptions', None),
#('user-subscribe', 'api/users/1/subscribe', {'id': 1}),



#('recipe-list', 'api/recipes', None),
#('recipe-detail', 'api/recipes/1', {'id': 1}),
#('recipe-download-shopping-cart',
# 'api/recipes/download_shopping_cart', None),
#('recipe-shopping-cart',
# 'api/recipes/1/shopping_cart', {'id': 1}),
#('recipe-favorite',
# 'api/recipes/1/favorite', {'id': 1}),
