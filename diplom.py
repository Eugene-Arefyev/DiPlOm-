# Дипломная работа: “Шпионские игры”
# Есть вещи, которые объединяют людей, а есть те, которые делают нас индивидуальными. Давайте посмотрим, чем пользователи в ВК не делятся со своими друзьями?

# Задание:
# Вывести список групп в ВК в которых состоит пользователь, но не состоит никто из его друзей.
# В качестве жертвы, на ком тестировать, можно использовать: https://vk.com/tim_leary

# Входные данные:
# имя пользователя или его id в ВК, для которого мы проводим исследование
# Внимание: и имя пользователя (tim_leary) и id (5030613)  - являются валидными входными данными
# Ввод можно организовать любым способом:
# •	из консоли
# •	из параметров командной строки при запуске
# •	из переменной
# Выходные данные:
# файл groups.json в формате
# [
# {
# “name”: “Название группы”,
# “gid”: “идентификатор группы”,
# “members_count”: количество_участников_собщества
# },
# {
# …
# }
# ]
# Форматирование не важно, важно чтобы файл был в формате json


import requests
import json
import time

ACCESS_TOKEN = "7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b7d9fb59859870658c4a0b8fdc4dd494db19099"
USER_ID = "5030613"

URL_TEMPLATE = "https://api.vk.com/method/{}.get?user_id={}&v=5.52&access_token={}"
GROUP_BY_ID_TEMPLATE = "https://api.vk.com/method/groups.getById?group_id={}&fields=members_count&v=5.52&access_token={}"

IDS = [USER_ID]

flag = True


# печатает на экран точку или решетку после каждого запроса к апи вк
def print_alive():
    global flag
    if flag:
        print(".")
    else:
        print('$')
    flag = not flag


# Отправить запрос в апи в зависимости от type (мы отправляем или friends или groups)
def get_data(type, url, user_id):
    url = url.format(type, user_id, ACCESS_TOKEN)
    r = requests.get(url)
    print_alive()
    return r


# Отправить запрос в апи для получения информации о конкретной группе
def get_group_info(id):
    r = requests.get(GROUP_BY_ID_TEMPLATE.format(id, ACCESS_TOKEN))
    print_alive()
    return r


count = 0  # глобальная переменная, если счётчик 3 , то зависает на 1 сек


# Выполнить запросы к апи для каждого переданного id. users_id - массив id
def get_data_by_ids(type, url, users_id):
    global count

    res = []
    for id in users_id:

        if count % 3 == 0:
            time.sleep(1)
        count += 1

        json_data = get_data(type, url, id).text

        # эта проверка нужна для того чтобы определить что запрос прошел успешно, потому что если у нас нет поля response, Это значит что такой пользователь или группа удалена
        if "response" not in json.loads(json_data):
            # print(json_data)
            continue

        res.extend(json.loads(json_data)['response']['items'])

    return set(res)


def format_group_info(info):
    if 'response' not in info:
        return None

    res = dict()

    res['name'] = info['response'][0]["name"]
    res['id'] = info['response'][0]["id"]
    res['members_count'] = info['response'][0]["members_count"]

    return res


friends = get_data_by_ids("friends", URL_TEMPLATE, IDS)
groups = get_data_by_ids("groups", URL_TEMPLATE, friends)
my_groups = get_data_by_ids("groups", URL_TEMPLATE, IDS)

res = my_groups - groups  # убираем похожие группы (a - b) см.test.py

result = []
for i in res:
    data = format_group_info(json.loads(get_group_info(i).text))
    if data is not None:
        result.append(data)

# записываем результат работы в файл!
with open("groups.json", "w", encoding = "utf-8") as f:
    f.write(json.dumps(result, sort_keys=True, indent=4, ensure_ascii=False))
