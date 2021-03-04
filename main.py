import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from pymongo import MongoClient
import pymongo
import requests
import vk_api, json
from vk_api.longpoll import VkLongPoll, VkEventType

main_token = "ee861bd7c946a561144d9a2899379557354701e61c9f44d19ff828e17a5cfc5166822c13addb40fafeefc" # моя группа
#main_token = "8c20fd59534bd074cc126ee189b7d533a06fb0d92c70ba6f9ad629d0e7e956ec2ce599cd6b12b11e377c8" # чат бот в группе

#Подключение к вк
vk_session = vk_api.VkApi(token=main_token)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

#Подключение к базе данных
client = MongoClient("mongodb+srv://al1ewnare:03092003@chatbotvk.qda4d.mongodb.net/charbotbd?retryWrites=true&w=majority")
db = client["charbotbd"]
colLessons = db["lessons"]
colUsers = db["users"]

def searchLessonsName(instituteName, semestrNumber, colLessons, event, start_key, temp):
    lessonsList = colLessons.find({"institutename": instituteName, "semestr": semestrNumber})
    message = "Доступные предметы: \n"
    array = []
    i = 0
    for item in lessonsList:
        array.append(item["lessonname"])
        message = message + str(i+1) + ")" + item["lessonname"] + "\n"
        i += 1
    write_msg_text(event.user_id, f"Ваши данные: {message}")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                i = int(request)
                lessonName = array[i-1]
                if temp == 1:
                    message = searchHelp(instituteName, semestrNumber, lessonName, colUsers)
                    write_msg(event.user_id, f"Ваши данные: {message}", start_key) 
                    return array[i-1]
                if temp == 2:
                    addUserToLesson(event.user_id, instituteName, semestrNumber, lessonName, colUsers)
                    write_msg(event.user_id, f"Данные успешно обновлены {event.user_id}, {instituteName}, {semestrNumber}, {lessonName}", start_key)
                    return array[i-1]


def searchHelp(instituteName, semestrNumber, lessonName, colUsers):
    usersList = colUsers.find({"status": True,"lessons": { '$elemMatch': {"institutename": instituteName, "semestr": semestrNumber, "lessonname":lessonName}}})
    message = ""
    for item in usersList:
        message = message + "https://vk.com/id" + str(item["vkid"]) + " (" + item["username"] + ")\n"

    return message 

def addUserToLesson(vkId, instituteName, semestrNumber,lessonName, colUsers):
    check = colUsers.find_one({"vkid": vkId, "lessons": { '$elemMatch': {"institutename": instituteName, "semestr": semestrNumber, "lessonname":lessonName}}})
    if check == None:
        user = colUsers.update_one({"vkid": vkId}, { '$push': { "lessons": { "institutename": instituteName, "semestr": semestrNumber, "lessonname": lessonName } } })


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
            nb[i][k] = {"action": {"type": "text", "payload": "{\"button\": \"" + "1" + "\"}", "label": f"{text}"}, "color": f"{color}"}
    first_keyboard = {'one_time': False, 'buttons': nb}
    first_keyboard = json.dumps(first_keyboard, ensure_ascii=False).encode('utf-8')
    first_keyboard = str(first_keyboard.decode('utf-8'))
    return first_keyboard

def write_msg_text(id, text):
    vk_session.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0})

def write_msg(id, text, key):
    vk_session.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0, 'keyboard': key})

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

    institute_key = get_keyboard(
        [
            [('ИЯФИТ', 'синий'), ('ЛАПЛАЗ', 'белый'), ('ИФИБ', 'синий')],
            [('ИНТЭЛ', 'белый'), ('ИИКС', 'синий'), ('ИФТИС', 'белый')],
            [('ИФТЭБ', 'синий'), ('ИМО', 'белый'), ('ФБИУКС', 'синий')]
        ]
    )
    while(True):
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text.lower()
                    id = event.user_id
                    if request == 'начать':
                        write_msg(event.user_id, "Выбирайте:", choice_key)
                        for event in longpoll.listen():
                            if event.type == VkEventType.MESSAGE_NEW:
                                if event.to_me:
                                    request = event.text.lower()
                                    what_want = request
                        
                                    write_msg(event.user_id, "Выберите институт", institute_key)
                                    for event in longpoll.listen():
                                        if event.type == VkEventType.MESSAGE_NEW:
                                            if event.to_me:
                                                request = event.text.lower()
                                                instituteName = request
                                                write_msg_text(event.user_id, "Введите семестр")
                                                for event in longpoll.listen():
                                                    if event.type == VkEventType.MESSAGE_NEW:
                                                        if event.to_me:
                                                            request = event.text.lower()
                                                            semestrNumber = request
                                                            semestrNumber = int(semestrNumber)
                                                            instituteName = instituteName.upper()
                                                            if semestrNumber>0 and semestrNumber<12:
                                                                if what_want == 'ищу помощь':
                                                                    lessonsName = searchLessonsName(instituteName, semestrNumber, colLessons, event, start_key, 1)
                                                                if what_want == 'хочу помочь':
                                                                    lessonsName = searchLessonsName(instituteName, semestrNumber, colLessons, event, start_key, 2)


while True:
    main()
