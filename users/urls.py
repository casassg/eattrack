from django.conf.urls import url
from users.views import MessengerBotView, test_food

urlpatterns = [
    url(r'^messenger/$', MessengerBotView.as_view()),
    url(r'^test/$', test_food),
    url(r'^users/(?P<fbid>\w{0,50})/$', test_food, name='user_stats'),

]
