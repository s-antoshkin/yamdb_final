# YaMDb(docker-compose + GitHub Actions)
[![Python](https://img.shields.io/badge/Made%20with-Python-green?logo=python&logoColor=white&color)](https://www.python.org/)
[![Docker](https://img.shields.io/static/v1?message=docker&logo=docker&labelColor=5c5c5c&color=002c66&logoColor=white&label=%20&style=plastic)](https://www.docker.com/)
[![Django](https://img.shields.io/static/v1?message=django&logo=django&labelColor=5c5c5c&color=0c4b33&logoColor=white&label=%20&style=plastic)](https://www.djangoproject.com/)
[![Nginx](https://img.shields.io/static/v1?message=nginx&logo=nginx&labelColor=5c5c5c&color=009900&logoColor=white&label=%20&style=plastic)](https://nginx.org/)
[![Postgres](https://img.shields.io/static/v1?message=postgresql&logo=postgresql&labelColor=5c5c5c&color=1182c3&logoColor=white&label=%20&style=plastic)](https://www.postgresql.org/)
![Workflow](https://github.com/s-antoshkin/yamdb_final/workflows/api_yamdb_workflow/badge.svg)


## О проекте:
**Проект YaMDb собирает отзывы (`Review`) пользователей на произведения (`Titles`).    
Произведения делятся на категории: «Книги», «Фильмы», «Музыка» (cписок категорий (`Category`) может быть расширен администратором).**
#### Проект доступен по [ссылке](http://51.250.21.52/api/v1/).

### Пользовательские роли:
 - **Аноним** — может просматривать описания произведений, читать отзывы и комментарии.
 - **Аутентифицированный пользователь (`user`)** — может читать всё, как и **Аноним**, может публиковать отзывы и ставить оценки произведениям (фильмам/книгам/песенкам), может комментировать отзывы; может редактировать и удалять свои отзывы и комментарии, редактировать свои оценки произведений. Эта роль присваивается по умолчанию каждому новому пользователю.
 - **Модератор (`moderator`)** — те же права, что и у **Аутентифицированного пользователя**, плюс право удалять и редактировать любые отзывы и комментарии.
 - **Администратор (`admin`)** — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.
 - **Суперюзер Django** должен всегда обладать правами администратора, пользователя с правами `admin`. Даже если изменить пользовательскую роль суперюзера — это не лишит его прав администратора. Суперюзер — всегда администратор, но администратор — не обязательно суперюзер.

### Самостоятельная регистрация новых пользователей:
1. Пользователь отправляет POST-запрос с параметрами `email` и `username` на эндпоинт `/api/v1/auth/signup/`;
2. Сервис YaMDB отправляет письмо с кодом подтверждения (`confirmation_code`) на указанный адрес `email`;
3. Пользователь отправляет POST-запрос с параметрами `username` и `confirmation_code` на эндпоинт `/api/v1/auth/token/`, в ответе на запрос ему приходит `token` (JWT-токен).
   ##### В результате пользователь получает токен и может работать с API проекта, отправляя этот токен с каждым запросом.

### Запуск проекта:
#### 1. В dev-режиме:
Клонировать репозиторий и перейти в него в командной строке:
```sh
git clone git@github.com:s-antoshkin/infra_sp2.git
```
Установить и активировать виртуальное окружение:
```sh
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt
```sh
pip install -r requirements.txt
```
Выполнить миграции:
```sh
python manage.py migrate
``` 
Импортировать данные:
```sh
python manage.py loaddata fixtures.json
```
или из CSV-файла:
```sh
python manage.py import_from_csv <csv файл> <название модели>
```
В папке с файлом manage.py выполните команду:
```sh
python manage.py runserver
```

#### 2. Запуск в контейнере docker:
Скопировать `.env.example` и назвать его `.env`:
```sh
cp .env.example .env
```
Заполнить переменные окружения в `.env`:
```sh
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД

SECRET_KEY=secret_key # секретный ключ (вставте свой)
```
Запустить `docker-compose` командой:
```
docker-compose up -d --build
```
Собрать статику и выполнить миграции внутри контейнера, создать суперпользователя:
```sh
docker-compose exec web python manage.py migrate --noinput
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```
#### При необходимости возможно импортировать тестовые данные:
```sh
docker-compose exec web python manage.py loaddata fixtures.json
```
- При импорте создается суперюзер `admin` с паролем `admin`

## Деплой на удаленном сервере
Для запуска на удаленном сервере необходимо:
- перенести файлы `docker-compose.yaml` и папку `nginx` на сервер, выполнив команду:
```sh
scp -r ./infra/* <username>@<server_ip>:/home/<username>/
```

- на github, в настройках репозитория `Secrets` --> `Actions` создать и заполнить переменные окружения:
```sh
DOCKER_USERNAME # Имя пользователя на Docker Hub;
DOCKER_PASSWORD # Пароль от Docker Hub;
DB_ENGINE # Указать, что работаем с базой данных PostgresQl;
DB_NAME # Имя базы данных;
DB_HOST # Название контейнера базы данных; 
DB_PORT # Порт для подключения к базе данных;
POSTGRES_USER # Логин для подключения к базе данных;
POSTGRES_PASSWORD # Пароль для подключение к базе данных;
SECRET_KEY # Секретный ключ приложения;
USER # Имя пользователя на сервере;
HOST # Публичный IP-адрес сервера;
PASSPHRASE # Указать в том случае, если ssh-ключ защищен фразой-паролем;
SSH_KEY # Приватный ssh-ключ;
TELEGRAM_TO # ID телеграм-аккаунта;
TELEGRAM_TOKEN # Токен телеграм-бота.
```

### После каждого пуша (`git push`) в главную ветку `main`:
- будут автоматически запускаться тесты: проверка кода на соответствие стандарту `PEP8` (с помощью пакате `flake8`) и запуск `pytest` из репозитория `yamdb_final`;
- сборка и доставка докер-образа на `Docker Hub`;
- автоматический деплой на боевой сервер;
- отправка сообщения в `Telegram` при успешном завершении деплоя.

### Ресурсы API YaMDb
- Ресурс `auth`: аутентификация.
- Ресурс `users`: пользователи.
- Ресурс `titles`: произведения, к которым пишут отзывы (определённый фильм, книга или песенка).
- Ресурс `categories`: категории (типы) произведений («Фильмы», «Книги», «Музыка»).
- Ресурс `genres`: жанры произведений. Одно произведение может быть привязано к нескольким жанрам.
- Ресурс `reviews`: отзывы на произведения. Отзыв привязан к определённому произведению.
- Ресурс `comments`: комментарии к отзывам. Комментарий привязан к определённому отзыву.

**Участники:**   

[Антошкин Семён](https://github.com/s-antoshkin):
- Категории (Categories), жанры (Genres) и произведения (Titles): модели, представления и эндпойнты для них;
- Контейнеризация, CI с использованием Github Actions.

[Сергей Лебедев](https://github.com/SergeiLebedev34907):
Управление пользователями (Auth и Users): система регистрации и аутентификации, права доступа, работа с токеном, система подтверждения через e-mail.

[Сергей Егоркин](https://github.com/serezhs):
Отзывы (Review) и комментариями (Comments): модели, представления, настрайка эндпойнты, права доступа для запросов; рейтинги произведений.
#### Подробную документацию можно посмотреть по [ссылке](http://51.250.21.52/redoc/) (или по [ссылке](http://127.0.0.1:8000/redoc/) - если проект запущен в dev-режиме).