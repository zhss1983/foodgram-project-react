import json
from http import HTTPStatus

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from .models import User


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


class EndpointsTestCase(TestCase):
    def reverse(self, url_basename, kwargs=None):
        return reverse(url_basename, kwargs=kwargs).strip("/")

    def test_url_basenames(self):
        """Проверяет наличие всех эндпоинтов, соответствия именам."""
        urls_basename = (
            # djoser.urls.authtoken
            ("login", "api/auth/token/login", None),
            ("logout", "api/auth/token/logout", None),
            # djoser.urls
            ("user-list", "api/users", None),
            ("user-detail", "api/users/1", {"id": 1}),
            ("user-me", "api/users/me", None),
            ("user-set-password", "api/users/set_password", None),
        )

        for name, url, kwargs in urls_basename:
            url_reversed = self.reverse(name, kwargs=kwargs)
            with self.subTest(url=url, url_reversed=url_reversed):
                self.assertEqual(url_reversed, url)


class UsersTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        users = (
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
        User.objects.create(
            **users[0], password="password_lkgdoi32dgu7e6", is_active=True
        )
        User.objects.create(
            **users[1], password="password_lkxznvcdsf7e94", is_active=True
        )
        User.objects.create(
            **users[2], password="password_nvreiuhfglkdsn", is_active=True
        )

    def test_users_list(self):
        """Проверяет получение списка пользователей без авторизации"""
        url = reverse("user-list")
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        count = User.objects.count()
        userlist = self.page_paginated(data, count)
        self.is_users(userlist, is_subscribed=False, count=count)

    def test_users_list_with_pagination(self):
        """Проверяет получение списка пользователей с пагинацией"""
        url = reverse("user-list")
        response = self.anonime.get(url, data={"page": 2, "limit": 2})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        count = User.objects.count()
        userlist = self.page_paginated(data, count)
        showed = 2 if count >= 4 else 0 if count <= 2 else count - 2
        self.is_users(userlist, count=showed)

    def test_users_profile_unauthorized(self):
        """
        Проверяет блокировку получение данных не авторизованным пользователем.
        """
        url = reverse("user-detail", kwargs={"id": 1})
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_users_profile_not_found(self):
        """
        Проверяет получение данных о несуществующем пользователе.
        """
        url = reverse("user-detail", kwargs={"id": 200})
        response = self.authorized.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_users_profile_authorized(self):
        """
        Проверяет получение данных пользователя авторизованным пользователем.
        """
        url = reverse("user-detail", kwargs={"id": self.__class__.user.pk})
        response = self.authorized.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.is_user(data, is_subscribed=False)

    def test_users_me_authorized(self):
        """
        Проверяет получение данных о текущем пользователе.
        """
        url = reverse("user-me")
        response = self.authorized.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.content)
        self.is_user(data, is_subscribed=False)
        self.assertEqual(data.get("id"), self.__class__.user.pk)

    def test_users_me_unauthorized(self):
        """
        Проверяет получение данных о текущем пользователе не авторизованным
        пользователем.
        """
        url = reverse("user-me")
        response = self.anonime.get(url)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_users_add_new_user_max_len_parameters(self):
        """
        Проверяет возможность добавления пользователя с максимальными по длине
        параметрами.
        """
        new_user = {
            "email": "a" * 246 + "@mail.ru",
            "username": "b" * 150,
            "first_name": "c" * 150,
            "last_name": "d" * 150,
            "password": "e" * 150,
        }
        response = self.anonime.post(reverse("user-list"), data=new_user, format="json")
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        data = json.loads(response.content)
        self.is_user(data)
        new_user.pop("password")
        self.assertEqual(new_user, data)

    def test_users_add_new_wrong_fields(self):
        """
        Проверяет блокировку добавления пользователя с избыточными по
        длине параметрами.
        """
        wrong_user = [
            {
                "email": "a" * 247 + "@mail.ru",
                "username": "b" * 150,
                "first_name": "c" * 150,
                "last_name": "d" * 150,
                "password": "e" * 150,
            },
            {
                "email": "a" * 246 + "@mail.ru",
                "username": "b" * 151,
                "first_name": "c" * 150,
                "last_name": "d" * 150,
                "password": "e" * 150,
            },
            {
                "email": "a" * 246 + "@mail.ru",
                "username": "b" * 150,
                "first_name": "c" * 151,
                "last_name": "d" * 150,
                "password": "e" * 150,
            },
            {
                "email": "a" * 246 + "@mail.ru",
                "username": "b" * 150,
                "first_name": "c" * 150,
                "last_name": "d" * 151,
                "password": "e" * 150,
            },
            {
                "email": "a" * 246 + "@mail.ru",
                "username": "b" * 150,
                "first_name": "c" * 150,
                "last_name": "d" * 150,
                "password": "e" * 151,
            },
        ]
        url = reverse("user-list")
        for user in wrong_user:
            with self.subTest(user=user):
                response = self.anonime.post(url, **user, format="json")
                self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    def test_users_set_password(self):
        """Проверяет возможность изменить пароль пользователя."""
        response = self.authorized.post(
            reverse("user-set-password"),
            {
                "new_password": self.__class__.password + "_new",
                "current_password": self.__class__.password,
            },
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.authorized.post(
            reverse("user-set-password"),
            {
                "new_password": self.__class__.password,
                "current_password": self.__class__.password + "_new",
            },
            format="json",
        )

    def test_users_set_password_unauthorized(self):
        """
        Проверяет блокировку изменения пароль пользователя не авторизованным
        пользователем.
        """
        response = self.anonime.post(
            reverse("user-set-password"),
            {
                "new_password": self.__class__.password + "_new",
                "current_password": self.__class__.password,
            },
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_users_set_password_wrong_field(self):
        """
        Проверяет блокировку изменения пароля с неверными параметрами.
        """
        response = self.authorized.post(
            reverse("user-set-password"),
            {
                "new_password": self.__class__.password + "_new",
                "current_wrong_password": self.__class__.password,
            },
            format="json",
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
