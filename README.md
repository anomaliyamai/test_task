# Тестовое задание

Запустить проект можно следующим образом:

- Соберем докер-образ из директории с проектом при помощи:

`docker build -t deposit-service .`

- Далее запускаем контейнер с настроенным портом и хостом:

` docker run -d --name deposit-service -e HOST='0.0.0.0' -e PORT='8000' -p 8000:8000 deposit-service`

Unit-тесты можно посмотреть [здесь](https://github.com/anomaliyamai/test_task/blob/main/app/test_app.py)