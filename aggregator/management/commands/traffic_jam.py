from django.core.management.base import BaseCommand, CommandError
from aggregator.models import Post
from django.conf import settings

import requests
import random
from os.path import join
from clint.textui import colored


# Black stuff, don;t use it :-D
def load_user_agents(uafile=join(settings.BASE_DIR, 'user_agents.txt')):
    uas = []
    with open(uafile, 'r') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1-1])
    random.shuffle(uas)
    return uas


HEADERS = {
    "Connection" : "close",
    'User-Agent': random.choice(load_user_agents())
}

class Command(BaseCommand):
    help = 'Traffic jammer.'

    def handle(self, *args, **options):
        posts = Post.objects.all()

        for post in posts:
            try:
                ref = "{0}{1}/ ".format(settings.DOMAIN, post.slug)
                dict = {'referer': ref}
                dict.update(HEADERS)
                obj = requests.get(post.url, headers=dict)
                if obj.status_code == 200:
                    print((colored.green("OK for: {0}".format(post.url))))
            except Exception as e:
                print((colored.red("[ERROR]: {0}".format(e))))

        self.stdout.write(self.style.SUCCESS('Successfully done parsing jobs'))
