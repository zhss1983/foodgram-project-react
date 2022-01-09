# [Документация к API Foodgram](http://www.zhss.tk/recipes)

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

## Описание проекта:

Проект Foodgram позволяет сохранять свои рецепты и просматривать чужие. Есть
выозможность подписаться на других пользователей и добавить различные рецепты
в избранные. Так же можно создать список рецептов для покупки продуктов.

## Работа с эндпоинтами:

Краткое описание основных возможностей, за более подробной информацией
обратитесь к [/redoc/](http://www.zhss.tk/api/docs/) 

По всем вопросам обращайтесь к администраторам по электронной почте
[zhss.83@mail.ru](mailto:zhss.83@mail.ru)