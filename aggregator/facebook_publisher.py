from django.conf import settings
from django.utils.html import strip_tags

import facebook
from clint.textui import colored

from .models import Post


async def get_ttachment(post, data):
    attachment =  {
        'name': data['title'],
        'link': '{0}{1}/'.format(settings.DOMAIN, post.slug)
    }

    sentiment = post.sentiment or "N/A"
    summary = post.summary or ""
    attachment['description'] = strip_tags(summary) + " " + sentiment
    if post.image:
        attachment['picture'] = '{0}{1}'.format(settings.DOMAIN, post.image)

    return attachment


async def face_publish(data):
    try:
        cfg = {
            "page_id"      : settings.PAGE_ID,
            "access_token" : settings.ACCESS_TOKEN
        }

        api = get_api(cfg)

        post = Post.objects.get(title=data['title'])

        attachment =  await get_ttachment(post=post, data=data)

        status = api.put_wall_post(message=post.title, attachment=attachment)
        print(colored.green("Published to Facebook: {0}".format(post.title)))
    except Exception as e:
        print(colored.red("At Facebook publish: {0}".format(e)))

def get_api(cfg):
    graph = facebook.GraphAPI(cfg['access_token'])

    return graph
