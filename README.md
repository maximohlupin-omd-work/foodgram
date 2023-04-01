# Foodgram - easy food social network

### Фронтэнд это разработка из команды "Яндекс.Практикум"

### Стэк разработки (Бэкенд)

- Python 3.9
- Django 4.1
- DjangoRestFramework 3.14.0
- gevent 22.10.2
- gunicorn 20.1.0

### Сборка

- cd ./infra
- docker compose -f docker-compose-prod.yml up -d

### Документация

- http://localhost/docs/redoc.html

### Значения по умолчанию

В докер-образе используется легковесная база SQLite3
При пулл образа в базу будут записаны данные о тестовом пользователе
Данные о тегах и ингридиентах и один готовый рецепт.

