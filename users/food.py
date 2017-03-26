from clarifai.rest import ClarifaiApp
from django.conf import settings


def extract(url):
    app = ClarifaiApp(settings.CLARIFAI_APP_ID, settings.CLARIFAI_APP_SECRET)

    # get the general model
    model = app.models.get("food-items-v1.0")

    # predict with the model
    res = model.predict_by_url(url=url)
    return map(lambda x: x['name'], filter(lambda x: x['value'] > 0.5,
                                           sorted(res['outputs'][0]['data']['concepts'], key=lambda x: -x['value'])))
