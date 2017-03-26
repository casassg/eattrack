import json
from datetime import datetime

from chartjs.views.lines import BaseLineChartView
from django.conf import settings
from django.db.models import Sum
from django.db.models.functions import TruncDay
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from users import food, wolfram, fb_bot, models
from users.utils import reverse

OTHER_VALUE = 'Other'


# Bot answers

def initial_text(fbid, recevied_message):
    # Get user details
    details = fb_bot.user_details(fbid)
    fb_bot.send_message(fbid, 'Welcome ' + details['first_name'] + ', let me help you keep track of what you eat.')
    fb_bot.send_message(fbid, ' Just send me a picture of what you are eating so I can recognize it!')


# Test request. TODO: DELETE THIS
def test_food(request):
    res = food.extract(
        'https://scontent.xx.fbcdn.net/v/t34.0-12/17496094_10208759653813233_938158810_n.jpg?_nc_ad=z-m&oh=479263e3f66abfc57b82db0bafe37062&oe=58D85803')
    return HttpResponse(json.dumps(res))


class MessengerBotView(generic.View):
    """
    Main messenger view
    """

    def get(self, request, *args, **kwargs):
        token = request.GET.get('hub.verify_token', '')
        if token == settings.FB_TOKEN:
            return HttpResponse(request.GET['hub.challenge'])
        else:
            return HttpResponse('BIENE')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                fbid = message['sender']['id']

                # Try and save the user
                user = models.AppUser()
                user.fbid = fbid
                user.save()

                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events

                # 0th case: No message
                if 'message' not in message:
                    continue

                if 'quick_reply' in message['message']:
                    quick_reply = message['message']['quick_reply']['payload']
                    # 1.1 case: Quick reply with quantity
                    if ';' in quick_reply:
                        product, calories = quick_reply.split(';')

                        fb_bot.send_message(fbid, 'You are having %s calories' % calories)

                        # Save new food reading
                        reading = models.Reading()
                        reading.calories = calories
                        reading.user = user
                        reading.product = product
                        reading.timestamp = datetime.now()
                        reading.save()
                        continue
                    # 1.2 case: Quick reply with product
                    try:
                        product = quick_reply
                        calories = float(wolfram.get_calories(product))
                    except ValueError as e:
                        fb_bot.send_message(fbid, 'I couldn\'t find calories for this product')
                        continue

                    top_funct = {
                        'half': lambda x: x / 2.0,
                        'third part': lambda x: x / 3.0,
                        'quarter part': lambda x: x / 4.0,
                        'an eigth': lambda x: x / 8.0,
                        '1 full': lambda x: x,
                        '2 of them': lambda x: x * 2.0,
                    }

                    qr = fb_bot.create_quick_replies_quantities(top_funct, calories, quick_reply)
                    fb_bot.send_message(fbid, "How much are you having?", quick_replies=qr)
                # 2nd case: Image sent to be recognized
                elif 'attachments' in message['message'] and 'image' in map(lambda x: x['type'],
                                                                            message['message']['attachments']):
                    # Analize only first image. TODO: Analize the rest
                    ats = len(message['message']['attachments'])
                    if ats > 1:
                        fb_bot.send_message(fbid, 'Only 1 at a time please! They haven\'t taught me better!')
                        continue

                    attachment = message['message']['attachments'][0]
                    if attachment['type'] == 'image':
                        url = attachment['payload']['url']
                        topics = food.extract(url)
                        fb_bot.send_message(fbid, 'What\'s the closest guess?', topics=(topics[:5]))

                # 3rd case: No message
                elif 'text' in message['message']:
                    text = message['message']['text']
                    if 'stats' in text.lower() or 'data' in text.lower():
                        url = reverse('user_stats', kwargs={'fbid': fbid}, request=request)
                        fb_bot.send_message(fbid, "Here are your usage stats, just for you!\n\n" + url)
                        continue
                    initial_text(fbid, text)
                else:
                    fb_bot.send_message(fbid, "I'm sorry, I couldn't understand you.")

        return HttpResponse()


def analytics(request, fbid):
    readings = models.Reading.objects.filter(user_id=fbid)
    return render(request, 'analytics.html', context={'readings': readings, 'fbid': fbid}, )


class LineChartJSONView(BaseLineChartView):
    def get_labels(self):
        """Return 7 labels."""
        return ["Monday", "Tuesday", "March", "April", "May", "June", "July"]

    def get_data(self):
        """Return 3 datasets to plot."""
        fbid = self.request.GET.get('fbid', '')
        readings = models.Reading.objects.filter(user_id=fbid).annotate(day=TruncDay('timestamp')).values(
            'day').annotate(
            t_calories=Sum('calories')).values('day', 't_calories')
        cals = list(map(lambda x: x['t_calories'], readings))
        res = []
        for i in range(7):
            if len(cals) + i >= 7:
                res += [cals[6 - i], ]
            else:
                res += [0, ]

        return [res, [], []]
