import json
import os
from abc import ABC, abstractmethod


import requests


class Basis(ABC):
    """Абстрактный класс для работы с API"""

    @abstractmethod
    def get_request(self):
        pass

    @abstractmethod
    def get_vacancies(self):
        pass


class Vacancy:
    "Класс для работы с вакансиями"
    __slots__ = ('id', 'title', 'url', 'salary_from', 'salary_to', 'employer', 'api')

    def __init__(self, vacancy_id, title, url, salary_from, salary_to, employer, api):
        self.id = vacancy_id
        self.title = title
        self.url = url
        self.salary_to = salary_to
        self.salary_from = salary_from
        self.employer = employer
        self.api = api

    def __gt__(self, other):
        if not other.salary_from:
            return True
        elif not self.salary_from:
            return False
        return self.salary_from >= other.salary_from

    def __str__(self):
        """ Метод для предоставления информации о вакансии"""
        salary_from = f"От {self.salary_from}" if self.salary_from else '' # проверка наличия мин зп
        salary_to = f"До {self.salary_to}" if self.salary_to else '' # наличие макс зп
        if self.salary_from is None and self.salary_to is None:
            salary_from = "Не указана" # если нет то не указана
        return f"Вакансия : \"id: {self.id}\" \n{self.title}\" \nКомпания: \"{self.employer}\" \nЗарплата: {salary_from} {salary_to} \nURL: {self.url} \nСайт: {self.api}"


class Connector:
    """Класс для работы с пользовательскими функциями"""
    def __init__(self, keyword, vacancies_json):
        self.__filename = f"{keyword.title()}.json"
        self.insert(vacancies_json)

    def insert(self, vacancies_json):
        with open(self.__filename, 'w', encoding='utf-8') as file:
            json.dump(vacancies_json, file, ensure_ascii=False, indent=4)

    def select(self):
        with open(self.__filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
        vacancies = [Vacancy(x['id'], x['title'], x['url'], x['salary_from'], x['salary_to'], x['employer'], x['api'])
                     for x in data]
        return vacancies

    def sorted_vacancies_min(self):
        """Сортировка по минимальной зп"""
        vacancies = self.select()
        vacancies = sorted(vacancies, reverse=True)
        return vacancies

    def sorted_vacancies_max(self):
        """Сортировка по минимальной зп"""
        vacancies = self.select()
        vacancies = sorted(vacancies, reverse=False)
        return vacancies


class HeadHunter(Basis):
    def __init__(self, keyword):
        self.__header = {
            "User Agent": "Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"
        }

        self.__param = {
            "text": keyword,
            "page": 0,
            "per_page": 50,
        }
        self.__vacancies = []

    def get_request(self):
        """Запрос по api"""
        response = requests.get('https://api.hh.ru/vacancies',
                                headers=self.__header,
                                params=self.__param)
        return response.json()['items']

    def get_vacancies(self, page_count=1):
        """Получает список страниц и перебирает пока не дойдет до количества страниц"""
        while self.__param['page'] < page_count:
            print(f"HeadHunter, парсинг страницы, {self.__param['page'] + 1}", end=": ")
            value = self.get_request()
            print(f"Найдено {len(value)} вакансий")
            self.__vacancies.extend(value)
            self.__param['page'] += 1

    @staticmethod
    def get_salary(salary):
        """Метод проверки зарплаты, умножается на примерный курс"""
        formated_salary = [None, None]
        if salary and salary['from'] and salary['from'] != 0:
            formated_salary[0] = salary['from'] if salary['currency'].lower() == 'rur' else salary['from'] * 78
        if salary and salary['to'] and salary['to'] != 0:
            formated_salary[1] = salary['to'] if salary['currency'].lower() == 'rur' else salary['to'] * 78
        return formated_salary

    def format_vacancies(self):
        """Добавление вакансий в список, по параметрам"""
        format_vacancies = []
        for vacancy in self.__vacancies:
            salary_from, salary_to = self.get_salary(vacancy['salary'])
            format_vacancies.append({
                'id': vacancy['id'],
                'title': vacancy['name'],
                'url': vacancy['alternate_url'],
                'salary_from': salary_from,
                'salary_to': salary_to,
                'employer': vacancy['employer']['name'],
                'api': 'HeadHunter',
            })
        return format_vacancies


class Superjob(Basis):
    def __init__(self, keyword):
        self.__header = {"X-Api-App-Id": os.getenv("SJ_API_KEY")}
        self.__param = {
            "keyword": keyword,
            "page": 0,
            "count": 50,
        }
        self.__vacancies = []

    def get_request(self):
        """Запрос по api"""
        response = requests.get('https://api.superjob.ru/2.0/vacancies',
                                headers=self.__header,
                                params=self.__param)
        return response.json()['objects']

    def get_vacancies(self, page_count=1):
        """Получает список страниц и перебирает пока не дойдет до количества страниц"""
        while self.__param['page'] < page_count:
            print(f"Superjob, парсинг страницы, {self.__param['page'] + 1}", end=": ")
            value = self.get_request()
            print(f"Найдено {len(value)} вакансий")
            self.__vacancies.extend(value)
            self.__param['page'] += 1

    def format_vacancies(self):
        """Добавление вакансий в список, по параметрам"""
        format_vacancies = []
        for vacancy in self.__vacancies:
            format_vacancies.append({
                'id': vacancy['id'],
                'title': vacancy['profession'],
                'url': vacancy['link'],
                'salary_from': self.get_salaray(vacancy['payment_from'], vacancy['currency']),
                'salary_to': self.get_salaray(vacancy['payment_to'], vacancy['currency']),
                'employer': vacancy['firm_name'],
                'api': 'Superjob'
            })
        return format_vacancies

    @staticmethod
    def get_salaray(salary, currency):
        """Проверка валюты, если не рубль, умножается на примерный курс"""
        formated_salary = None
        if salary and salary != 0:
            formated_salary = salary if currency == 'rub' else salary * 78
        return formated_salary
