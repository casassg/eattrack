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
        'first_name'] + ', send me a picture so I can recognize it!'
    send_message(fbid, response)


def send_message(fbid, answer, quick_replies=None):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % settings.FB_TOKEN
    if quick_replies:
        response = {"recipient": {"id": fbid}, "message": {"text": answer, 'quick_replies': quick_replies}}
    else:
        response = {"recipient": {"id": fbid}, "message": {"text": answer}}
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=json.dumps(response))
    info(status.json())


def analyze_food(fbid, image_url):
    # Remove all punctuations, lower case the text and split it based on space

    topics = food(image_url)
    qr = [{'content_type': 'text', 'title': topic, 'payload': topic} for topic in topics[:5]]

    send_message(fbid, 'Choose the correct option')


def food(url):
    app = ClarifaiApp(settings.CLARIFAI_APP_ID, settings.CLARIFAI_APP_SECRET)

    # get the general model
    model = app.models.get("food-items-v1.0")

    # predict with the model
    debug(url)
    res = model.predict_by_url(url=url)
    res = map(lambda x: x['name'], res['outputs'][0]['data']['concepts'])
    return res


def test_food(request):
    return HttpResponse(json.dumps(food(
        'https://scontent.xx.fbcdn.net/v/t34.0-12/17496094_10208759653813233_938158810_n.jpg?_nc_ad=z-m&oh=479263e3f66abfc57b82db0bafe37062&oe=58D85803')))


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
                            analyze_food(fbid, url)
                elif 'message' in message:
                    answer_text(fbid, message['message']['text'])

                info(message)

        return HttpResponse()
