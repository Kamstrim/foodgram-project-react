## Описание

Приложение «Продуктовый помощник»: Онлайн-сервис и API для него. Сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Функционал

- Регистрация и восстановление доступа по электронной почте;
- Создаются и редактируются собственные записи;
- Добавляются изображения к посту;
- Просмотриваются страницы других авторов;
- Комментируются записи других авторов;
- Подписки и отписки от авторов;
- Записи назначаются в отдельные группы;
- Личная страница для публикации записей;
- Отдельная лента с постами авторов на которых подписан пользователь;
- Через панель администратора модерируются записи, происходит управление пользователями и создаются группы.

## Стек технологий

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)


- Проект работает с СУБД PostgreSQL.
- Проект запущен на сервере в Яндекс.Облаке в трёх контейнерах: nginx, PostgreSQL и Django+Gunicorn. Контейнер с проектом обновляется на Docker Hub.
- В nginx настроена раздача статики, остальные запросы переадресуются в Gunicorn.
- Данные сохраняются в volumes.

## Оформление кода

Код соответствует PEP8.

## Доменное имя

[https://kamstrim.ddns.net/](https://kamstrim.ddns.net/)

[https://158.160.5.250/](https://158.160.5.250/)


## Доступ к Админ панели
```
login: kamstrim
password: 12345
```
### Запуск проекта:
1. Клонируйте проект:
```
git clone https://github.com/Kamstrim/foodgram-project-react.git
```
2. Подготовьте сервер:

- Установить на сервере Docker, Docker Compose:

```
sudo apt install curl

curl -fsSL https://get.docker.com -o get-docker.sh

sh get-docker.sh

sudo apt-get install docker-compose-plugin
```

- Скопировать на сервер файлы docker-compose.production.yml, .env, nginx.conf из папки infra (команды выполнять находясь в папке infra):

```
scp docker-compose.production.yml nginx.conf .env username@IP:/home/username/   

```

- Для работы с GitHub Actions необходимо в репозитории в разделе Secrets - Actions создать переменные окружения:
```
DOCKER_PASSWORD
DOCKER_USERNAME
HOST
USER
SSH_PASSPHRASE
SSH_KEY
TELEGRAM_TO
TELEGRAM_TOKEN

```

- Создать и запустить контейнеры Docker, выполнить команду на сервере

```
sudo docker compose -f docker-compose.production.yml up -d
```

- После успешной сборки выполнить миграции:
```
sudo docker compose -f docker-compose.production.yml exec -T backend python manage.py migrate --noinput
```

- Создать суперпользователя:
```
sudo docker compose -f docker-compose.production.yml exec -T backend python manage.py createsuperuser
```

- Собрать статику:
```
sudo docker compose -f docker-compose.production.yml exec -T backend python manage.py collectstatic --noinput
```

- Наполнить базу данных:
```
sudo docker compose -f docker-compose.production.yml exec -T backend python manage.py import_csv.py
```

- [@Kamstrim](https://www.github.com/Kamstrim)



