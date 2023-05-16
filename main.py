from pprint import pprint

from classes import HeadHunter, Superjob, Connector


def main():
    vacancies_json = []
    keyword = "Python"

    hh = HeadHunter(keyword)
    sj = Superjob(keyword)
    for api in (hh, sj):
        api.get_vacancies(page_count=2)
        vacancies_json.extend(api.format_vacancies())

    pprint(vacancies_json)

    connector = Connector(keyword=keyword, vacancies_json=vacancies_json)

    while True:
        command = input(
            '1 - вывести список вакансий\n'
            '2 - отсортировать по мин зп\n'
            'exit - выход\n'
        )
        if command.lower() == 'exit':
            break
        elif command == '1':
            vacancies = connector.select()
        elif command == '2':
            vacancies = connector.sorted_vacancies()

        for vacancy in vacancies:
             print(vacancy, end='\n\n')


if __name__ == "__main__":
    main()
