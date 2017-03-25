from django.conf.urls import url
from users.views import MessengerBotView

urlpatterns = [
    url(r'^messenger/$', MessengerBotView.as_view()),

]
