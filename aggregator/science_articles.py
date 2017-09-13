#!/usr/bin/env python
# -*- coding: utf-8 -*-


#3d party imports
import textract
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from itertools import chain, groupby
from clint.textui import colored
from os.path import join
from textwrap import wrap

#django imports
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_text

if settings.RESEARCH_MODULE:
    #own imports
    from .models import (ScienceArticle, ScienceCat)
    from .tasks import (summarizer, sentiment, text_cleaner)


    def downloader():
        pdfs = ScienceArticle.objects.filter(got_pdf=False)

        for pdf in pdfs:
            source = requests.get(pdf.pdf_url, proxies=settings.PROXIES, headers=settings.HEADERS, timeout=settings.TIMEOUT)

            name = "{0}.pdf".format(wrap(pdf.slug, 60)[0])
            filename = join(settings.BASE_DIR, 'uploads', 'research', name)

            with open(filename, 'wb') as fle:
                print((colored.green("Successfully opened pdf w. path: {0}".format(filename))))
                fle.write(source.content)
                fle.close()

            pdf.file = "uploads/research/{0}".format(name)
            pdf.got_pdf = True
            pdf.save()


    def get_abstracts():
        pdfs = ScienceArticle.objects.all()

        for pdf in pdfs:
            try:
                source = requests.get(pdf.abs_url, proxies=settings.PROXIES, headers=settings.HEADERS, timeout=settings.TIMEOUT)

                if source.status_code == 200:
                    abs = str(source.text).split("<span class=\"descriptor\">Abstract:</span> ")[1].split("</blockquote>")[0]
                    pdf.summary = abs
                    pdf.sentiment = sentiment(abs)
                    pdf.save()
                    print((colored.green("Successfully saved abstract to db.")))
            except Exception as e:
                print((colored.red("[ERROR] At abstract: {0}".format(e))))


    def make_summaries():

        pdfs = ScienceArticle.objects.all()

        for pdf in pdfs:
            try:
                pdf.summary = text_cleaner(pdf.text)
                #summarizer(pdf.text, settings.SUMMARIZER_SENTENCES)
                #pdf.sentiment = sentiment(pdf.text)
                pdf.save()
                print((colored.green("Successfully saved PDF summary to db.")))
            except Exception as e:
                print((colored.red("[ERROR] At PDF text summarizer: {0}".format(e))))
                continue

    def parse_pdfs():

        pdfs = ScienceArticle.objects.filter(got_pdf=True).filter(text=None)

        for pdf in pdfs:
            filename = join(settings.BASE_DIR, 'uploads', 'research', str(pdf.file).split('/')[-1])
            try:
                parsed = textract.process(filename)
                pdf.text = smart_text(parsed)
                pdf.save()
                print((colored.green("Successfully saved PDF text to db.")))
            except Exception as e:
                print((colored.red("[ERROR] At PDF text parse: {0}".format(e))))


    def get_pdfs_urls():

        main_link = 'https://arxiv.org'

        months = list(range(1, 13))
        now = datetime.now()
        endyear_ = str(now.year)[2:4]
        endyear = int(endyear_) + 100 + 1
        years = list(range(97, endyear)) #97

        for y in years:
            if y >= 100:
                y = y - 100
                if y < 10:
                    y = "0{0}".format(y)

            for m in months:
                if m < 10:
                    m = "0{0}".format(m)

                url = "https://arxiv.org/list/q-fin/{0}{1}?show=1000".format(y, m)
                print((colored.green("Getting: {0}".format(url))))

                source = requests.get(url, proxies=settings.PROXIES, headers=settings.HEADERS, timeout=settings.TIMEOUT)

                if source.status_code == 200:
                    print((colored.green("Request successful. processing...")))
                    tree = BeautifulSoup(source.text, 'html.parser')

                    entries1 = []
                    entries2 = []

                    id = 0
                    for i in tree.find_all('dt'):
                        entry1 = {}

                        abs = str(i.contents[2]).split("a href=\"")[1].split("\"")[0]
                        if 'abs' in abs:
                            entry1['abs'] = abs

                        pdf = str(i.contents[2]).split("a href=\"")[2].split("\"")[0]
                        if 'pdf' in pdf:
                            entry1['pdf'] = pdf

                        entry1['id'] = id
                        id += 1
                        entries1.append(entry1)

                    id = 0
                    for i in tree.findAll('dd'):
                        entry2 = {}

                        entry2['title'] = str(i.contents[1]).split("</div>")[0].split('</span> ')[1].replace('\n', '')
                        entry2['category'] = str(i.contents[1]).split("Subjects:")[1].split("\">")[1].split("<")[0].split(" (")[0]
                        entry2['id'] = id
                        id += 1
                        entries2.append(entry2)

                    lst = sorted(chain(entries1, entries2), key=lambda x:x['id'])

                    entries = []
                    for k, v in groupby(lst, key=lambda x:x['id']):
                        d = {}
                        for dct in v:
                            d.update(dct)
                            entries.append(d)

                    for e in entries:
                        try:
                            category_ = ScienceCat.objects.get(title=e['category'])
                        except ObjectDoesNotExist:
                            category_ = ScienceCat.objects.create(title=e['category'])
                            category_.save()

                        try:
                            science_art = ScienceArticle.objects.create(title=e['title'], \
                                abs_url="{0}{1}".format(main_link, e['abs']), \
                                pdf_url="{0}{1}".format(main_link, e['pdf']), \
                                category=category_)

                            science_art.save()
                        except Exception as e:
                            print(e)
