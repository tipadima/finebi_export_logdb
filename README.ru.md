# FineBI logdb ElasticSearch to MySQL Exporter

Скрипт предназначен для копирования содержимого logdb хранящегося в ElasticSearch в сторонюю базу. Актуальная версия предназначения для использования с FineBI версии 6.1.1+ и MySQL версии 5.4+. Скрипт анализирует наличие индексов в ElasticSerch и создает одноименные таблицы в MySQL, если они там отсутсвуют. Далее получает из базы последнюю запись и копирует из ElasticSearch все записи старше последней.

## Структура проекта

- **docker/**
  - `Dockerfile` - докерфайл для запуска скрипта
- **example/**
  - `config.json` - пример конфигурационного файла для запуска скрипта
- `requirements.txt` - зависимости пакетов
- `connect.py` - библиотека для подключения к ElasticSearch и MySQL
- `main.py` - основной скрипт


## Пример использования

Собрать образ.
```
docker build . -f ./docker/Dockerfile -t finebi_export_logdb
```

Создать базу данных в MySQL указанную в конфигурационном файле.
Добавить в cron запуск.
```
*/1 * * * * /usr/bin/docker run --rm -v /opt/finebi_export_logdb/config.json:/opt/app/config.json finebi_export_logdb:latest
```

## Структура конфигурационного файла

```
{
    "elasticsearch": {                           # Блок подключения к ElasticSearch
        "address": "http://elasticsearch:9200",  # Адрес подключения
        "username": "elastic",                   # Имя пользователя
        "password": "elastic"                    # Пароль пользователя
    },
    "mysql": {                                   # Блок подключения к MySQL
        "address": "mysql:3306",                 # Адрес подключения
        "database": "logdb",                     # Название базы данных (по умолчанию: logdb)
        "username": "root",                      # Имя пользователя
        "password": "root",                      # Пароль пользователя
        "batch_size": 1000                       # размер пачки для вставки в MySQL (по умолчанию: 1000)
    },
    "log_level": "INFO"                          # Уровень логгирования (DEBUG, по умолчанию: INFO)
}

```

Допускается передача конфигурации переменными коружения, например
```
docker run \
    --rm \
    -e elasticsearch.address='http://elasticsearch:9200' \
    -e elasticsearch.username=elastic \
    -e elasticsearch.password=elastic \
    -e mysql.address='mysql:3306' \
    -e mysql.username=root \
    -e mysql.password=root \
    finebi_export_logdb:latest
```
