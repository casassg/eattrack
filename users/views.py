import json
from pprint import pprint

import requests
from clarifai.rest import ClarifaiApp
from django.conf import settings
from django.http import HttpResponse
# Create your views here.
from django.utils.decorators import method_decorator
from django.views import generic
# Helper function
from django.views.decorators.csrf import csrf_exempt


def analyze_food(fbid, recevied_message):
    # Remove all punctuations, lower case the text and split it based on space

    user_details_url = "https://graph.facebook.com/v2.6/%s" % fbid
    user_details_params = {'fields': 'first_name,last_name,profile_pic', 'access_token': settings.FB_TOKEN}
    user_details = requests.get(user_details_url, user_details_params).json()
    joke_text = 'Yo ' + user_details['first_name'] + '..! '
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % settings.FB_TOKEN
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": joke_text}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    pprint(status.json())


def food(request):
    app = ClarifaiApp(settings.CLARIFAI_APP_ID, settings.CLARIFAI_APP_SECRET)

    # get the general model
    model = app.models.get("food-items-v1.0")

    # predict with the model
    res = model.predict_by_url('')
    return HttpResponse(json.dumps(res))


class MessengerBotView(generic.View):
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
                if 'message' in message and 'attachments' in message['message']:
                    # Print the message to the terminal
                    pprint(message)
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly.
                    analyze_food(message['sender']['id'], message['message']['text'])
                else:
                    analyze_food(message['sender']['id'], message['message']['text'])

        return HttpResponse()
