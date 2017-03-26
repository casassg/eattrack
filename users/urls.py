from django.conf.urls import url
from users.views import MessengerBotView, test_food, analytics

urlpatterns = [
    url(r'^messenger/$', MessengerBotView.as_view()),
    url(r'^test/$', test_food),
    url(r'^users/(?P<fbid>\w{0,50})/$', analytics, name='user_stats'),

]
