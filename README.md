
# дипломный проект — сайт Foodgram, «Продуктовый помощник»

Приложение «Продуктовый помощник»: Онлайн-сервис и API для него. Сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Инфраструктура

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
Kamstrim
12345

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

## Authors

- [@Kamstrim](https://www.github.com/Kamstrim)



