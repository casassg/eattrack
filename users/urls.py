from django.conf.urls import url
from users import views

urlpatterns = [
    url(r'^messenger/$', views.MessengerBotView.as_view()),
    url(r'^test/$', views.test_food),
    url(r'^users/(?P<fbid>\w{0,50})/$', views.analytics, name='user_stats'),
    url(r'^ajax/calories/week.json$', views.LineChartJSONView.as_view(), name='line_chart_json'),

]
