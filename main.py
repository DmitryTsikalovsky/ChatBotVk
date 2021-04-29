import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from pymongo import MongoClient
import time
import pymongo
import requests
import vk_api, json
from vk_api.longpoll import VkLongPoll, VkEventType

# main_token = "8c20fd59534bd074cc126ee189b7d533a06fb0d92c70ba6f9ad629d0e7e956ec2ce599cd6b12b11e377c8" # чат бот в группе

# # Подключение к вк
# vk_session = vk_api.VkApi(token=main_token)
# session_api = vk_session.get_api()
# longpoll = VkLongPoll(vk_session)

# Подключение к базе данных
client = MongoClient(
    "mongodb+srv://al1ewnare:03092003@chatbotvk.qda4d.mongodb.net/charbotbd?retryWrites=true&w=majority")
db = client["charbotbd"]
colLessons = db["lessons"]
colUsers = db["users"]
colLink = db["literature"]



def searchLink(instituteName, semestrNumber, lessonName, colLink):
    LinkList = colLink.find({"institutename": instituteName, "semestr": semestrNumber, "lessonname": lessonName})
    message = ""
    i = 1
    for item in LinkList:
        message = message + str(i) + ")" +item["title"] + "\n"
        if len(item["autors"]) != 0:
            autormessage = "Авторы: "
            for autor in item["autors"]:
                autormessage = autormessage + autor + " "
            message = message + autormessage + "\n"
        message = message + item["href"] + "\n"
        i += 1
    return message


result = searchLink(["ИИКС"], 1, "Математический анализ", colLink)
a = result

def addLink(instituteName, semestrNumber, lessonName, title, autors , href, colLnik):
        colLnik.insert_one({"institutename": instituteName, "semestr": semestrNumber, "lessonname": lessonName, "title": title, "autors": autors, "href": href})
addLink(["ИИКС"], 1,"Математический анализ","Кр 2 Окороков", [], "lalla", colLink)


