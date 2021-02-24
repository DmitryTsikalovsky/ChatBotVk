import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import tok, group_id
from pymongo import MongoClient
import pymongo
client = pymongo.MongoClient("mongodb+srv://al1ewnare:03092003@chatbotvk.qda4d.mongodb.net/charbotbd?retryWrites=true&w=majority")
db = client.test
vk_session = vk_api.VkApi(token = tok)
longpoll = VkLongPoll(vk_session, group_id)
