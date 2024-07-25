![status workflow](https://github.com/k0sdm1/foodgram/actions/workflows/main.yml/badge.svg)

`Python` `Django` `Django Rest Framework` `Docker` `Gunicorn` `NGINX` `PostgreSQL` `Yandex Cloud` `Continuous Integration` `Continuous Deployment`

# **_Foodgram_**
Foodgram - «Продуктовый помощник». Онлайн-сервис и API для него. На этом сервисе пользователи публикуют свои рецепты, подписываются на публикации других пользователей, добавляют понравившиеся рецепты в список «Избранное», а перед походом в магазин могут скачать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

**_Ссылка на [проект](https://yaclfoodgram.ddns.net "Гиперссылка к проекту.")_**

**_Ссылка на [админ-зону](https://yaclfoodgram.ddns.net/admin "Гиперссылка к админке.")_**

**_Ссылка на документацию к [API](https://yaclfoodgram.ddns.net/api/docs/ "Гиперссылка к API.") с актуальными адресами. Здесь описана структура возможных запросы и ожидаемых ответов_**

### _Развернуть проект на удаленном сервере:_

**_Клонировать репозиторий:_**
```
git clone https://github.com/k0sdm1/foodgram.git
```
**_Установить на сервере Docker, Docker Compose:_**
```
sudo apt install curl                                   - установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      - скачать скрипт для установки
sh get-docker.sh                                        - запуск скрипта
sudo apt-get install docker-compose-plugin              - последняя версия docker compose
```
**_Скопировать на сервер файлы docker-compose.production.yml, из папки infra (команды выполнять находясь в папке infra):_**
```
scp -i путь_до_ssh_ключей/имя_приватного_ключа docker-compose.production.yml username@IP:/home/username/infra

# username - имя пользователя на сервере
# IP - публичный IP сервера
```

**_Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:_**
```
SECRET_KEY              - секретный ключ Django проекта
DOCKER_PASSWORD         - пароль от Docker Hub
DOCKER_USERNAME         - логин Docker Hub
HOST                    - публичный IP сервера
USER                    - имя пользователя на сервере
PASSPHRASE              - *если ssh-ключ защищен паролем
SSH_KEY                 - приватный ssh-ключ
TELEGRAM_TO             - ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          - токен бота, посылающего сообщение
```

**_Создать и запустить контейнеры Docker, выполнить команду на сервере (версии команд "docker compose" или "docker-compose" отличаются в зависимости от установленной версии Docker Compose):**_
```
sudo docker compose -f docker-compose.production.yml up -d
```
**_Выполнить миграции:_**
```
sudo docker compose exec backend python manage.py migrate
```
**_Собрать статику:_**
```
sudo docker compose exec backend python manage.py collectstatic --noinput
```
**_Наполнить базу данных содержимым из файла ingredients.json:_**
```
sudo docker compose exec backend python manage.py fill_db_from_csv "/app/data"
```
**_Создать суперпользователя:_**
```
sudo docker compose exec backend python manage.py createsuperuser
```
**_Для остановки контейнеров Docker:_**
```
sudo docker compose down -v      - с их удалением
sudo docker compose stop         - без удаления
```
### После каждого обновления репозитория (push в ветку master) будет происходить:

1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
2. Тестирование бэкэнда
3. Сборка и доставка докер-образов frontend и backend на Docker Hub
4. Разворачивание проекта на удаленном сервере
5. Отправка сообщения в Telegram в случае успеха

### Локальный запуск проекта:

**_Склонировать репозиторий к себе_**
```
git clone https://github.com/k0sdm1/foodgram.git
```

**_В основной директории создать файл .env и заполнить своими данными:_**
```
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

**_Создать и запустить контейнеры Docker, как указано выше._**

**_После запуска проект будут доступен по адресу: http://localhost/_**

**_Документация будет доступна по адресу: http://localhost/api/docs/_**


### Автор
Бэкэнд: k0sdm1

