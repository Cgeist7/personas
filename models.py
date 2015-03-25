from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
#from django.contrib.gis.db import models as gismodels
#from jsonfield import JSONField
#from djgeojson.fields import PointField
#from treasuremap.fields import LatLongField
import collections


class Nation(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    might = models.PositiveSmallIntegerField(default=0)
    intrigue = models.PositiveSmallIntegerField(default=0)
    magic = models.PositiveSmallIntegerField(default=0)
    wealth = models.PositiveSmallIntegerField(default=0)
    influence = models.PositiveSmallIntegerField(default=0)
    defense = models.PositiveSmallIntegerField(default=0)

    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify(self.name)
        super(Nation, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=128)
    creator = models.ForeignKey(User, unique=False)
    image = models.ImageField(upload_to='location_images/%Y/%m/%d', default='location_images/nowhere.jpg')
    terrain = models.CharField(max_length=128)
    features = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    nation = models.ForeignKey(Nation, blank=True)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    #geom = PointField()

    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify(self.name)
        super(Location, self).save(*args, **kwargs)


    def __str__(self):
        return self.name


class Trait(models.Model):
    CORE = "CO"
    VALUES = "VA"
    BACKGROUND = "BA"
    FLAW = "FL"

    TRAIT_TYPE_CHOICES = (
        (CORE, "Core"),
        (VALUES, "Values"),
        (BACKGROUND, "Background"),
        (FLAW, "Flaw")
        )

    label = models.CharField(max_length=12, choices=TRAIT_TYPE_CHOICES, default="CO", blank=True)
    name = models.CharField(max_length=128)
    character = models.ForeignKey('Character')
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        slug = slugify(self.name)
        super(Trait, self).save(*args, **kwargs)


    def __str__(self):
        return self.name


class SpecialAbility(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    character = models.ForeignKey('Character', null=True, blank=True)
    item = models.ForeignKey('Item', null=True, blank=True)

    def save(self, *args, **kwargs):
        super(SpecialAbility, self).save(*args, **kwargs)


    def __str__(self):
        return "{}: {}".format(self.name, self.description)


class Note(models.Model):
    creator = models.ForeignKey(User, default=0)
    content = models.TextField()
    date = models.DateTimeField(auto_now=True)
    character = models.ForeignKey("Character", blank=True, null=True)
    location = models.ForeignKey("Location", blank=True, null=True)
    organization = models.ForeignKey("Organization", blank=True, null=True)
    scene = models.ForeignKey("Scene", blank=True, null=True)
    chapter = models.ForeignKey("Chapter", blank=True, null=True)
    story = models.ForeignKey("Story", blank=True, null=True)
    rating = models.PositiveSmallIntegerField(default=0)

    def save(self, creator, character, location, organization, scene, chapter, story, *args, **kwargs):
        self.creator = creator
        super(Note, self).save(creator, *args, **kwargs)

    def __str__(self):
        return "{} -- ({})".format(self.content, self.creator)


class Communique(models.Model):
    author = models.ForeignKey("Character", related_name="Author")
    receiver = models.ForeignKey("Character", related_name="Receiver")
    date = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=140)
    rating = models.PositiveSmallIntegerField(default=0)

    def save(self, author, *args, **kwargs):
        self.author = author
        super(Communique, self).save(*args, **kwargs)

    def __str__(self):
        return "{} -- {} to {}".format(self.content, self.author, self.receiver,)


class Skill(models.Model):
    GENERAL = "General"
    INVESTIGATIVE = "Investigative"

    SKILL_TYPES = (
        (GENERAL, "General"),
        (INVESTIGATIVE, "Investigative"))

    name = models.CharField(max_length=32)
    value = models.PositiveSmallIntegerField(default=0)
    s_type = models.CharField(max_length=32, choices=SKILL_TYPES, verbose_name="Skill Type", default="General")
    character = models.ForeignKey('Character')
    description = models.TextField(blank=True)

    def __str__(self):
        return "{}: {}".format(self.name, self.value)


class Item(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    character = models.ForeignKey('Character', blank=True, null=True)

    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify(self.name)
        super(Item, self).save(*args, **kwargs)


    def __str__(self):
        return "{}: {}".format(self.name, self.description)


class Character(models.Model):

    PROTAGONIST = "Protagonist"
    ANTAGONIST = "Antagonist"
    SUPPORTING = "Supporting"
    CREATURE = "Creature"

    CHAR_CHOICES = (
        (PROTAGONIST, "Protagonist"),
        (ANTAGONIST, "Antagonist"),
        (SUPPORTING, "Supporting"),
        (CREATURE, "Creature"))

    creator = models.ForeignKey(User, unique=False, blank=True)
    name = models.CharField(max_length=128, unique=False)
    c_type = models.CharField(choices=CHAR_CHOICES, 
        max_length=32, default="Supporting", verbose_name="Character Type")
    xp = models.PositiveSmallIntegerField(blank=True, default=0)
    description = models.TextField(blank=True)
    age = models.PositiveSmallIntegerField(default=21)
    nationality = models.ForeignKey(Nation, default=1)
    birthplace = models.ForeignKey(Location, related_name='place_of_birth', default=1)
    base_of_operations = models.ForeignKey(Location, related_name='active_in', default=2)

    image = models.ImageField(upload_to='profile_images/%Y/%m/%d', default='profile_images/nobody.jpg')
    slug = models.SlugField(unique=True)

    def save(self, slug=None, creator=None, *args, **kwargs):
        slug = slugify(self.name)
        super(Character, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Relationship(models.Model):
    ALLY = 'Ally'
    ENEMY = 'Enemy'
    FRIEND = 'Friend'
    SPOUSE = 'Spouse'
    PARENT = 'Parent'
    CHILD = 'Child'
    SIBLING = 'Sibling'
    RIVAL = 'Rival'
    LOVER = 'Lover'
    PARTNER = 'Partner'
    MEMBER = 'Member'

    RELATIONSHIP_CLASS_CHOICES = (
        (ALLY, 'Ally'),
        (ENEMY, 'Enemy'),
        (FRIEND, 'Friend'),
        (SPOUSE, 'Spouse'),
        (PARENT, 'Parent'),
        (CHILD, 'Child'),
        (SIBLING, 'Sibling'),
        (RIVAL, 'Rival'),
        (LOVER, 'Lover'),
        (PARTNER, 'Business Partner'),
        (MEMBER, 'Co-member'),
    )

    from_character = models.ForeignKey(Character, related_name="from_character")
    to_character = models.ForeignKey(Character, related_name="to_character")

    relationship_class = models.CharField(max_length=32,
        choices=RELATIONSHIP_CLASS_CHOICES, default='Ally')

    weight = models.PositiveSmallIntegerField(default=50, verbose_name="Strength of the relationship %")

    relationship_description = models.CharField(max_length=128, unique=False)

    def __str__(self):
        return '{} - {} ({}: {}%) --> {}'.format(self.from_character, self.relationship_class, self.relationship_description, self.weight, self.to_character)


class Organization(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(Character, through='Membership', blank=True)
    purpose = models.CharField(max_length=128)
    region = models.CharField(max_length=128)
    location = models.ForeignKey(Location)

    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify(self.name)
        super(Organization, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Membership(models.Model):
    character = models.ForeignKey(Character)
    organization = models.ForeignKey(Organization)
    date_joined = models.DateField()
    role = models.CharField(max_length=128)


class Scene(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    location = models.ForeignKey(Location, blank=True)
    time = models.DateTimeField()
    characters = models.ManyToManyField(Character, blank=True)
    chapter = models.ForeignKey("Chapter")


    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify(self.title)
        super(Scene, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class Chapter(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    story = models.ForeignKey("Story")

    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify(self.title)
        super(Chapter, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Story(models.Model):
    SUPERS = 'Supers'
    FANTASY = 'Fantasy'
    HORROR = 'Horror'
    HISTORICAL = 'Historical'
    SCI_FI = 'Science-Fiction'
    WESTERN = 'Western'
    DRAMA = 'Drama'
    COMEDY = 'Comedy'
    CRIME = 'Crime'
    FABLE = 'Fable'
    MYSTERY = 'Mystery'

    GENRE_CHOICES = (
        (SUPERS, 'Supers'),
        (FANTASY, 'Fantasy'),
        (HORROR, 'Horror'),
        (HISTORICAL, 'Historical'),
        (SCI_FI, "Science Fiction"),
        (WESTERN, 'Western'),
        (DRAMA, 'Drama'),
        (COMEDY, 'Comedy'),
        (CRIME, 'Crime'),
        (FABLE, 'Fable'),
        (MYSTERY, 'Mystery'),
    )

    title = models.CharField(max_length=128)
    author = models.ForeignKey(User)
    publication_date = models.DateField()
    description = models.TextField(blank=True)
    genre = models.CharField(max_length=128, choices=GENRE_CHOICES, default='Fantasy')
    image = models.ImageField(upload_to='story_images/%Y/%m/%d', default='story_images/nobody.jpg')
    background = models.ImageField(upload_to='story_backgrounds/%Y/%m/%d', default='story_backgrounds/nothing.jpg')

    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify(self.title)
        super(Story, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class MainMap(models.Model):
    name = models.CharField(max_length=64)
    story = models.ForeignKey(Story)
    base_latitude = models.FloatField(blank=True)
    base_longitude = models.FloatField(blank=True)
    tiles = models.CharField(max_length=256, blank=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        slug = slugify(self.name)
        super(MainMap, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    website = models.URLField(blank=True)
    image = models.ImageField(
        upload_to='user_images/%Y/%m/%d', default='user_images/nobody.jpg')

    def __str__(self):
        return self.user.username



