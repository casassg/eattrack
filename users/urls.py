from django.conf.urls import url
from users.views import food, MessengerBotView

urlpatterns = [
    url(r'^test/$', food),
    url(r'^messenger/$', MessengerBotView.as_view())
]
