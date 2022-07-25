# Документация к API Foodgram

![example workflow](https://github.com/zhss1983/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Описание проекта:

API Foodgram позволяет сохранять свои рецепты и делиться ими с друзьями. Дополнительные возможности позволяют выбрать
 избранные рецепты или подписаться на друзей, можно собрать корзину и выгрузить список того что требуется купить для их
 приготовления.

Стэк технологий:
 **Python 3.9,
 [Django 3.2.9](https://docs.djangoproject.com/en/4.0/),
 [DjangoRestFramework](https://www.django-rest-framework.org),
 [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/),
 [PostgreSQL](https://www.postgresql.org/docs/),
 [Docker](https://docs.docker.com/),
 [Docker Compose](https://docs.docker.com/compose/),
 [Gunicorn](https://docs.gunicorn.org/en/stable/) 20.0,
 [Nginx](https://docs.nginx.com/) 1.21 ([Ru](https://nginx.org/ru/docs/)).**

## Особенность данного проекта:

В этом проекте применена технология Single-page application. Моя часть работы заключалась в написании Backend API для
 него и размещение всего проекта на сервере.

Процесс регистрации и авторизация пользователя ...

Джанго настроен для работы с базой данных Postgres.

Образ серверной части приложения создаётся в момент размещения кода в репозитории GitHub. Для этого создан
 соответствующий скрипт с активацией по команде push в ветку main. При этом происходит обязательное тестирование
 залитого проекта на соответствие стандартам PEP8 и на прохождение всех написанных мною юнит тестов (Django Unit Test framework).

Следующим шагом происходит сборка docker образа и его деплой на DockerHub. При этом применяется Gunicorn - Python WSGI HTTP Server для UNIX систем.

После успешного деплоя происходит отправка отчёта от GitHub в телеграмм разработчика.

Запуск проекта происходит с применением docker-compose (описано ниже). При этом происходит сборка четырёх образов:
1) Компиляция по соответствующим инструкциям образа фронтэнда из докерфайла.
2) Копирование с DockerHub образа Postgres на базе Alpine Linux и копирование туда файлов базы данных.
3) Копирование с DockerHub бэкэнд образа [zhss1983/foodgram](https://hub.docker.com/r/zhss1983/foodgram) скомпилированного автоматически GitHub-ом.
4) Копирование с DockerHub бэкэнд образа Nginx на базе Alpine Linux, его настройка для работы со статикой и бекендом.

## Как запустить проект:

Копировать с репозитория следующие файлы и папки:
- /docs/
- /frontend/
- /infra/
- /docker-compose.yml

Создать три файла с переменными окружения:

- .env_db - необходим для создания БД
  - DB_ENGINE=django.db.backends.postgresql_psycopg2
  - DB_NAME=postgres
  - POSTGRES_USER=<ИМЯ ПОЛЬЗОВАТЕЛЯ>
  - POSTGRES_PASSWORD=<ПАРОЛЬ>
  - DB_HOST=db
  - DB_PORT=5432
  - CLIENT_ENCODING=UTF8
- .env_web - необходимы для запуска проекта в целом.
  - SECRET_KEY=<КЛЮЧ БЕЗОПАСНОСТИ БЭКЭНДА>
  - HOST_NAMES=<ИМЯ ХОСТА>, <ИМЯ ХОСТА>, <...>, <АДРЕС ХОСТА>
  - EMAIL_FOODGRAM=<ПОЧТА ДЛЯ ОТПРАВКИ ПИСЕМ АДМИНИСТРАТОРУ>
- .env_mail - необходимы для отправки почты.
  - EMAIL_HOST=smtp.mail.ru
  - EMAIL_PORT=2525
  - EMAIL_HOST_USER=<ПОЧТОВЫЙ ЯЩИК С КОТОРОГО ОТПРАВЛЯЕТСЯ ПОЧТА>
  - EMAIL_HOST_PASSWORD=<ПАРОЛЬ>
  - EMAIL_USE_TLS=True

Выполнить команду:
```
docker-compose up -d
```

## Работа с эндпоинтами:

Краткое описание основных возможностей, за более подробной информацией
 обратитесь к [/redoc/](https://github.com/zhss1983/foodgram-project-react/tree/master/docs/redoc.html) 
 ([yml](https://github.com/zhss1983/foodgram-project-react/tree/master/docs/openapi-schema.yml)). 

По всем вопросам обращайтесь к администраторам по электронной почте
 [zhss.83@yandex.ru](mailto:zhss.83@yandex.ru)
