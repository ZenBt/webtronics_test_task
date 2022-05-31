# webtronics_test_task
Тестовое задание на позицию Junior Python Developer

## Выполнил
Игорь ZenBt Ткаченко

## Описание проекта
Небольшой REST API сервис, представляющий из себя социальную сеть с возможностью регистрации, аутентификации, добавления постов, оценки постов.

## Установка
`git clone https://github.com/ZenBt/webtronics_test_task.git` \
Создать виртуальное окружени (например через `python3 -m venv venv`) \
Активировать venv `source venv/bin/activate` и установить необходимые пакеты \
`pip install -r webtronics_test_task/requirements.txt` \
Для работы необходим установленный PostgreSQL. \
Данные о созданном пользователе необходимо внести в переменные окружения: \
`export PG_NAME="название бд"` \
`export PG_USER="имя пользователя бд"` \
`export PG_PWD="пароль для бд"` \
`export PG_HOST="localhost"` \
Создать секретный ключ \
`export SECRET_KEY="VerySecretKeyDjango123123"` \
При необходимости провести миграции \
`python manage.py makemigrations` \
`python manage.py migrate` \
Запуск \
`python manage.py runserver`

## Тестирование
Перед запуском рекомендуется запустить юнит тесты \
`python manage.py test`

## Использование
Проект использует аутентификацию по JWT-токену. 
### Регистрация
После запуска приложения необходимо пройти регистрацию: \
`POST /api/singup/` в POST-запрос необходимо включить `username` и `password`
### Получение токена
Пройдя регистрацию появится возможность получить access и refresh токены: \
`POST /api/token/`в POST-запрос необходимо включить внесенные ранее `username` и `password` 
### Взаимодействие с постами
Просмотр списка постов `GET /api/post/` \
Формат ответа: \
[ \
    { \
        "id": 1, \
        "title": "test 1", \
        "content": "ts2", \
        "author_name": "ZenBt", \
        "total_likes": 1 \
    }, \
    { \
        "id": 2, \
        "title": "test 2", \
        "content": "new", \
        "author_name": "test_user", \
        "total_likes": 4 \
    }, \
    { \
        "id": 3, \
        "title": "test 3", \
        "content": "ts3", \
        "author_name": "ZenBt", \
        "total_likes": 0 \
    } \
] \
Добавлени поста `POST /api/post/` обязательные данные `title` и `content` \
Просмотр поста по его id `GET /api/post/<int:post_id>` дополнительных параметров не требуется
### Взаимодействие с лайками
Поставить лайк посту `POST /api/like/<int:post_id>` обязательный параметр `is_liked: True` \
После добавление лайка его можно убрать `PUT /api/like/<int:post_id>`, аналогично наличие `is_liked` обязательно \
Дальнейшее взаимодействие с лайками происходи посредством `PUT`: \
`is_liked: true` добавит лайк к посту, `is_liked: false` - уберет \
Важно: `PUT` запрос до добавление первого лайка приведет к ошибке. 
Последующее изменение значение `is_liked` через `POST` так же вызовет ошибку `BAD REQUEST`
