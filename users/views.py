import json
from logging import info, debug

import requests
from clarifai.rest import ClarifaiApp
from django.conf import settings
from django.http import HttpResponse
# Create your views here.
from django.utils.decorators import method_decorator
from django.views import generic
# Helper function
from django.views.decorators.csrf import csrf_exempt


def answer_text(fbid, recevied_message):
    user_details_url = "https://graph.facebook.com/v2.6/%s" % fbid
    user_details_params = {'fields': 'first_name,last_name,profile_pic', 'access_token': settings.FB_TOKEN}
    user_details = requests.get(user_details_url, user_details_params).json()
    response = 'Yo ' + user_details[
        'first_name'] + ', send me a picture so I can recognize it! You said: ' + recevied_message
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % settings.FB_TOKEN
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": response}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
    info(status.json())


def analyze_food(fbid, image_url):
    # Remove all punctuations, lower case the text and split it based on space

    joke_text = 'Here\'s your description:'
    res_food = food(image_url)
    joke_text += '\n\n\n' + json.dumps(res_food)
    answer_text(fbid, joke_text)


def food(url):
    app = ClarifaiApp(settings.CLARIFAI_APP_ID, settings.CLARIFAI_APP_SECRET)

    # get the general model
    model = app.models.get("food-items-v1.0")

    # predict with the model
    debug(url)
    res = model.predict_by_url(url=url)
    return res


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
                fbid = message['sender']['id']
                if 'message' in message and 'attachments' in message['message'] and 'image' in map(lambda x: x['type'],
                                                                                                   message['message'][
                                                                                                       'attachments']):
                    # Print the message to the terminal

                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly.
                    for attachment in message['message']['attachments']:

                        if attachment['type'] == 'image':
                            url = attachment['payload']['url']
                            analyze_food(fbid,
                                         url)
                            answer_text(fbid, url)
                elif 'message' in message:
                    answer_text(fbid, message['message']['text'])

                info(message)

        return HttpResponse()
