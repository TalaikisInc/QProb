import time
from os.path import join
import asyncio

import requests
from clint.textui import colored

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_text
from django.utils.html import strip_tags

from .amazon_api import AmazonAPI
from .models import (Post, Books, BooksCat)
from . import summarize

#TODO as this requires manual bok cat selection, this should be automatewd
# -> should dtermine keywords auto and query amazon on them

async def make_summaries(title):
    book = Books.objects.get(title=title)

    try:
        book.summary = await summarizer(data=strip_tags(book.review), sentences=(settings.SUMMARIZER_SENTENCES+3))
        book.save()
        print("Amazon summary saved to database: {0}".format(book.summary))
    except Exception as e:
        print(colored.red("[ERROR] At Amazon summary: {0}".format(e)))


async def download_image(url):
    source = requests.get(url, proxies=settings.PROXIES, headers=settings.HEADERS)
    image_name = url.rsplit('/', 1)[-1].split('?', 1)[0].replace('%', '')

    filename = join(settings.BASE_DIR, 'uploads', 'books', image_name)

    with open(filename, 'wb') as image:
        image.write(source.content)
        image.close()
        print("Successfully saved image w. path {0}".format(filename))

        return 'uploads/books/{0}'.format(image_name)


async def generate_images(book):
    try:
        if book.medium_image_url:
            if settings.SHOW_DEBUG:
                print("Image from db: {0}".format(book.medium_image_url))
            image_name = await download_image(url=book.medium_image_url)
            if settings.SHOW_DEBUG:
                print("Got image from folder: {0}".format(image_name))

            if not (image_name is None):
                book.image = image_name
                book.got_image = True
                book.save()
                print("Amazon image saved to database book: {0}".format(book.title))
    except Exception as e:
        print(colored.red("At Amazon generate_images {}".format(e)))


async def get_amazon_images(loop):
    books = Books.objects.filter(got_image=False)

    asyncio.gather(*[generate_images(\
        book=book) for book in books], \
        return_exceptions=True
    )


async def query_amazon(query, howmuch):
    products = []
    try:
        time.sleep(10)
        amazon = AmazonAPI(settings.AMAZON_ACCESS_KEY, settings.AMAZON_SECRET_KEY, settings.AMAZON_ASSOC_TAG)
        products = amazon.search(Keywords=query, SearchIndex='Books', n=howmuch)
    except Exception as e:
        print(colored.red("[ERROR] at querying Amazon: {0}".format(e)))

    return products


async def save_cat(c, product, entry):
    print(product.browse_nodes[c].name)
    try:
        cat = BooksCat.objects.get(id=product.browse_nodes[c].id)
    except ObjectDoesNotExist:
        cat = BooksCat.objects.create(id=product.browse_nodes[c].id, title=product.browse_nodes[c].name)
        cat.save()
        print(colored.green("Book category saved: {0}".format(product.browse_nodes[c].name)))
    except Exception as e:
        print(colored.green("At save_cat: {}".format(e)))

    entry.categories.add(cat)
    print("Book category added to book {}".format(product.browse_nodes[c].name))


async def create_categories(product, entry):
    try:
        asyncio.gather(*[save_cat(\
            c=c, product=product, entry=entry) for c in range(0, len(product.browse_nodes))], \
            return_exceptions=True
        )
    except Exception as e:
        print(colored.red("At create_categories {}".format(e)))


async def get_authors(product):
    authors_ = product.authors

    if len(authors_) > 0:
        authors = ', '.join(authors_)
    else:
        authors = authors_[0]

    return authors


async def get_image(product):
    if product.large_image_url:
        image = product.large_image_url
    else:
        image = product.medium_image_url

    return image

# TODO should be tested if categories are properly saved
async def create_book(product, loop):
    try:
        authors = await get_authors(product=product)
        image = await get_image(product=product)

        if (not (authors is None)) & (not (image is None)):
            entry = Books.objects.create(title=product.title, asin=product.asin,
                authors=authors, publication_date=product.publication_date,
                pages=product.pages, medium_image_url=image,
                price=product.list_price[0], currency=product.list_price[1],
                review=product.editorial_review)

            await create_categories(product=product, entry=entry)

            if settings.SHOW_DEBUG:
                print(colored.green("Book saved: {0}".format(product.title)))
            entry.save()
            return entry
            #TODO filter duplicate netires errors
    except Exception as e:
        print(colored.red("[ERROR] At creating book: {0}".format(e)))


async def generate_amazon(cat, loop):
    try:
        print("Category title {}".format(smart_text(cat.title)))

        products = await query_amazon(query=cat.title, howmuch=100)

        if len(products) > 0:
            asyncio.gather(*[create_book(\
                product=product, loop=loop) for i, product in enumerate(products)], \
                return_exceptions=True
            )
    except Exception as e:
        print("At Amazon by category {}".format(e))


def parse_by_categories(loop):
    cats = BooksCat.objects.filter(enabled=True)

    loop.run_until_complete(asyncio.gather(*[generate_amazon(\
        cat=cat, loop=loop) for cat in cats], \
        return_exceptions=True
    ))


async def process_keyword(k, loop):
    try:
        products = await query_amazon(query=k, howmuch=100)

        if len(products) > 0:
            asyncio.gather(*[create_book(\
                product=product, loop=loop) for product in products], \
                return_exceptions=True
            )
    except Exception as e:
        print(colored.red("[ERROR] At Amazon process_keyword: {0}".format(e)))


#TODO needs normal keyword generator!!!!!
#FIXME this qwouldn't work now due to intrduction of async
def parse_by_keywords(loop):
    keywords = ['trading system', 'quantitative trading', 'momnetum strategy', 'mean reversion straetgy', \
            'mechanical trading strategy', 'algorithmic trading strategy', 'algorithmic trading', 'quants', \
            'swing trading', 'trading', 'investing', 'investments', 'forex strategies', 'stock trading', \
            'stock market', 'forex market', 'futures market', 'how I made', 'day trading', 'market microstructure', \
            'Warren Buffet', 'John Tempelton', 'Philip Fisher', 'Benjamin Graham', 'Peter Lynch', 'George Soros', \
            'Jack Bogle', 'Bill Ackman', 'Peter Thiel', 'Ray Dalio', 'Prince Alwaleed', 'hedge fund', \
            'hedge fund strategyes', 'alpha models', 'data analsysis', 'quantitative investing', 'trading techniques',
            'investment banking', 'futures market', 'volatility', 'risk management', 'technical analysis', \
            'ETF', 'trading techniques']

    loop.run_until_complete(asyncio.gather(*[process_keyword(\
        k=k, loop=loop) for k in keywords], \
        return_exceptions=True
    ))


async def add_books_to_posts(product, post, loop):
    try:
        entry = await create_book(product=product, post=post, loop=loop)
        post.books.add(entry)
        post.got_books = True
        post.save()
        print(colored.green("Book included in post: {0}".format(product.title)))
        await make_summaries(title=entry.title)
    except Exception as e:
        print(colored.red("[ERROR] at Amazon add_books_to_posts: {0}".format(e)))


#TODO there is a problem qwhen nothing found on Amazon, maybe something better may be thought than just searching fore article titles
async def parse_amazon(title, loop):
    post = Post.objects.get(title=title)

    try:
        products = await query_amazon(query=post.title, howmuch=10)

        if products:
            asyncio.gather(*[add_books_to_posts(\
                product=product, post=post, loop=loop) for i, product in enumerate(products)], \
                return_exceptions=True
            )

        await get_amazon_images(loop=loop)
    except Exception as e:
        if settings.SHOW_DEBUG:
            print(colored.red("At parse_amazon {}".format(e)))
            post.got_books = True
            post.save()
            print("Updated book as unsuccessfull Amazon parse.")
