# Проект парсинга pep

## ОПИСАНИЕ ПРОЕКТА
Проект - парсер, который способен собирать информацию о документации Python и PEP.

## ОСОБЕННОСТИ ПРОЕКТА
Проект - консольное приложение Python c обработкой аргументов командной строки

## ЗАПУСК ПРОЕКТА
1. клонировать проект
```
git clone https://github.com/monteg179/bs4_parser_pep.git
```
2. создать, активировать и настроить виртуальное окружение
```
cd bs4_parser_pep
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
3. запустить приложение
```
cd src
python main.py
```

## ИСПОЛЬЗОВАНИЕ ПРОЕКТА
- получение справки
```
python main.py -h
```
- получение информации о нововведениях в Python
```
python main.py whats-new
```
- получение информации о статусах версий Python
```
python main.py latest-versions
```
- загрузка архив с актуальной документацией
```
python main.py download
```
- получение информации о статусах PEP
```
python main.py pep
```

## ТЕХНОЛОГИИ
- Python 3.9
- BeautifulSoup
- requests-cache
- PrettyTable
- tqdm
- csv

## АВТОРЫ
* Сергей Кузнецов - monteg179@yandex.ru


