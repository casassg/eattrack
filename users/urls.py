from django.conf.urls import url
from users.views import food, messenger

urlpatterns = [
    url(r'^test/$', food),
    url(r'^messenger/$', messenger)
]
