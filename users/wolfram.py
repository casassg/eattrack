import requests
from django.conf import settings

QUERY_WOLFRAM = "http://api.wolframalpha.com/v1/result"


def get_calories(food):
    res = requests.get(QUERY_WOLFRAM, params={'appid': settings.WOLFRAM_ID, 'i': 'calories ' + food})
    return res.content.split(' ')[0]
