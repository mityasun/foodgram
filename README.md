## Проект Foodgram - сайта с рецептами.

***Здесь вы можете создавать рецепты, добавлять их в избранное, добавлять их в список покупок и скачивать список покупок. Также можно подписываться на других авторов рецептов.***

### Возможности API:
- Регистрация пользователей и токен авторизации (Simple JWT).
- Получение, создание, обновление, удаление учетных записей.
- Получение, создание, обновление, удаление произведений.
- Получение, создание, удаление категорий произведений и их жанров.
- Получение, создание, обновление, удаление отзывов и комментариев.

Подробней [по ссылке](http://localhost/api/redoc/)<br>
<sub>Ссылка откроется после развертывания проекта.</sub>
<br>
### Технологии
![Python](https://img.shields.io/badge/Python-3.9.8-%23254F72?style=for-the-badge&logo=python&logoColor=yellow&labelColor=254f72)
![Django](https://img.shields.io/badge/Django-3.2.16-0C4B33?style=for-the-badge&logo=django&logoColor=white&labelColor=0C4B33)
![Django REST](https://img.shields.io/badge/Django%20REST-3.12.4-802D2D?style=for-the-badge&logo=django&logoColor=white&labelColor=802D2D)
![REACT](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=white&labelColor=20232A)
![PostGres](https://img.shields.io/badge/PostGres-31648D?style=for-the-badge&logo=postgresql&logoColor=white&labelColor=31648D)


### Как запустить проект:

Клонировать репозиторий и перейти в него в терминале:

```
git clone https://github.com/mityasun/foodgram-project-react.git
```

Перейдите в директорию с настройками Docker-compose:

```
cd foodgram-project-react/infra/
```

Создать файл .env в этой директории пропишите в нем:

```
SECRET_KEY=*Секретный ключ Django*
DEBUG=*False для прода и True для тестов*
ALLOWED_HOSTS=*Список разрешенных хостов*
DB_NAME=*Имя БД*
POSTGRES_USER=*Имя пользователя БД*
POSTGRES_PASSWORD=*Пароль пользователя БД*
DB_HOST=db
DB_PORT=5432
```

Запустите образ из файла Docker-compose:
```
docker-compose up -d --build
```

Примените миграции:

```
docker-compose exec backend python manage.py migrate
```

Соберите статику:

```
docker-compose exec backend python manage.py collectstatic --no-input
```

Заполнить базу данными из копии::

```
docker-compose exec backend python manage.py loaddata fixtures.json
```

Создайте суперпользователя:

```
docker-compose exec backend python manage.py createsuperuser
```

<br>

### Импорт данных из csv для наполнения базы:

В терминале наберите команду:

```
docker-compose exec backend python manage.py load_csv_data
```

В терминале отобразится результат импорта.<br>
Если какой-либо из файлов отсутствует, то он не будет импортирован.

Примеры файлов csv для наполнения базы находятся в папке recipes/management/data/*.csv:
- tags.csv - файл для заполнения таблицы тегов.
- ingredients.csv - файл для заполнения таблицы ингредиентов.
<br>

Авторы проекта:
<br>
Петухов Артем [Github](https://github.com/mityasun)
