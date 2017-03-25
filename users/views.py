import json

from django.conf import settings
from django.http import HttpResponse
# Create your views here.
from django.utils.decorators import method_decorator
from django.views import generic
# Helper function
from django.views.decorators.csrf import csrf_exempt
from users import food, wolfram
from users.fb_bot import send_message, user_details


# Bot answers

def initial_text(fbid, recevied_message):
    # Get user details
    details = user_details(fbid)
    response = 'Hi ' + details['first_name'] + ', send me a picture so I can recognize it!'
    send_message(fbid, response)


def analyze_pic(fbid, image_url):
    topics = food.extract(image_url)
    send_message(fbid, 'Choose the correct option:', quick_replies=(topics[:5]))


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
            return HttpResponse('Not correct')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events
                fbid = message['sender']['id']

                # 0th case: No message
                if 'message' not in message:
                    continue
                # 1st case: Image sent by user
                if 'quick_reply' in message['message']:
                    selected = message['message']['quick_reply']['payload']
                    calories = wolfram.get_calories(selected)
                    send_message(fbid, 'This was %s calories' % calories)
                elif 'attachments' in message['message'] and 'image' in map(lambda x: x['type'],
                                                                            message['message']['attachments']):
                    # Analize only first image. TODO: Analize the rest
                    ats = len(message['message']['attachments'])
                    if ats > 1:
                        send_message(fbid, 'Only 1 at a time')
                        continue

                    attachment = message['message']['attachments'][0]
                    if attachment['type'] == 'image':
                        url = attachment['payload']['url']
                        analyze_pic(fbid, url)

                # 3rd case: No message
                elif 'text' in message['message']:
                    initial_text(fbid, message['message']['text'])

        return HttpResponse()
