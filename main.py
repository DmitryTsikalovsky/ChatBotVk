import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from pymongo import MongoClient
import pymongo
import requests
import vk_api, json
from vk_api.longpoll import VkLongPoll, VkEventType

main_token = "8c20fd59534bd074cc126ee189b7d" 

vk_session = vk_api.VkApi(token=main_token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# Подключение к базе данных
client = MongoClient(
    "mongodb+srv://al1ewnare:03092003@chatbotvk.qda4d.mongodb.net/charbotbd?retryWrites=true&w=majority")
db = client["charbotbd"]
colLessons = db["lessons"]
colUsers = db["users"]


def searchLessonsName(instituteName, semestrNumber, colLessons, event, start_key, temp, colUsers, userName):
    lessonsList = colLessons.find({"institutename": instituteName, "semestr": semestrNumber})
    message = "Доступные предметы: \n"
    array = []
    i = 0
    for item in lessonsList:
        array.append(item["lessonname"])
        message = message + str(i + 1) + ")" + item["lessonname"] + "\n"
        i += 1
    write_msg_text(event.user_id, f"Ваши данные: {message}")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                if request.isdigit() and int(request) > i + 1:
                    write_msg_text(event.user_id, "Некорректный ввод данных. Попробуйте еще раз.")
                elif request.isdigit():
                    i = int(request)
                    lessonName = array[i - 1]
                    if temp == 1:
                        message = searchHelp(instituteName, semestrNumber, lessonName, colUsers)
                        write_msg(event.user_id, f"Ваши данные: {message}", start_key)
                        return array[i - 1]
                    if temp == 2:
                        addUserToLesson(event.user_id, instituteName, semestrNumber, lessonName, userName, colUsers)
                        write_msg(event.user_id,
                                "Данные успешно обновлены",
                                start_key)
                        return array[i - 1]
                else:
                    write_msg_text(event.user_id, "Некорректный ввод данных. Попробуйте еще раз.")


def searchHelp(instituteName, semestrNumber, lessonName, colUsers):
    usersList = colUsers.find({"status": True, "lessons": {
        '$elemMatch': {"institutename": instituteName, "semestr": semestrNumber, "lessonname": lessonName}}})
    message = ""
    for item in usersList:
        message = message + "https://vk.com/id" + str(item["vkid"]) + " (" + item["username"] + ")\n"

    return message


def addUserToLesson(vkId, instituteName, semestrNumber, lessonName, userName, colUsers):
    lesson = colLessons.find_one({"institutename": instituteName, "semestr": semestrNumber, "lessonname": lessonName})
    user = colUsers.find_one({"vkid": vkId})
    if user:
        check = colUsers.find_one({"vkid": vkId, "lessons": {
            '$elemMatch': {"institutename": instituteName, "semestr": semestrNumber, "lessonname": lessonName}}})
        if check == None:
            user = colUsers.update_one({"vkid": vkId}, {'$push': {
                "lessons": {"institutename": lesson["institutename"], "semestr": semestrNumber, "lessonname": lessonName}}})
    else:
        colUsers.insert_one({"vkid": vkId, "username": userName, "status": True, "lessons": [
            {"institutename": lesson["institutename"], "semestr": semestrNumber, "lessonname": lessonName}]})

def get_keyboard(buts):
    nb = []
    color = ''
    for i in range(len(buts)):
        nb.append([])
        for k in range(len(buts[i])):
            nb[i].append(None)
    for i in range(len(buts)):
        for k in range(len(buts[i])):
            text = buts[i][k][0]
            color = {'белый': 'secondary', 'красный': 'negative', 'синий': 'primary'}[buts[i][k][1]]
            nb[i][k] = {"action": {"type": "text", "payload": "{\"button\": \"" + "1" + "\"}", "label": f"{text}"},
                        "color": f"{color}"}
    first_keyboard = {'one_time': False, 'buttons': nb}
    first_keyboard = json.dumps(first_keyboard, ensure_ascii=False).encode('utf-8')
    first_keyboard = str(first_keyboard.decode('utf-8'))
    return first_keyboard

def checkUser(vkId, colUsers):
    check = colUsers.find_one({"vkid": vkId})
    if check:
        return 1
    else:
        return 0

def get_name(user_id):
    info = vk_session.method('users.get', {'user_ids': user_id})
    info = info[0]
    first_name = info['first_name']
    last_name = info['last_name']
    name = first_name + ' ' + last_name
    return name

def deleteLesson(vkId, colUsers, index):
    user = colUsers.find_one({"vkid": vkId})
    lesson = user["lessons"][index]
    colUsers.update_one({"vkid": vkId}, {"$pull": {
        "lessons": {"institutename": lesson["institutename"], "semestr": lesson["semestr"],
                    "lessonname": lesson["lessonname"]}}})
    user = colUsers.find_one({"vkid": vkId})
    if user["lessons"]:
        return
    else:
        colUsers.delete_one({"vkid": vkId})


def getUserLessons(vkId, colUsers):
    user = colUsers.find_one({"vkid": vkId})
    i = 1
    if user:
        message = ""
        for lesson in user["lessons"]:
            message = message + str(i) + ")" + str(lesson["semestr"]) + ' семестр ' + lesson["institutename"][0] + ' ' + \
                      lesson["lessonname"] + "\n"  # 1) 1 семестр ИИКС Матанализ
            i += 1
    else:
        message = "У вас нет предметов :("
    return message


def getStatus(vkId, colUsers):
    user = colUsers.find_one({"vkid": vkId})
    if user["status"]:
        return 1
    else:
        return 0

def check_institute(instituteName):
    names = ['ияфит', 'лаплаз', 'ифиб', 'интэл', 'иикс', 'ифтис', 'ифтэб', 'имо', 'фбиукс']
    for name in names:
        if instituteName in name:
            return 1
    return 0

def changeStatus(vkId, colUsers):
    user = colUsers.find_one({"vkid": vkId})
    if user["status"]:
        colUsers.update_one({"vkid": vkId}, {"$set": {"status": False}})
    else:
        colUsers.update_one({"vkid": vkId}, {"$set": {"status": True}})

def write_msg_text(id, text):
    vk_session.method('messages.send', 
                      {'user_id': id, 'message': text, 'random_id': 0})


def write_msg(id, text, key):
    vk_session.method('messages.send', 
                      {'user_id': id, 'message': text, 'random_id': 0, 'keyboard': key})

def message_violation(text):
    vk_session.method('messages.send', {'user_id': '361771852', 'message': f'СООБЩЕНИЕ О НАРУШЕНИИ: \n {text}', 'random_id': 0})

def main():
    users = []

    start_key = get_keyboard(
        [
            [('Начать', 'синий')]
        ]
    )

    choice_key = get_keyboard(
        [
            [('Ищу помощь', 'синий')],
            [('Хочу помочь', 'белый')]
        ]
    )

    choice_zareg_key = get_keyboard(
        [
            [('Ищу помощь', 'синий')],
            [('Мой профиль', 'белый')],
            [('Сообщить о нарушении', 'синий')]
        ]
    )

    profil_key = get_keyboard(
        [
            [('Статус', 'синий')],
            [('Показать предметы', 'белый')],
            [('Добавить предмет', 'синий')],
            [('Удалить предмет', 'белый')]
        ]
    )

    institute_key = get_keyboard(
        [
            [('ИЯФИТ', 'синий'), ('ЛАПЛАЗ', 'белый'), ('ИФИБ', 'синий')],
            [('ИНТЭЛ', 'белый'), ('ИИКС', 'синий'), ('ИФТИС', 'белый')],
            [('ИФТЭБ', 'синий'), ('ИМО', 'белый'), ('ФБИУКС', 'синий')]
        ]
    )

    status_key = get_keyboard(
        [
            [('Показать статус', 'синий')],
            [('Изменить статус', 'белый')]
        ]
    )

    step = 1
    item = 0
    add_lesson = 0
    aktiv_check = 0
    temp_tst = 0
    violation = 0

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                status = checkUser(event.user_id, colUsers)
                request = event.text.lower()
                name = get_name(event.user_id)
                info = vk_session.method('users.get', {'user_ids': event.user_id})
                check = 0

                if step == 1 and status == 0:
                    write_msg(event.user_id, "Выбирайте: ", choice_key)
                    check = 1

                if step == 1 and status == 1:
                    write_msg(event.user_id, "Выбирайте: ", choice_zareg_key)
                    check = 1

                if step == 2 and status == 1 and request == 'мой профиль':
                    write_msg(event.user_id, "Выбирайте: ", profil_key)
                    check = 1

                if violation == 1:
                    message_violation(request)
                    violation = 0
                    check = 1

                if step == 2 and status == 1 and request == 'сообщить о нарушении':
                    write_msg_text(event.user_id, "Введите сообщение, которое будет передано администраторам: ")
                    violation = 1
                    check = 1

                if (step == 3 and status == 1) or (aktiv_check == 1):
                    if request == 'статус' or aktiv_check == 1:
                        if aktiv_check == 0:
                            write_msg(event.user_id, "Выбирайте: ", status_key)
                            aktiv_check = 1
                            check = 1
                        if request == 'показать статус':
                            aktiv = getStatus(event.user_id, colUsers)
                            if aktiv == 1:
                                aktiv = 'Активен'
                            else:
                                aktiv = 'Неактивен'
                            write_msg(event.user_id, f"Ваш статус: '{aktiv}'", start_key)
                            step = 0
                            aktiv_check = 0
                            check = 1
                        if request == 'изменить статус':
                            changeStatus(event.user_id, colUsers)
                            write_msg(event.user_id, "Ваш статус изменен", start_key)
                            step = 0
                            aktiv_check = 0
                            check = 1

                    if request == 'показать предметы':
                        text = getUserLessons(event.user_id, colUsers)
                        write_msg(event.user_id, f"Ваши данные:\n {text}", start_key)
                        step = 0
                        check = 1

                    if request == 'добавить предмет':
                        add_lesson = 1
                        what_want = 'хочу помочь'
                        write_msg(event.user_id, "Выберите институт", institute_key)
                        check = 1

                    if request == 'удалить предмет' or item == 1:
                        if item == 0:
                            text = getUserLessons(event.user_id, colUsers)
                            write_msg_text(event.user_id, f"Выберите предмет для удаления:\n {text}")
                            step -= 1
                            item = 1
                        else:
                            deleteLesson(event.user_id, colUsers, int(request) - 1)
                            write_msg(event.user_id, "Предмет успешно удален", start_key)
                            step = 0
                            item = 0
                        check = 1

                if (step == 2 and status == 0) or (step == 2 and status == 1 and request == 'ищу помощь'):
                    what_want = request
                    write_msg(event.user_id, "Выберите институт", institute_key)
                    temp_tst = 1
                    check = 1

                if (step == 3 and status == 0) or (add_lesson == 2) or (step == 3 and status == 1 and temp_tst == 1):
                    instituteName = request
                    check = check_institute(instituteName)
                    if check == 1:
                        instituteName = instituteName.upper()
                        write_msg_text(event.user_id, "Введите семестр")
                        if temp_tst == 1:
                            temp_tst += 1
                    
                if (step == 4 and status == 0) or (add_lesson == 3) or (step == 4 and status == 1 and temp_tst == 2 and add_lesson == 0):
                    if request.isdigit():
                        semestrNumber = request
                        semestrNumber = int(semestrNumber)
                        if semestrNumber > 0 and semestrNumber < 12:
                            if what_want == 'ищу помощь':
                                lessonsName = searchLessonsName(instituteName, semestrNumber, colLessons, event, start_key,
                                                                1, colUsers, name)
                            if what_want == 'хочу помочь':
                                lessonsName = searchLessonsName(instituteName, semestrNumber, colLessons, event, start_key,
                                                                2, colUsers, name)
                        step = 0
                        add_lesson = 0
                        check = 1

                if check == 1:
                    step += 1
                    if add_lesson != 0:
                        add_lesson += 1
                else:
                    write_msg_text(event.user_id, "Некорректный ввод данных. Попробуйте еще раз.")
                


while True:
    main()
