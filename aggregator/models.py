from django.db import models
from django.utils.translation import ugettext as T
from django.db import IntegrityError
from django.template.defaultfilters import slugify
from django.conf import settings


class AutoSlugifyOnSaveModel(models.Model):
    """
    http://www.laurencegellert.com/2016/04/django-automatic-slug-generator/
    Models that inherit from this class get an auto filled slug property based on the models name property.
    Correctly handles duplicate values (slugs are unique), and truncates slug if value too long.
    The following attributes can be overridden on a per model basis:
    * value_field_name - the value to slugify, default 'name'
    * slug_field_name - the field to store the slugified value in, default 'slug'
    * max_interations - how many iterations to search for an open slug before raising IntegrityError, default 1000
    * slug_separator - the character to put in place of spaces and other non url friendly characters, default '-'
    """

    def save(self, *args, **kwargs):
        pk_field_name = self._meta.pk.name
        value_field_name = getattr(self, 'value_field_name', 'title')
        slug_field_name = getattr(self, 'slug_field_name', 'slug')
        max_interations = getattr(self, 'slug_max_iterations', 1000)
        slug_separator = getattr(self, 'slug_separator', '-')

        # fields, query set, other setup variables
        slug_field = self._meta.get_field(slug_field_name)
        slug_len = slug_field.max_length
        queryset = self.__class__.objects.all()

        # if the pk of the record is set, exclude it from the slug search
        current_pk = getattr(self, pk_field_name)

        if current_pk:
            queryset = queryset.exclude(**{pk_field_name: current_pk})

        # setup the original slug, and make sure it is within the allowed length
        slug = slugify(getattr(self, value_field_name)).replace('-', '_')

        if slug_len:
            slug = slug[:slug_len]

        original_slug = slug

        # iterate until a unique slug is found, or max_iterations
        counter = 2
        while queryset.filter(**{slug_field_name: slug}).count() > 0 and counter < max_interations:
            slug = original_slug
            suffix = '%s%s' % (slug_separator, counter)
            if slug_len and len(slug) + len(suffix) > slug_len:
                slug = slug[:slug_len-len(suffix)]
            slug = '%s%s' % (slug, suffix)
            counter += 1

        if counter == max_interations:
            raise IntegrityError('Unable to locate unique slug')

        setattr(self, slug_field.attname, slug)

        super(AutoSlugifyOnSaveModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class AutoSlugifyOnSaveVideoModel(models.Model):
    def save(self, *args, **kwargs):
        pk_field_name = self._meta.pk.name
        value_field_name = getattr(self, 'value_field_name', 'channel_title')
        slug_field_name = getattr(self, 'slug_field_name', 'slug')
        max_interations = getattr(self, 'slug_max_iterations', 1000)
        slug_separator = getattr(self, 'slug_separator', '-')

        # fields, query set, other setup variables
        slug_field = self._meta.get_field(slug_field_name)
        slug_len = slug_field.max_length
        queryset = self.__class__.objects.all()

        # if the pk of the record is set, exclude it from the slug search
        current_pk = getattr(self, pk_field_name)

        if current_pk:
            queryset = queryset.exclude(**{pk_field_name: current_pk})

        slug = slugify(getattr(self, value_field_name)).replace('-', '_')

        if slug_len:
            slug = slug[:slug_len]

        setattr(self, slug_field.attname, slug)

        super(AutoSlugifyOnSaveVideoModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


if settings.RESEARCH_MODULE:
    class ScienceCat(AutoSlugifyOnSaveModel):
        if not settings.EXISTING_SITE:
            id = models.AutoField(primary_key=True)
            title = models.CharField(max_length=250, verbose_name=T("Article title"), unique=True)
        else:
            title = models.CharField(max_length=250, verbose_name=T("Article title"), primary_key=True)
        slug = models.CharField(max_length=140, verbose_name=T("Category slug"), blank=True, null=True)

        class Meta:
            ordering = ('title',)

        def __unicode__(self):
            return '%s' %(self.title)

        def __str__(self):
            return '%s' %(self.title)


    class ScienceArticle(AutoSlugifyOnSaveModel):
        if not settings.EXISTING_SITE:
            id = models.AutoField(primary_key=True)
            title = models.CharField(max_length=250, verbose_name=T("Article title"), unique=True)
        else:
            title = models.CharField(max_length=250, verbose_name=T("Article title"), primary_key=True)
        text = models.TextField(default='', verbose_name=T("Article text"))
        summary = models.TextField(default='', verbose_name=T("Article summary"))
        sentiment = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, verbose_name=T("Sentiment"))
        file = models.FileField(upload_to="uploads/research/", blank=True, null=True, verbose_name=T("PDF"))
        abs_url = models.URLField(verbose_name=T("URL to abstract"), null=True, blank=True)
        pdf_url = models.URLField(verbose_name=T("URL to PDF"), null=True, blank=True)
        date =  models.DateTimeField(verbose_name=T("Date"), null=True, blank=True)
        slug = models.CharField(max_length=140, verbose_name=T("Article slug"), blank=True, null=True)
        category = models.ForeignKey(ScienceCat, on_delete=models.CASCADE)
        got_pdf =  models.BooleanField(default=0)

        class Meta:
            ordering = ('date',)

        def __unicode__(self):
            return '%s' %(self.title)

        def __str__(self):
            return '%s' %(self.title)

class BooksCat(AutoSlugifyOnSaveModel):
    if not settings.EXISTING_SITE:
        id = models.AutoField(primary_key=True)
        title = models.CharField(max_length=150, verbose_name=T("Book category"), unique=True)
    else:
        title = models.CharField(max_length=150, verbose_name=T("Book category"), primary_key=True)
    slug = models.CharField(max_length=50, blank=True, null=True)
    enabled = models.BooleanField(default=0, verbose_name=T("Do show?"))

    def __unicode__(self):
        return '%s' %(self.title)

    def __str__(self):
        return '%s' %(self.title)


class Books(AutoSlugifyOnSaveModel):
    if not settings.EXISTING_SITE:
        id = models.AutoField(primary_key=True)
        title = models.CharField(max_length=250, verbose_name=T("Book title"), unique=True)
    else:
        title = models.CharField(max_length=250, verbose_name=T("Book title"), primary_key=True)
    asin = models.CharField(max_length=20, verbose_name=T("ASIN"))
    authors = models.CharField(max_length=200, verbose_name=T("Authors"))
    publication_date = models.DateTimeField(verbose_name=T("Date"), null=True, blank=True)
    pages = models.IntegerField(verbose_name=T("Pages"), null=True, blank=True)
    medium_image_url = models.URLField(verbose_name=T("Image URL"), null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=T("True"))
    currency = models.CharField(max_length=10, verbose_name=T("Currency"), blank=True, null=True)
    review = models.TextField(verbose_name=T("Editorial review"), blank=True, null=True)
    summary = models.TextField(verbose_name=T("Summary"), blank=True, null=True)
    categories = models.ManyToManyField(BooksCat, blank=True, verbose_name=T("Categories"))
    image = models.ImageField(upload_to="uploads/books/", blank=True, null=True, verbose_name=T("Image"))
    got_image = models.BooleanField(default=0)
    slug = models.CharField(max_length=150, verbose_name=T("Book slug"), blank=True, null=True)

    def __unicode__(self):
        return '%s' %(self.title)

    def __str__(self):
        return '%s' %(self.title)


class Video(AutoSlugifyOnSaveVideoModel):
    if not settings.EXISTING_SITE:
        id = models.AutoField(primary_key=True)
        title = models.CharField(max_length=140, verbose_name=T("Video"), unique=True)
    else:
        title = models.CharField(max_length=140, verbose_name=T("Video"), primary_key=True)
    description = models.TextField(default='')
    date = models.DateTimeField(verbose_name=T("Date"))
    channel_title = models.CharField(max_length=140, verbose_name=T("Channel title"))
    slug = models.CharField(max_length=140, verbose_name=T("Channel slug"), blank=True, null=True)
    channel_id =  models.CharField(max_length=60, verbose_name=T("Channel ID"))
    video_id =  models.CharField(max_length=40, verbose_name=T("Video ID"))

    class Meta:
        ordering = ('date',)

    def __unicode__(self):
        return '%s' %(self.title)

    def __str__(self):
        return '%s' %(self.title)


class Category(AutoSlugifyOnSaveModel):
    if not settings.EXISTING_SITE:
        id = models.AutoField(primary_key=True)
        title = models.CharField(max_length=40, verbose_name=T("Categoery"), unique=True)
    else:
        title = models.CharField(max_length=40, verbose_name=T("Categoery"), primary_key=True)
    slug = models.CharField(max_length=40, blank=True, null=True)
    thumbnail = models.ImageField(upload_to="uploads/", blank=True, null=True, verbose_name=T("Image thumbnail"), height_field=None, width_field=None)

    class Meta:
        ordering = ('title',)

    def __unicode__(self):
        return '%s' %(self.title)

    def __str__(self):
        return '%s' %(self.title)


class Tags(AutoSlugifyOnSaveModel):
    TAG_TYPES = (
        ('T', 'Twitter'),
        ('A', 'Article tag collector'),
        ('D', 'Database tag collector'),
        ('G', 'Google Adwords'),
    )
    if not settings.EXISTING_SITE:
        id = models.AutoField(primary_key=True)
        title = models.CharField(max_length=30, verbose_name=T("Tag"), unique=True)
    else:
        title = models.CharField(max_length=30, verbose_name=T("Tag"), primary_key=True)
    slug = models.CharField(max_length=30, blank=True, null=True)
    active = models.BooleanField(default=0)
    tag_type = models.CharField(max_length=10, verbose_name=T("Tag type"), choices=TAG_TYPES, default='A',)

    def __unicode__(self):
        return '%s' %(self.title)

    def __str__(self):
        return '%s' %(self.title)


class Sources(models.Model):
    if not settings.EXISTING_SITE:
        id = models.AutoField(primary_key=True)
        feed = models.URLField(verbose_name=T("Feed URL"), unique=True)
    else:
        feed = models.URLField(verbose_name=T("Feed URL"), primary_key=True)
    name = models.CharField(max_length=40, verbose_name=T("Your name"), blank=True, null=True)
    email = models.EmailField(max_length=60, verbose_name=T("Your email"), blank=True, null=True)
    twitter_handle = models.CharField(max_length=30, verbose_name=T("Twitter handle"), blank=True, null=True)
    active =  models.BooleanField(default=False)
    dead = models.BooleanField(default=False)
    failures = models.SmallIntegerField(verbose_name=T("Failures"), default=0)

    def __unicode__(self):
        return '(%s) %s %s' %(self.feed, self.twitter_handle, self.name)

    def __str__(self):
        return '(%s) %s %s' %(self.feed, self.twitter_handle, self.name)


class Twits(models.Model):
    tweet_id = models.BigIntegerField(primary_key=True, verbose_name=T("Tweet ID"))
    content = models.CharField(max_length=140, verbose_name=T("Tweet text"))
    twitter_handle = models.ForeignKey(Sources, on_delete=models.CASCADE)
    screen_name = models.CharField(max_length=30, verbose_name=T("Twitter screen name"))
    profile_image = models.CharField(max_length=250, blank=True, null=True, verbose_name=T("Twitter profile image URL"))
    date = models.DateTimeField(verbose_name=T("Date"))
    hashtags =  models.CharField(max_length=140, verbose_name=T("Hashtags"), blank=True, null=True)
    tags =  models.ManyToManyField(Tags, blank=True, verbose_name=T("Tags"))

    class Meta:
        ordering = ('date',)

    def __unicode__(self):
        return '%s' %(self.content)

    def __str__(self):
        return '%s' %(self.content)


class TwitsByTag(models.Model):
    tweet_id = models.BigIntegerField(primary_key=True, verbose_name=T("Tweet ID"))
    content = models.CharField(max_length=140, verbose_name=T("Tweet text"))
    twitter_handle = models.CharField(max_length=40, verbose_name=T("Twitter handle"))
    screen_name = models.CharField(max_length=30, verbose_name=T("Twitter screen name"))
    profile_image = models.CharField(max_length=250, blank=True, null=True, verbose_name=T("Twitter profile image URL"))
    date = models.DateTimeField(verbose_name=T("Date"))
    hashtags =  models.CharField(max_length=140, verbose_name=T("Hashtags"), blank=True, null=True)
    tags =  models.ManyToManyField(Tags, blank=True, verbose_name=T("Tags"))
    by_tag =  models.CharField(max_length=40, verbose_name=T("What tag is used to query it"))

    class Meta:
        ordering = ('date',)

    def __unicode__(self):
        return '(%s) %s %s' %(self.content, self.screen_name, self.hashtags)

    def __str__(self):
        return '(%s) %s %s' %(self.content, self.screen_name, self.hashtags)


class Post(AutoSlugifyOnSaveModel):
    if not settings.EXISTING_SITE:
        id = models.AutoField(primary_key=True)
        title = models.CharField(max_length=250, unique=True, verbose_name=T("Title"))
    else:
        title = models.CharField(max_length=250, primary_key=True, verbose_name=T("Title"))
    content = models.TextField(verbose_name=T("Article body"), default='', blank=True)
    working_content = models.TextField(verbose_name=T("Temporal article body"), default='', blank=True)
    feed_content = models.TextField(verbose_name=T("Content from the feed"), default='', blank=True)
    summary =  models.TextField(verbose_name=T("Summary"), default='', blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=T("Categoery"))
    feed = models.ForeignKey(Sources, on_delete=models.CASCADE, verbose_name=T("Feed URL"))
    date = models.DateTimeField(verbose_name=T("Date"))
    pub_date = models.DateTimeField('date published', blank=True, null=True)
    tags = models.ManyToManyField(Tags, blank=True, verbose_name=T("Tags"))
    sentiment = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, verbose_name=T("Sentiment"))
    image = models.ImageField(upload_to="uploads/", blank=True, null=True, verbose_name=T("Image"), height_field=None, width_field=None)
    wordcloud = models.ImageField(upload_to="static/wordcloud/", blank=True, null=True, verbose_name=T("Wordcloud image"), height_field=None, width_field=None)
    videos = models.ManyToManyField(Video, blank=True, verbose_name=T("Videos"))
    url = models.URLField(verbose_name=T("URL to article"))
    slug = models.CharField(max_length=120, blank=True, null=True)
    parsed = models.BooleanField(default=0)
    books = models.ManyToManyField(Books, blank=True, verbose_name=T("Books"))
    got_books = models.BooleanField(default=0, verbose_name=T("Got books?"))
    hits = models.IntegerField(default=0, verbose_name=T("Hits"))
    dead = models.BooleanField(default=False)

    class Meta:
        ordering = ('date',)

    def __unicode__(self):
        return '(%s) %s %s %s %s' %(self.title, self.content, self.working_content, self.summary, self.tags)

    def __str__(self):
        return '(%s) %s %s %s %s' %(self.title, self.content, self.working_content, self.summary, self.tags)


class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40, verbose_name=T("Your name"))
    email = models.EmailField(max_length=60, blank=False, null=False, verbose_name=T("Your email"))
    message = models.TextField(verbose_name=T("Your message"))

    def __unicode__(self):
        return '(%s) %s' %(self.name, self.message)

    def __str__(self):
        return '(%s) %s' %(self.name, self.message)

class Subscribers(models.Model):
    SUB_STATUSES = (
        ('S', 'Subscribed'),
        ('C', 'Confirmed'),
        ('U', 'Unsubscribed'),
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40, verbose_name=T("Your name"))
    email = models.EmailField(max_length=60, verbose_name=T("Your email"), unique=True)
    email_confirmed = models.BooleanField()
    date_subscribed = models.DateTimeField(verbose_name=T("Date subscribed"), blank=False)
    date_confirmed = models.DateTimeField(verbose_name=T("Date confirmed"), blank=True, null=True)
    date_unsubscribed = models.DateTimeField(verbose_name=T("Date unsubscribed"), blank=True, null=True)
    status = models.CharField(max_length=3, verbose_name=T("Subscriber status"), choices=SUB_STATUSES, default='S')

    def __unicode__(self):
        return '%s' %(self.name)

    def __str__(self):
        return '%s' %(self.name)

if settings.DEFINITIONS_MODULE:
    class TermLinks(models.Model):
        LINK_STATUSES = (
            ('T', 'Term link'),
            ('U', 'Unknown'),
            ('A', 'Article in db'),
        )
        link = models.URLField(verbose_name=T("URL"), primary_key=True)
        status_parsed = models.CharField(max_length=5, verbose_name=T("Status"), choices=LINK_STATUSES, default='U')

    class Terms(models.Model):
        if not settings.EXISTING_SITE:
            id = models.AutoField(primary_key=True)
            term =  models.CharField(max_length=60, verbose_name=T("Term"), unique=True)
        else:
            term =  models.CharField(max_length=60, verbose_name=T("Term"), primary_key=True)
        text =  models.TextField(verbose_name=T("Term description"))
        summary =  models.TextField(verbose_name=T("Summary"), null=True, blank=True)
        image =  models.CharField(max_length=140, verbose_name=T("Image"))
        movies =  models.CharField(max_length=250, verbose_name=T("Video links"))

        def __unicode__(self):
            return '(%s) %s' %(self.term, self.text)

        def __str__(self):
            return '(%s) %s' %(self.term, self.text)
