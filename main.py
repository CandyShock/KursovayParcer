import json

from classes import HeadHunter, Superjob, Connector


def main():
    vacancies_json = []
    keyword = input()
    page_count = int(input("Введите количество страниц для получения вакансий "))
    service_filter = input('Выберите сервис для поиска\n'
                           '1 - HeadHunter\n'
                           '2 - Superjob\n'
                           '3 - оба сервиса\n'
                           'exit - выход\n')

    hh = HeadHunter(keyword)
    sj = Superjob(keyword)

    if service_filter == 'exit':
        exit()
    elif service_filter == '1':
        hh.get_vacancies(page_count=page_count)
        vacancies_json.extend(hh.format_vacancies())
    elif service_filter == '2':
        sj.get_vacancies(page_count=page_count)
        vacancies_json.extend(sj.format_vacancies())
    elif service_filter == '3':
        for api in (hh, sj):
            api.get_vacancies(page_count=page_count)
            vacancies_json.extend(api.format_vacancies())




    connector = Connector(keyword=keyword, vacancies_json=vacancies_json)

    while True:
        command = input(
            '1 - вывести список вакансий\n'
            '2 - отсортировать по мин зп\n'
            '3 - отсортировать по макс зп\n'
            '4 - удалить вакансию по id\n'
            'exit - выход\n'
        )
        if command.lower() == 'exit':
            break
        elif command == '1':
            vacancies = connector.select()
        elif command == '2':
            vacancies = connector.sorted_vacancies_min()
        elif command == '3':
            vacancies = connector.sorted_vacancies_max()
        elif command == '4':
            vacancy_name = input("Введите название вакансии ")
            with open(f"{vacancy_name}.json", encoding="utf8") as file:
                dict_ = json.load(file)
            num = 0
            for i in dict_:
                print(f"{i['id']}:{num}")
                num += 1

            vacancy_del = int(input("введите порядковый номер id вакансии для удаления "))
            del dict_[vacancy_del]

            with open(f"{vacancy_name}", "w", encoding="utf8") as file:
                json.dump(dict_, file, ensure_ascii=False, indent=4)

        for vacancy in vacancies:
             print(vacancy, end='\n\n')




if __name__ == "__main__":
    main()
