import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import tok, group_id

vk_session = vk_api.VkApi(token = tok)
longpoll = VkLongPoll(vk_session, group_id)