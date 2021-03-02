import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import tok, group_id
from pymongo import MongoClient
import pymongo

client = MongoClient("mongodb+srv://al1ewnare:03092003@chatbotvk.qda4d.mongodb.net/charbotbd?retryWrites=true&w=majority")
db = client["charbotbd"]
colLessons = db["lessons"]
colUsers = db["users"]

def searchLessonsName(instituteName, semestrNumber, colLessons):
    lessonsList = colLessons.find({"institutename": instituteName, "semestr": semestrNumber})
    message = "Доступные предметы: \n"
    array = []
    i = 0
    for item in lessonsList:
        array.append(item["lessonname"])
        message = message + str(i+1) + ")" + item["lessonname"] + "\n"
        i += 1

    #Отправляем сформированное сообщение, получаем цифру, выбранную пользователем, и возвращаем имя предмата
    return array[i-1] #Поменять на номер (на один меньше) который присылает пользователь

#message = searchLessonsName("ИИКС", 1, colLessons)

def searchHelp(instituteName, semestrNumber, lessonName, colUsers):
    usersList = colUsers.find({"status": True,"lessons": { '$elemMatch': {"institutename": instituteName, "semestr": semestrNumber, "lessonname":lessonName}}})
    message = ""
    for item in usersList:
        message = message + "@" + item["vkid"] + "(" + item["username"] + ")\n"

    return message

#searchHelp("ИИКС", 1, "Матанализ", colUsers)

def addUserToLesson(vkId, instituteName, semestrNumber,lessonName, colUsers):
    check = colUsers.find_one({"vkid": vkId, "lessons": { '$elemMatch': {"institutename": instituteName, "semestr": semestrNumber, "lessonname":lessonName}}})
    if check == None:
        user = colUsers.update_one({"vkid": vkId}, { '$push': { "lessons": { "institutename": instituteName, "semestr": semestrNumber, "lessonname": lessonName } } })

# addUserToLesson("03092003", "ИИКС", 1, "Маанализ", colUsers )


# vk_session = vk_api.VkApi(token = tok)
# longpoll = VkLongPoll(vk_session, group_id)
