from django.conf.urls import url
from users.views import MessengerBotView, test_food

urlpatterns = [
    url(r'^messenger/$', MessengerBotView.as_view()),
    url(r'^test/$', test_food),

]
