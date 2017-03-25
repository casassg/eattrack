import json

from clarifai.rest import ClarifaiApp
from django.conf import settings
from django.http import HttpResponse


# Create your views here.


def food(request):
    app = ClarifaiApp(settings.CLARIFAI_APP_ID, settings.CLARIFAI_APP_SECRET)

    # get the general model
    model = app.models.get("food-items-v1.0")

    # predict with the model
    res = model.predict_by_base64()
    return HttpResponse(json.dumps(res))


def messenger(request):
    token = request.GET['hub.verify_token']
    if token == 'gerardcasassaez':
        return HttpResponse(request.GET['hub.challenge'])
    else:
        return HttpResponse('Not correct')