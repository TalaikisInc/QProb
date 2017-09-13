from datetime import datetime
from time import mktime, sleep
import random
from os import listdir, rename, remove, name
from os.path import isfile, join
from asyncio import gather
from textwrap import wrap
import warnings
from subprocess import call

import requests
from PIL import Image
from feedparser import parse
from newspaper import Article, Config
from textblob import TextBlob
from clint.textui import colored
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from nltk import pos_tag
from nltk.tokenize import word_tokenize

from django.utils.html import strip_tags
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.utils.encoding import smart_text

from .models import Sources, Twits, TwitsByTag, Tags, Post, Category, Video
from . import rake
from .facebook_publisher import face_publish
from .twitter import post_tweet, twitter_date, get_tweets_by_tag, get_tweets
from .amazon import parse_amazon
from .text_tools import replace_all, text_cleaner, summarizer, words_wo_stopwords, WordCloudMod, filter_insignificant
from .youtube import do_youtube_once
from .meaning import NPExtractor

warnings.filterwarnings("ignore")

NEWSPAPER_CONFIG = Config()
NEWSPAPER_CONFIG.browser_user_agent = settings.HEADERS['User-Agent']
NEWSPAPER_CONFIG.skip_bad_cleaner = True
EXTS = ['png', 'jpg', 'gif', 'jpeg']

#TODO implement optimized images functions: start_opt, del_nonopt, use_opt,...


def feeds_to_db(data):
    sources = Sources.objects.create(feed=data[0], twitter_handle=data[1].\
        replace('https://twitter.com/', '').replace('http://twitter.com/', ''))
    sources.save()


# TODO solve the problem if handle not in db, but called
# from somewhere, when should be saved to TwitsByTag
# this should be unified
async def get_source_obj(source):
    try:
        source_obj = Sources.objects.get(twitter_handle=source)
    except Exception as err:
        print(err)
        source_obj = None
    return source_obj


async def save_tweet(entry, source):
    try:
        if settings.SHOW_DEBUG:
            print("Twitter handle {}".format(entry.user.screen_name))
        source_obj = await get_source_obj(source=source)
        if not source_obj is None:
            twit_obj = Twits.objects.create(tweet_id=entry.id, content=entry.text, \
                twitter_handle=source_obj, screen_name=entry.user.name, \
                profile_image=entry.user.profile_image_url, hashtags=entry.hashtags, \
                date=await twitter_date(entry.created_at))
            twit_obj.save()
            if settings.SHOW_DEBUG:
                print(colored.green("Tweet cached to db."))
    except IntegrityError:
        pass
    except Exception as err:
        print(colored.red("At save_tweet {}").format(err))


async def generate_tweets(source):
    data = await get_tweets(handle=source)

    if not data is None:
        if len(data) > 0:
            gather(*[save_tweet(entry=entry, source=source) \
                for entry in data], return_exceptions=True)


def tweets_to_db(loop):
    sources_ = Sources.objects.filter(active=True, dead=False).values('twitter_handle')
    sources = [s['twitter_handle'] for s in sources_ if not s['twitter_handle'] is ""]
    sample = random.sample(sources, len(sources))

    loop.run_until_complete(gather(*[generate_tweets(source=source) \
        for source in sample], return_exceptions=True))


async def save_tweet_tag(tweet, tag):
    try:
        tweet_obj = TwitsByTag.objects.create(tweet_id=tweet.id, content=tweet.text, \
            twitter_handle=tweet.user.screen_name, screen_name=tweet.user.name, \
            profile_image=tweet.user.profile_image_url, hashtags=tweet.hashtags, \
            date=await twitter_date(value=tweet.created_at), by_tag=tag)
        tweet_obj.save()
        if settings.SHOW_DEBUG:
            print(colored.green("Tweet inserted into db."))
    except IntegrityError:
        pass
    except Exception as err:
        print(colored.red("At tweetes by tag to db {0}".format(err)))


async def generate_tweets_tag(tag):
    tweets = await get_tweets_by_tag(tag=tag)
    if not tweets is None:
        if len(tweets) > 0:
            gather(*[save_tweet_tag(tweet=tweet, tag=tag) for tweet in tweets], \
                return_exceptions=True)


# TODO this can be improved, definitely has duplicates
def tweets_by_tag_to_db(loop):
    tags = Tags.objects.filter(tag_type='T', active=True)

    loop.run_until_complete(gather(*[generate_tweets_tag(tag=tag) \
        for tag in tags], return_exceptions=True))


async def clean_tweet(tweet, replacements):
    for each in tweet.hashtags.split('Hashtag'):
        if 'Text' in each:
            hashtag = await replace_all(each.split('Text=')[1], replacements)
            try:
                tweet.tags.add(hashtag)
                tag = Tags.objects.create(title=hashtag, tag_type='T')
                tag.save()
                if settings.SHOW_DEBUG:
                    print("Tag {0} saved.".format(hashtag))
            except IntegrityError:
                pass
            except Exception as err:
                print("TAt tag cleaner {0} with {1}.".format(err, hashtag))


def twit_cleaner(tweets, loop):
    replacements = {"u'": "", ")": "", "]": "", "'": "", ",": ""}

    loop.run_until_complete(gather(*[clean_tweet(tweet=tweet, \
        replacements=replacements) for tweet in tweets], return_exceptions=True))


def clean_tweet_hashtags(loop):
    tweets = Twits.objects.all()
    twit_cleaner(tweets=tweets, loop=loop)
    tweets = TwitsByTag.objects.all()
    twit_cleaner(tweets=tweets, loop=loop)


async def get_category(cat_title):
    cat = wrap(cat_title, 40)[0]
    if settings.SHOW_DEBUG:
        print(colored.green("New category name if changed: {0}".format(cat)))

    try:
        if len(cat) > 0:
            category_ = Category.objects.get(title=cat)
        else:
            category_ = Category.objects.get(title='Unknown')
    except ObjectDoesNotExist:
        if len(cat) > 0:
            category_ = Category.objects.create(title=cat)
        else:
            category_ = Category.objects.create(title='Unknwon')
        category_.save()

    return category_


async def save_tags(tags, entry):
    try:
        if len(tags) > 0:
            for tag in tags:
                if "'s" not in tag:
                    try:
                        tag_obj = Tags.objects.get(title=tag)
                    except ObjectDoesNotExist:
                        tag_obj = Tags.objects.create(title=tag)
                        tag_obj.save()
                        print(colored.green("Added tag '{0}' to entry".format(tag)))
                    entry.tags.add(tag_obj)
    except IntegrityError:
        pass
    except Exception as err:
        print(colored.red("At save_tags {}".format(err)))
    
    return entry


async def check_image_exist(image_name):
    """
    Checks if image exists in the uplods folder.
    """
    if not isfile(join(settings.BASE_DIR, image_name)):
        image_name = None

    return image_name


async def posts_to_db(row, loop):
    """
    Writes article to database.

    Args:
        row (dict): Dictionary of data.
        loop (loop): Asyncio loop.

    Returns:
        None.
    """

    if settings.SHOW_DEBUG:
        print(colored.green("Data for insertion: {0}, {1}".format(row['title'], row['date'])))

    category_ = await get_category(cat_title=row['category'])
    feed_ = Sources.objects.get(feed=row['feed'])

    if len(row['title']) > settings.MINIMUM_TITLE:
        try:
            if not row['image_url'] is None:
                row['image_url'] = await check_image_exist(image_name=row['image_url'])
                await resize_image(file_name=row['image_url'].replace("uploads/", ""))

            entry = Post.objects.create(title=smart_text(row['title']), url=row['url'],  \
                image=row['image_url'], working_content=smart_text(row['working_content']) or None,  \
                content=smart_text(row['cleaned_text']) or None, summary=smart_text(row['summary']) or None,  \
                date=row['date'], sentiment=row['sentiment'], category=category_,  \
                feed=feed_, feed_content=row['feed_content'], pub_date=datetime.now())

            entry = await save_tags(tags=row["tags"], entry=entry)

            if settings.GET_YOUTUBE:
                if settings.SHOW_DEBUG:
                    print("Going to youtube...")
                await do_youtube_once(post=entry, loop=loop)

            if settings.POST_TO_TWITTER:
                if not settings.DEV_ENV:
                    print("Going to Twitter...")
                    await post_tweet(data=row)

            if settings.POST_TO_FACEBOOK:
                if not settings.DEV_ENV:
                    if settings.SHOW_DEBUG:
                        print("Going to Facebook...")
                await face_publish(data=row)

            if settings.GET_AMAZON:
                if settings.SHOW_DEBUG:
                    print("Going to Amazon...")
                await parse_amazon(title=row['title'], loop=loop)
            
            entry = await make_wordcloud(entry=entry)
            entry.save()
            print(colored.green("Article saved to db."))
        except Exception as err:
            print(colored.red("[ERROR] At post to db: {0}".format(err)))


async def get_body_from_internet(url):
    try:
        article = Article(url, config=NEWSPAPER_CONFIG)
        article.download()
        article.parse()
    except Exception as err:
        print(colored.red("At get_body_from_internet {}".format(err)))

    return article


async def sentiment(data):
    try:
        blob = TextBlob(data)
        sentiment_value = round(blob.sentiment.polarity, 2)
    except Exception as err:
        print("At sentiment {}".format(err))
        sentiment_value = None

    return sentiment_value


async def title_dropper(title):
    removals_ = open(join(settings.BASE_DIR, "aggregator", 'data', 'title_stops.txt'), 'r')
    removals = [r.replace('\n', '') for r in removals_]

    for removal in removals:
        if removal in title:
            return False

    return True


async def del_art(article):
    try:
        if await title_dropper(article.title) is False:
            if settings.SHOW_DEBUG:
                print(colored.green("This article should be deleted: {0}".format(article.title)))
            article.delete()
    except Exception as err:
        print(colored.red("At del_art {}".format(err)))


def title_cleaner_from_db(loop):
    articles = Post.objects.all()

    loop.run_until_complete(gather(*[del_art(article=article) \
        for article in articles], return_exceptions=True))


def remake_summaries_from_content():
    articles = Post.objects.filter(parsed=True)

    for article in articles:
        entry = Post.objects.get(title=article.title)

        try:
            print((colored.green("Got this entry: {0}".format(entry.title))))
            entry.summary = summarizer(data=entry.content, sentences=settings.SUMMARIZER_SENTENCES)
            entry.sentiment = sentiment(entry.content)
            entry.save()
            print(colored.green("Remade summary: {0}".format(entry.summary)))
        except IntegrityError:
            pass
        except Exception as err:
            print(colored.red("[ERROR] At remake summaries: {0}".format(err)))


async def update_item(article):
    try:
        entry = Post.objects.get(title=article.title)
        entry.content = await text_cleaner(data=entry.working_content)
        entry.save()
    except Exception as err:
        print(colored.red("[ERROR] At update db with cleaned content {}".format(err)))


def update_db_with_cleaned_content(loop):
    articles = Post.objects.all()

    loop.run_until_complete(gather(*[update_item(article=article) \
        for article in articles], return_exceptions=True))


def update_wrong_image_urls():
    articles = Post.objects.filter(image__icontains='%')

    for article in articles:
        oldname = "{0}".format(article.image)
        newname = "{0}".format(article.image).replace('%', '')
        article.image = newname
        article.save()
        print(colored.green("Removed percents from image url {0}.".\
            format(article.image)))
        original_filename = join(settings.BASE_DIR, 'uploads', oldname.split('/', 1)[1])
        new_filename = join(settings.BASE_DIR, 'uploads', newname.split('/', 1)[1])
        rename(original_filename, new_filename)
        print(colored.green("Renamed image from {0} to {1} in folder.".\
            format(original_filename, new_filename)))


async def check_post(entry):
    try:
        #if content from feed is betetr than acquired from web
        if (len(entry.working_content) < 50) & (len(entry.feed_content) > 50):
            soup = BeautifulSoup(entry.feed_content)
            text = ''.join(soup.findAll(text=True))
            entry.content = await text_cleaner(data=text)
            entry.summary = await summarizer(data=text, sentences=settings.SUMMARIZER_SENTENCES)
            entry.sentiment = await sentiment(data=text)
            entry.parsed = True
            entry.save()
            if settings.SHOW_DEBUG:
                print(colored.green("Empty post updated with feed content: {0}".\
                    format(entry.title)))
        else:
            #empty everyhing otherwise
            entry.content = ""
            entry.summary = ""
            entry.parsed = True
            entry.save()
    except Exception as err:
        print(colored.red("[ERROR] At content if emtpy [all] : {0}".format(err)))


def content_if_empty_all(loop):
    empty_posts = Post.objects.raw("SELECT * FROM aggregator_post WHERE \
        LENGTH(working_content) < 50")

    loop.run_until_complete(gather(*[check_post(entry=entry) \
        for entry in empty_posts], return_exceptions=True))


async def check_img(filenames, post):
    try:
        if "uploads/" in str(post.image):
            if str(post.image)[8:] not in filenames:
                print("Updating image {}".format(post.image))
                post.image = None
                post.save()
                print(colored.green("Updated image as non-existent"))
    except Exception as err:
        print(colored.red("At check_img {}".format(err)))


def clean_images_from_db(loop):
    filenames = [f for f in listdir(join(settings.BASE_DIR, "uploads")) \
        if isfile(join(settings.BASE_DIR, "uploads", f))]
    posts = Post.objects.all()

    loop.run_until_complete(gather(*[check_img(filenames=filenames, \
        post=post) for post in posts], return_exceptions=True))


async def check_db_for_image(fle):
    try:
        post_count = Post.objects.filter(image='uploads/{0}'.format(fle)).count()
        if post_count == 0:
            print("File not in db: {0}".format(fle))
            filename = join(settings.BASE_DIR, 'uploads', fle)
            remove(filename)
            print("Removed {0}".format(filename))
    except Exception as err:
        print(colored.red("At check_db_for_image {}".format(err)))


def clean_images_from_folder(loop):
    path = join(settings.BASE_DIR, 'uploads')
    filenames = [f for f in listdir(path) if isfile(join(path, f))]

    loop.run_until_complete(gather(*[check_db_for_image(fle=fle) \
        for fle in filenames], return_exceptions=True))


async def get_image_locs(url):
    try:
        image_name_, filename = None, None
        try:
            image_name_ = url.split('?', 1)[0]
        except:
            pass
        image_name_ = image_name_.rsplit('/', 1)[-1]

        if any(ext in image_name_ for ext in EXTS):
            replacements = {"%": "", ")": "", "]": "", "'": "", ",": "", "-": "", \
                "_": "", "=": ""}
            img = await replace_all(image_name_, replacements)
            image_name = img.split(".")[-2][:100].replace(".", "") + "." + img.split(".")[-1]
            filename = join(settings.BASE_DIR, 'uploads', image_name)
    except Exception as err:
        print(colored.red("At get_image_locs {}".format(err)))

    return (image_name, filename)


async def check_image_format(filename, image_name):
    try:
        img = None
        with Image.open(filename) as format_checker:
            width, height = format_checker.size
            if not format_checker.format is None:
                if width < settings.MINIMUM_IMAGE or height < settings.MINIMUM_IMAGE:
                    format_checker.close()
                    remove(filename)
                else:
                    format_checker.close()
                    img = "uploads/{}".format(image_name)
            else:
                format_checker.close()
                remove(filename)
    except Exception as err:
        print(colored.red("At check_image_format {}".format(err)))

    return img


async def save_image(post_count, filename, source, image_name):
    try:
        img = None
        if post_count == 0:
            with open(filename, 'wb') as image:
                image.write(source.content)
                image.close()
                img = await check_image_format(filename=filename, image_name=image_name)
        else:
            img = "uploads/{}".format(image_name)
    except Exception as err:
        print(colored.red("At save_image {}".format(err)))

    return img


async def download_image(url):
    try:
        img, image_name, filename = None, None, None
        if len(url) > 0:
            source = requests.get(url, proxies=settings.PROXIES, \
                headers=settings.HEADERS)
            image_name, filename = await get_image_locs(url=url)
            if not image_name is None:
                post_count = Post.objects.filter(image="uploads/{0}".format(\
                    image_name)).count()
                img = await save_image(post_count=post_count, filename=filename, \
                    source=source, image_name=image_name)
    except Exception as err:
        print(colored.red("At download_image {}".format(err)))

    return img


async def keyword_extractor(data):
    try:
        #np_extractor = NPExtractor(words_wo_stopwords(strip_tags(data)))
        #result = np_extractor.extract()
        text = words_wo_stopwords(strip_tags(data))

        #TODO this is duplicated job, should be improved
        words = word_tokenize(strip_tags(text))
        taggged = pos_tag(words)
        cleaned = filter_insignificant(taggged)
        text = " ".join(cleaned)
        wc = WordCloudMod().generate(text)
        result = list(wc.keys())[:10]
    except Exception as err:
        print(colored.red("At keywords extraction {}".format(err)))
        result = []

    return result


# TODO definitely can be better if we knew where content is
async def get_feed_content(data):
    try:
        feed_content = data.content
    except Exception as err:
        if settings.SHOW_DEBUG:
            print(colored.red("[ERROR] At body from feed #1: {0}".format(err)))
        try:
            feed_content = data.summary
        except Exception as err:
            if settings.SHOW_DEBUG:
                print(colored.red("[ERROR] At body from feed #2: {0}".format(err)))
            try:
                feed_content = data.description
            except Exception as err:
                if settings.SHOW_DEBUG:
                    print(colored.red("[ERROR] At body from feed #3: {0}".format(err)))
                feed_content = ""
    return feed_content


async def get_date(data):
    try:
        date_now = datetime.fromtimestamp(mktime(data.published_parsed))
    except Exception as err:
        print(colored.red("[ERROR] At creation parsing date: {0}".format(err)))
        date_now = datetime.now()

    return date_now


async def content_creation(data, feed, category, loop):
    row = {}

    try:
        if (len(category) > 0) & (len(feed) > 0) & (len(data.title) > 0) & (len(data.link) > 0):
            row['category'] = category
            row['feed'] = feed
            row['title'] = data.title
            row['url'] = data.link
            row['feed_content'] = await get_feed_content(data=data)
            body = await get_body_from_internet(url=row['url'])
            if len(body.top_image) > 0:
                row['image_url'] = await download_image(url=body.top_image)
            else:
                row['image_url'] = None
            row['working_content'] = body.text
            row['cleaned_text'] = await text_cleaner(data=body.text)
            if (not row['cleaned_text'] is None) | (not row['cleaned_text'] is ""):
                row['summary'] = await summarizer(data=row['cleaned_text'], \
                    sentences=settings.SUMMARIZER_SENTENCES)
            else:
                row['summary'] = None
            if not row['working_content'] is None:
                row['sentiment'] = await sentiment(data=row['working_content'])
            else:
                row['sentiment'] = None
            row['date'] = await get_date(data=data)
            if not row['cleaned_text'] is None:
                if len(row['cleaned_text']) > 100:
                    row['tags'] = await keyword_extractor(data=row['cleaned_text'])
                else:
                    row['tags'] = []
            else:
                row['tags'] = []

            await posts_to_db(row=row, loop=loop)

    except Exception as err:
        print(colored.red("[ERROR] At content creation: {0}".format(err)))


async def parse_item(posts, data, feed, category, i, loop):
    try:
        post = posts.get(title=data.entries[i].title)
        if settings.SHOW_DEBUG:
            print(colored.green("Article is in database: {0}.".format(post.title)))
    except Exception as err:
        if data.entries[i].title:
            if await title_dropper(data.entries[i].title):
                if settings.SHOW_DEBUG:
                    print(colored.green("This article not in db: '{0}'".format(\
                        data.entries[i].title)))
                try:
                    if len(data.entries[i].link) < 150:
                        await content_creation(data=data.entries[i], feed=feed, \
                            category=category, loop=loop)
                except Exception as err:
                    print(colored.red("[ERROR] At content cretion iterator: {0}."\
                        .format(err)))
                sleep(settings.DELAY_REQUESTS)


async def get_data_from_feed(feed, posts, loop):
    try:
        data = parse(feed)
        if data.bozo == 0:
            category = data['feed']['title']
            if len(category) > 0:
                gather(*[parse_item(posts=posts, data=data, feed=feed, \
                    category=category, i=i, loop=loop) for i in range(0, \
                    len(data.entries))], return_exceptions=True)
        else:
            err = data.bozo_exception
            print(colored.red("Feed {0} is malformed: {1}".format(feed, err)))
            source_obj = Sources.objects.get(feed=feed)
            if source_obj.failures < 5:
                source_obj.failures = source_obj.failures + 1
            else:
                source_obj.failures = source_obj.failures + 1
                source_obj.active = False
            source_obj.save()
    except Exception as err:
        print(colored.red("At get_data_from_feed {}".format(err)))


def parse_all_feeds(loop):
    posts = Post.objects
    sources_ = Sources.objects.all().filter(active=True, dead=False).values('feed')
    feeds = [s['feed'] for s in sources_]
    sample = random.sample(feeds, len(feeds))

    if posts.all().count() > 0 or posts.all().count() == 0:
        loop.run_until_complete(gather(*[get_data_from_feed(feed=feed, \
            posts=posts, loop=loop) for feed in sample], return_exceptions=True))


def sources_to_db():
    """
    Used to parse sources from text list of tuples.
    """
    data = [('', '')]

    for item in data:
        try:
            feeds_to_db(item)
        except Exception as err:
            print(colored.red(err))
    print(colored.green("Done"))


async def check_source(source):
    posts = Post.objects.filter(feed=source).count()
    if posts == 0:
        source_obj = Sources.objects.get(feed=source["feed"])
        source_obj.active = False
        source_obj.save()


def empty_sources(loop):
    sources = Sources.objects.filter(active=True, dead=False)

    loop.run_until_complete(gather(*[check_source(source=source) \
        for source in sources], return_exceptions=True))


async def check_status(post):
    try:
        req = requests.get(post.url)

        if req.status_code != 200:
            post.dead = True
            post.save()
    except Exception as err:
        print(colored.red("At check_status {}".format(err)))
        post.dead = True
        post.save()


async def check_feed_status(source):
    try:
        req = requests.get(source.feed)
        if req.status_code != 200:
            source.dead = True
        else:
            source.dead = False
        source.save()
    except Exception as err:
        print(colored.red("At check_feed_status {}".format(err)))
        source.dead = True
        source.save()


def feed_status_checker(loop):
    sources = Sources.objects.filter(active=True)

    loop.run_until_complete(gather(*[check_feed_status(source=source) \
        for source in sources], return_exceptions=True))


def url_status_checker(loop):
    posts = Post.objects.filter(dead=False, feed__dead=False)

    loop.run_until_complete(gather(*[check_status(post=post) \
        for post in posts], return_exceptions=True))


async def resize_image(file_name):
    try:
        file_path = join(settings.BASE_DIR, "uploads", file_name)
        img = Image.open(file_path)
        w, h  = img.size
        factor = 1
        if w > 800:
            factor = 1/(w/800)
        if factor != 1:
            resized = img.resize((int(w*factor), int(h*factor)), Image.ANTIALIAS)
            resized.save(file_path)
            print(colored.green("Resized image."))
    except Exception as err:
        print(colored.red("At resize_image {}".format(err)))


async def resize(file_name):
    try:
        ext = file_name.split(".")[1]
        if ext in EXTS:
            await resize_image(file_name=file_name)
    except Exception as err:
        print(colored.red("At resize {}".format(err)))


def img_resizer(loop):
    filenames = [f for f in listdir(join(settings.BASE_DIR, "uploads")) \
        if isfile(join(settings.BASE_DIR, "uploads", f))]

    loop.run_until_complete(gather(*[resize(file_name=file_name) \
        for file_name in filenames], return_exceptions=True))

    #if not name is "nt":
        #call(["python", "/home/{}/aggregator/img4web.py".format(
            #settings.SITE_FOLDER), "--src", "/home/{}/uploads".format(settings.SITE_FOLDER),
            #"--dst", "/home/{}/uploads".format(settings.SITE_FOLDER)])


def make_category_thumbs():
    cats = Category.objects.all()

    for cat in cats:
        try:
            posts = Post.objects.filter(category_id=cat).exclude(image='').values("image")
            images = [i["image"] for i in posts]
            if len(images) > 0:
                supreme_leader = random.sample(images, 1)[0]
                cat.thumbnail = supreme_leader
                cat.save()
                print(colored.green("Saved thumbnail."))
        except Exception as err:
            print(colored.red("At make_category_tumbs {}".format(err)))


def full_wordcloud():
    """
    Generates wordcloud for the site.
    """
    text = ""
    try:
        posts = Post.objects.filter().values("content")
        for post in posts:
            text += post["content"] + " "

        text = words_wo_stopwords(text=text)
        word_cloud = WordCloud(max_font_size=40, background_color="rgba(255, 255, 255, 0)", width=350, height=600, mode="RGBA").generate(text)
        fig = plt.figure(frameon=False)
        fig.patch.set_visible(False)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        ax.imshow(word_cloud, interpolation='bilinear')
        plt.savefig(join(settings.STATIC_ROOT, 'images', 'wordcloud.png'))
        plt.close()
    except Exception as err:
            print(err)


def posts_wordcloud():
    """
    Generates wordcloud foeach post.
    """
    posts = Post.objects.filter().exclude(content="")
    for post in posts:
        try:
            image_file = join(settings.STATIC_ROOT, "wordcloud", "{0}.png".format(post.slug))

            if not isfile(image_file):
                text = words_wo_stopwords(text=post.content)
                if len(text) > 100:
                    word_cloud = WordCloud(max_font_size=40, background_color="rgba(255, 255, 255, 0)", width=800, height=350, mode="RGBA").generate(text)
                    fig = plt.figure(frameon=False)
                    fig.patch.set_visible(False)
                    ax = fig.add_axes([0, 0, 1, 1])
                    ax.axis('off')
                    ax.imshow(word_cloud, interpolation='bilinear')
                    plt.savefig(image_file)
                    plt.close()
                    post.wordcloud = "static/wordcloud/{0}.png".format(post.slug)
                    post.save()
        except Exception as err:
            print(err)


async def make_wordcloud(entry):
    """
    Makes singular wordcloud for a post.
    """
    text = words_wo_stopwords(text=entry.content)
    if len(text) > 100:
        word_cloud = WordCloud(max_font_size=60, background_color="rgba(255, 255, 255, 0)", mode="RGBA").generate(text)
        fig = plt.figure(frameon=False)
        fig.patch.set_visible(False)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        ax.imshow(word_cloud, interpolation='bilinear')
        plt.savefig(join(settings.STATIC_ROOT, "wordcloud", "{0}.png".format(entry.slug)))
        plt.close()
        entry.wordcloud = "static/wordcloud/{0}.png".format(entry.slug)

    return entry

def banner():
    terms = ["sex", "porn"]
    for term in terms:
        tags = Tags.objects.filter(title__icontains=term).delete()
        posts = Post.objects.filter(title__icontains=term).delete()
        videos = Video.objects.filter(title__icontains=term).delete()
        twits = Twits.objects.filter(content__icontains=term).delete()
        taged = TwitsByTag.objects.filter(content__icontains=term).delete()


def db_cleaner():
    posts = Post.objetcs.all()
    for post in posts:
        post.working_content = ""
        post.feed_content = ""
        post.save()

    books = Books.objects.all().delete()
    videos = Video.objects.all().delete()
    twits = Twits.objects.all().delete()
    taged = TwitsByTag.objects.all().delete()