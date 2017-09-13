#!/usr/bin/env python
# -*- coding: utf-8 -*-

#third party imports
from bs4 import BeautifulSoup
import requests
from clint.textui import colored
from nltk.tokenize import sent_tokenize
import re

#django improts
from django.db import IntegrityError
from django.conf import settings
from django.utils.encoding import smart_text

#own imports
from .models import Terms, TermLinks
from .tasks import (get_body_from_internet, summarizer)


main_link = link_ = "http://www.investopedia.com"

#FIXME this is too messy, but probably not worth keeping

def remove_unwanted():
    terms = Terms.objects.all()

    for t in terms:
        try:
            t.term = smart_text(t.term).replace(smart_text(' Definition'), '')
            t.save()
            print((colored.green("Replaced unwanted: {0}".format(t.term))))
        except Exception as e:
            print((colored.red("[ERROR] Ar ttitle customization: {0}".format(e))))


def make_summaries():
    terms = Terms.objects.all()

    removals = ['DEFINITION', 'BREAKING DOWN', 'What is']

    for term in terms:
        try:
            summary = summarizer(term.text, settings.SUMMARIZER_SENTENCES)
            sentence_tokens = sent_tokenize(summary)
            text = ''
            for sentence in sentence_tokens:
                if not any(to_remove in sentence for to_remove in removals):
                    text += "{0} ".format(sentence.replace(r'\A[\d]\S\s', ''))

            term.summary = summarizer(text, settings.SUMMARIZER_SENTENCES)
            term.save()
        except Exception as e:
            print((coloredf.red("[ERROR] Ar terms summarizer: {0}".format(e))))


def update_link(original_link, type_):
    from .models import TermLinks

    update_link = TermLinks.objects.get(link=original_link)
    update_link.status_parsed = type_
    update_link.save()
    print(("Updated link status: {0}".format(original_link)))


def link_collector(source, initial, type_):
    from .models import TermLinks

    if source.status_code == 200:
        print("Request status successful.")
        tree = BeautifulSoup(source.text, 'html.parser')

        for l in tree.find_all('a'):
            link = l.get('href')
            print(("Got link: {0}".format(link)))
            if "terms/" in link:
                    print("Terms definiton in link found.")
                    try:
                        entry = TermLinks.objects.create(link=link, status_parsed='U')
                        entry.save()
                        print(("Saved new link: {0}".format(link)))
                        update_link(link, 'U')
                    except Exception as e:
                        print(("Failed at collector: {0}".format(e)))
                        update_link(link, type_)
                        continue
            else:
                print("No term definitions found in the link.")
                try:
                    update_link(link, type_)
                except Exception as e:
                    print(("Link {0} not useful, continuing.".format(link)))
                    continue

        update_link(initial, type_)



def get_article(link_, original_link):
    try:
        if not ('page' in link_):
            article = get_body_from_internet(link_)
            if 'Definition' in article.title:
                entry = Terms.objects.create(term=article.title, text=article.text, \
                        movies=article.movies, image=article.top_image)
                entry.save()
                print("Article saved in db.")
                update_link(original_link, 'A')
            else:
                update_link(original_link, 'A')
        else:
            update_link(original_link, 'A')
    except IntegrityError as e:
        print(e)
        update_link(original_link, 'A')


def parse():
    if TermLinks.objects.count() == 0:
        link_ = "http://www.investopedia.com/dictionary/"
        source = requests.get(link_, proxies=settings.PROXIES, headers=settings.HEADERS)
        if source.status_code == 200:
            tree = BeautifulSoup(source.text, 'html.parser')

            for l in tree.find_all('a'):
                link = l.get('href')
                if "terms/" in link:
                    try:
                        entry = TermLinks.objects.create(link=link, status_parsed='U')
                        entry.save()
                    except Exception as e:
                        print(("Failed at initial parse: {0}".format(e)))
    else:
        sources = TermLinks.objects.filter(status_parsed='U')

        for source in sources:
            if ('http://' or 'https://') in source.link:
                try:
                    print(("Requesting #1: {0}".format(source.link)))
                    s = requests.get(source.link)
                    link_collector(s, source.link, 'T')
                    print("Collected kinks.")
                except Exception as e:
                    print(("Failed at parsing db links #1: {0}".format(e)))
                    continue
            else:
                try:
                    print(("Requesting #2: {0}{1}".format(main_link, source.link)))
                    s = requests.get("{0}{1}".format(main_link, source.link))
                    link_collector(s, source.link, 'T')
                    print("Collected kinks.")
                except Exception as e:
                    print(("Failed at parsing db links #2: {0}".format(e)))
                    continue


    #collect articles
    links = TermLinks.objects.filter(status_parsed='T')

    for link in links:
        try:
            if ('http://' or 'https://') in link.link:
                print(("Trying get an article: {0}".format(link.link)))
                get_article(link_=link.link, original_link=link.link)
                print("Got the article.")
                s = requests.get(link.link)
                link_collector(s, link.link, 'A')
                print("Collected kinks.")
            else:
                lnk = "{0}{1}".format(main_link, link.link)
                print(("Trying get an article: {0}".format(lnk)))
                get_article(link_=lnk, original_link=link.link)
                print("Got the article.")
                s = requests.get(lnk)
                link_collector(s, link.link, 'A')
                print("Collected kinks.")
        except Exception as e:
            print(e)
            continue
