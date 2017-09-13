from os.path import join
from re import UNICODE, DOTALL, IGNORECASE, findall, compile, escape, sub
import sys
from collections import defaultdict
from operator import itemgetter
from math import log
import string

from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from clint.textui import colored

from django.conf import settings
from django.utils.html import strip_tags

from . import summarize


async def replace_all(text, dic):
    """
    Replaces all occurrences in text by provided dictionary of replacements.
    """
    for i, j in list(dic.items()):
        text = text.replace(i, j)
    return text


#dirty fix for compatibility w. django
def replace_all_nonasy(text, dic):
    for i, j in list(dic.items()):
        text = text.replace(i, j)
    return text


def scoreFunction(wholetext):
    """Get text, find most common words and compare with known
    stopwords. Return dictionary of values"""

    dictiolist = {}
    scorelist = {}
    # These are the available languages with stopwords from NLTK
    NLTKlanguages=["dutch","finnish","german","italian", "portuguese",
        "spanish","turkish","danish","english", "french","hungarian",
        "norwegian","russian","swedish"]

    FREElanguages = [""]
    languages=NLTKlanguages + FREElanguages

    # Fill the dictionary of languages, to avoid  unnecessary function calls
    for lang in NLTKlanguages:
        dictiolist[lang] = stopwords.words(lang)

    # Split all the text in tokens and convert to lowercase. In a
    # decent version of this, I'd also clean the unicode
    tokens = word_tokenize(wholetext)
    tokens = [t.lower() for t in tokens]

    # Determine the frequency distribution of words, looking for the
    # most common words
    freq_dist = FreqDist(tokens)

    # This is the only interesting piece, and not by much. Pick a
    # language, and check if each of the 20 most common words is in
    # the language stopwords. If it's there, add 1 to this language
    # for each word matched. So the maximal score is 20. Why 20? No
    # specific reason, looks like a good number of words.
    for lang in languages:
        scorelist[lang]=0
        for word in freq_dist.keys()[0:20]:
            if word in dictiolist[lang]:
                scorelist[lang]+=1
    return scorelist

def whichLanguage(scorelist):
    """This function just returns the language name, from a given
    "scorelist" dictionary as defined in scoreFunction()."""

    maximum = 0
    for item in scorelist:
        value=scorelist[item]
        if maximum<value:
            maximum = value
            lang = item
    return lang


class Autolinker(object):
    ignoreCaseLength = 12

    def __init__(self):
        self.links = {}
        #any item that gets added must have a linkHTML method that accepts a title parameter

    def addItem(self, title, item):
        self.links[title] = item

    def addLinks(self, links):
        for link in links:
            self.links[link.title()] = link

    def replaceAll(self, haystack):
        for title, link in sorted(list(self.links.items()), key=lambda x:-len(x[0])):
            haystack = self.replace(title, link, haystack)
            #we're going paragraph-by-paragraph, but don't want multiple links
            if self.replaced:
                del self.links[title]
        return haystack

    def regexOptions(self, text):
        options = DOTALL
        if len(text) > self.ignoreCaseLength:
            options = options | IGNORECASE
        return options

    def replace(self, needle, replacement, haystack):
        self.replacement = replacement
        options = self.regexOptions(needle)
        needle = compile('([^{}]*?)(' + escape(needle) + ')([^{}]*)', options)
        self.needle = needle
        self.replaced = False
        return self.doReplace(haystack)

    def doReplace(self, haystack):
        return sub(self.needle, self.matcher, haystack)

    def matcher(self, match):
        fullText = match.group(0)
        if not self.replaced:
            #if it's inside of a django tag, don't make the change
            if fullText[0] == '%' or fullText[-1] == '%':
                return fullText
                #if it's inside of a link already, don't make the change
                leftText = match.group(1)
                matchText = match.group(2)
                rightText = match.group(3)
                rightmostAnchor = leftText.rfind('<a')
                if rightmostAnchor != -1:
                    anchorClose = leftText.rfind('</a>')
                    if anchorClose < rightmostAnchor:
                        #this is inside of an open a tag.
                        #but there might be a match in the rightText
                        fullText = leftText+matchText + self.doReplace(rightText)
                        return fullText
                        #check the right side for anchors, too.
                        leftmostAnchorClose = rightText.find('</a>')
                        if leftmostAnchorClose != -1:
                            anchorOpen = rightText.find('<a')
                            if anchorOpen == -1 or anchorOpen > leftmostAnchorClose:
                                #this is inside of an open a tag
                                return fullText
                                #otherwise, it is safe to make the change
                                fullText = leftText + self.replacement.linkHTML(title=matchText) + rightText
                                self.replaced = True
                                return fullText


async def text_cleaner(data):
    paragraphs_ = ""
    try:
        keep_endings = ['.', '?']

        removals_ = open(join(settings.BASE_DIR, "aggregator", 'data', 'stop_sentences.txt'), 'r')
        removals = [r.replace('\n', '') for r in removals_]

        if not (data is None):
            text = data.split('\n')
            paragraphs = []
            for p in text:
                if len(p) > settings.MINIMUM_PARAGRAPH:
                    paragraphs.append(p)

            for p in paragraphs:
                sentence_tokens = sent_tokenize(p)
                paragraph = ""
                for sentence in sentence_tokens:
                    if sentence[-1] in keep_endings:
                            if len(sentence) > settings.MINIMUM_SENTENCE:
                                #should remove most of the code:
                                if sentence[0].isupper():
                                    if not any(to_remove in sentence for to_remove in removals):
                                        #eliminate some bad ending strings:
                                        if not sentence.endswith(('e.g.', 'i.e.')):
                                            paragraph += "{0} ".format(sentence)
                paragraphs_ +=  "<p>{0}</p>".format(paragraph)
    except Exception as e:
        print(colored.red("At text_cleaner {}".format(e)))

    return paragraphs_


async def summarizer(data, sentences):
    try:
        ss = summarize.SimpleSummarizer()
        summary =  ss.summarize(input_data=data, num_sentences=sentences)
    except Exception as e:
        print(colored.red("At summarizer: {0}".format(e)))
        summary =  None

    return summary


def load_stop_words(stop_word_file):
    """
    Utility function to load stop words from a file and return as a list of words
    @param stop_word_file Path and file name of a file containing stop words.
    @return list A list of stop words.
    """
    punctuation = list(string.punctuation)
    stop_words = []
    for line in open(stop_word_file):
        if line.strip()[0:1] != "#":
            for word in line.split():  # in case more than one per line
                stop_words.append(word)
    return stop_words + punctuation


def words_wo_stopwords(text):
    """
    Cleans text from stop words.
    """
    nltk_stopwords_list = stopwords.words('english')
    specifics = load_stop_words(stop_word_file=join(settings.BASE_DIR, "aggregator", 'data', 'stop_words.txt'))

    stopwords_list = list(set(nltk_stopwords_list + specifics + ["'s", "n't"]))

    words = word_tokenize(strip_tags(text))
    cleaned = [w for w in words if not w.lower() in stopwords_list]
    text = " ".join(cleaned)

    return text


def filter_insignificant(chunk, tag_suffixes=['DT', 'CC', 'CD', 'POS', 'PRP']):
    good = []

    for word, tag in chunk:
        ok = True

        for suffix in tag_suffixes:
            if tag.endswith(suffix):
                ok = False
                break

        if ok:
            good.append(word)

    return good


"""
Below code is modified version pf (c) https://github.com/amueller/word_cloud
"""

def dunning_likelihood(k, n, x):
    # dunning's likelihood ratio with notation from
    # http://nlp.stanford.edu/fsnlp/promo/colloc.pdf p162
    return log(max(x, 1e-10)) * k + log(max(1 - x, 1e-10)) * (n - k)


def score(count_bigram, count1, count2, n_words):
    """Collocation score"""
    if n_words <= count1 or n_words <= count2:
        # only one words appears in the whole document
        return 0
    N = n_words
    c12 = count_bigram
    c1 = count1
    c2 = count2
    p = c2 / N
    p1 = c12 / c1
    p2 = (c2 - c12) / (N - c1)
    score = (dunning_likelihood(c12, c1, p) + dunning_likelihood(c2 - c12, N - c1, p)
             - dunning_likelihood(c12, c1, p1) - dunning_likelihood(c2 - c12, N - c1, p2))
    return -2 * score


def pairwise(iterable):
    from itertools import tee

    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def process_tokens(words, normalize_plurals=True):
    d = defaultdict(dict)
    for word in words:
        word_lower = word.lower()
        # get dict of cases for word_lower
        case_dict = d[word_lower]
        # increase this case
        case_dict[word] = case_dict.get(word, 0) + 1
    if normalize_plurals:
        # merge plurals into the singular count (simple cases only)
        merged_plurals = {}
        for key in list(d.keys()):
            if key.endswith('s') and not key.endswith("ss"):
                key_singular = key[:-1]
                if key_singular in d:
                    dict_plural = d[key]
                    dict_singular = d[key_singular]
                    for word, count in dict_plural.items():
                        singular = word[:-1]
                        dict_singular[singular] = (
                            dict_singular.get(singular, 0) + count)
                    merged_plurals[key] = key_singular
                    del d[key]
    fused_cases = {}
    standard_cases = {}
    item1 = itemgetter(1)
    for word_lower, case_dict in d.items():
        # Get the most popular case.
        first = max(case_dict.items(), key=item1)[0]
        fused_cases[first] = sum(case_dict.values())
        standard_cases[word_lower] = first
    if normalize_plurals:
        # add plurals to fused cases:
        for plural, singular in merged_plurals.items():
            standard_cases[plural] = standard_cases[singular.lower()]
    return fused_cases, standard_cases


def unigrams_and_bigrams(words, normalize_plurals=True):
    n_words = len(words)
    # make tuples of two words following each other
    bigrams = list(pairwise(words))
    counts_unigrams = defaultdict(int)
    counts_bigrams = defaultdict(int)
    counts_unigrams, standard_form = process_tokens(
        words, normalize_plurals=normalize_plurals)
    counts_bigrams, standard_form_bigrams = process_tokens(
        [" ".join(bigram) for bigram in bigrams],
        normalize_plurals=normalize_plurals)
    # create a copy of counts_unigram so the score computation is not changed
    counts = counts_unigrams.copy()

    # decount words inside bigrams
    for bigram_string, count in counts_bigrams.items():
        bigram = tuple(bigram_string.split(" "))
        # collocation detection (30 is arbitrary):
        word1 = standard_form[bigram[0].lower()]
        word2 = standard_form[bigram[1].lower()]

        if score(count, counts[word1], counts[word2], n_words) > 30:
            # bigram is a collocation
            # discount words in unigrams dict. hack because one word might
            # appear in multiple collocations at the same time
            # (leading to negative counts)
            counts_unigrams[word1] -= counts_bigrams[bigram_string]
            counts_unigrams[word2] -= counts_bigrams[bigram_string]
            counts_unigrams[bigram_string] = counts_bigrams[bigram_string]
    words = list(counts_unigrams.keys())
    for word in words:
        # remove empty / negative counts
        if counts_unigrams[word] <= 0:
            del counts_unigrams[word]
    return counts_unigrams


class WordCloudMod(object):
    def __init__(self, max_words=200, relative_scaling=.5, regexp=None, collocations=True,
                 colormap=None, normalize_plurals=True):
        self.collocations = collocations
        self.max_words = max_words
        self.regexp = regexp
        self.normalize_plurals = normalize_plurals
        self.item1 = itemgetter(1)

    def fit_words(self, frequencies):
        return self.generate_from_frequencies(frequencies)

    def generate_from_frequencies(self, frequencies):
        # make sure frequencies are sorted and normalized
        frequencies = sorted(frequencies.items(), key=self.item1, reverse=True)
        if len(frequencies) <= 0:
            raise ValueError("We need at least 1 word to plot a word cloud, "
                             "got %d." % len(frequencies))
        frequencies = frequencies[:self.max_words]

        # largest entry will be 1
        max_frequency = float(frequencies[0][1])

        frequencies = [(word, freq / max_frequency)
                       for word, freq in frequencies]
        
        self.words_ = dict(frequencies)

        return self.words_

    def process_text(self, text):
        flags = (UNICODE if sys.version < '3' and type(text) is unicode
                 else 0)
        regexp = self.regexp if self.regexp is not None else r"\w[\w']+"

        words = findall(regexp, text, flags)
        # remove stopwords
        words = [word for word in words]
        # remove 's
        words = [word[:-2] if word.lower().endswith("'s") else word
                 for word in words]
        # remove numbers
        words = [word for word in words if not word.isdigit()]

        if self.collocations:
            word_counts = unigrams_and_bigrams(words, self.normalize_plurals)
        else:
            word_counts, _ = process_tokens(words, self.normalize_plurals)

        return word_counts

    def generate_from_text(self, text):
        words = self.process_text(text)
        freqs = self.generate_from_frequencies(words)
        return freqs

    def generate(self, text):
        return self.generate_from_text(text)