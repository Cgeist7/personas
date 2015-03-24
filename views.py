from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from django.forms.formsets import formset_factory
from django.contrib.auth import logout, login, authenticate
from django.db.models import F, Q
from crispy_forms.layout import Submit, HTML
from crispy_forms.helper import FormHelper
from personas.models import Nation, Location, Character, Organization, Relationship, Membership, Trait, SpecialAbility, Item, Story, MainMap, Chapter, Scene, Skill, Note, Communique
from personas.forms import CharacterForm, NoteForm, CommuniqueForm, UserForm, UserProfileForm, SkillForm, TraitForm, TraitFormSetHelper


def index(request):
    context_dict = {}

    try:
        stories = Story.objects.all()

        context_dict['stories'] = stories

    except Story.DoesNotExist:
        pass

    return render(request, 'personas/index.html', context_dict)


def collections(request):
    character_list = Character.objects.all()
    location_list = Location.objects.all()
    organization_list = Organization.objects.all()

    context_dict = {'boldmessage': "Personas", 'characters': character_list,
        'locations': location_list, 'organizations': organization_list}

    return render(request, 'personas/collections.html', context_dict)


def about(request):
    return HttpResponse(
        "<h1>Welcome to the about page!</h1> <a href='/personas/'>Main</a>")


def location(request, location_name_slug):

    context_dict = {}

    try:
        location = Location.objects.get(slug=location_name_slug)

        context_dict['story'] = Story.objects.get(chapter__scene__location__slug=location_name_slug)

        context_dict['location_name'] = location.name
        context_dict['creator'] = location.creator
        context_dict['image'] = location.image
        context_dict['terrain'] = location.terrain
        context_dict['features'] = location.features
        context_dict['description'] = location.description
        context_dict['nation'] = location.nation
        context_dict['latitude'] = location.latitude
        context_dict['longitude'] = location.longitude
        context_dict['slug'] = location.slug
        context_dict['scenes'] = Scene.objects.filter(
            location__name=location.name)
        context_dict['characters'] = Character.objects.filter(
            scene__location__name=location.name)

        context_dict['notes'] = Note.objects.filter(location__name=location.name)

    except Location.DoesNotExist:
        pass

    return render(request, 'personas/location.html', context_dict)


def scene(request, scene_name_slug):

    context_dict = {}

    try:
        scene = Scene.objects.get(slug=scene_name_slug)

        context_dict['scene_title'] = scene.title
        context_dict['slug'] = scene_name_slug
        context_dict['location'] = scene.location
        context_dict['description'] = scene.description
        context_dict['time'] = scene.time
        context_dict['characters'] = Character.objects.filter(scene__title=scene.title)

        context_dict['story'] = Story.objects.get(chapter__scene__title=scene.title)
        context_dict['chapter'] = Chapter.objects.get(scene__title=scene.title)

        context_dict['notes'] = Note.objects.filter(
            scene__title=scene.title)[0:10]

        form = NoteForm(request.POST or None)
        context_dict['form'] = form

        if request.method == 'POST':
            if form.is_valid():

                form = context_dict['form']
                post_scene = scene
                post_creator = request.user
                form.save(scene=post_scene, creator=post_creator, commit=True)

                return HttpResponseRedirect("")

        else:

            context_dict['form'] = NoteForm()

    except Scene.DoesNotExist:
        pass

    return render(request, 'personas/scene.html', context_dict)


def character(request, character_name_slug):

    context_dict = {}

    try:
        character = Character.objects.get(slug=character_name_slug)
        #for item in character:

        context_dict['character_name'] = character.name
        context_dict['creator'] = character.creator
        context_dict['c_type'] = character.c_type
        context_dict['xp'] = character.xp
        context_dict['description'] = character.description

        context_dict['aspects'] = Trait.objects.filter(
            character__name=character.name)

        context_dict['general_skills'] = Skill.objects.filter(
            character__name=character.name).filter(s_type="General")
        context_dict['investigative_skills'] = Skill.objects.filter(
            character__name=character.name).filter(s_type="Investigative")

        context_dict['artifacts'] = Item.objects.filter(
            character__name=character.name)
        context_dict['relationships'] = Relationship.objects.filter(
            from_character__name=character.name)
        context_dict['abilities'] = SpecialAbility.objects.filter(
            character__name=character.name)
        context_dict['notes'] = Note.objects.filter(
            character__name=character.name)

        context_dict['communiques'] = Communique.objects.filter(
            Q(author__name=character.name) |
            Q(receiver__name=character.name))

        context_dict['nationality'] = character.nationality
        context_dict['birthplace'] = character.birthplace
        context_dict['base_of_operations'] = character.base_of_operations
        context_dict['c_type'] = character.c_type

        context_dict['image'] = character.image

        # Note Form Section
        noteform = NoteForm(request.POST, prefix="note")
        context_dict['noteform'] = noteform
        communique_form = CommuniqueForm(request.POST, prefix="comm")
        context_dict['communique_form'] = communique_form

        if request.method == 'POST':
            noteform = NoteForm(request.POST)
            communique_form = CommuniqueForm(request.POST)

            creator = request.user
            post_creator = character
            note_subject = character

            if noteform.is_valid():
                noteform.save(
                    creator=creator, character=note_subject, commit=True)

            if communique_form.is_valid():
                communique_form.save(author=post_creator, commit=True)

            if noteform.is_valid() or communique_form.is_valid():
                return HttpResponseRedirect("")

            else:
                print (context_dict['communique_form'].errors)
                print (context_dict['noteform'].errors)

        else:

            context_dict['noteform'] = NoteForm()
            context_dict['communique_form'] = CommuniqueForm()

    except Character.DoesNotExist:
        pass

    return render(request, 'personas/character.html', context_dict)


def add_character(request):

    if request.method == 'POST':
        character_form = CharacterForm(request.POST)

        creator = request.user

        if character_form.is_valid():
            slug = slugify(character_form.cleaned_data['name'])
            character_form.save(creator=creator, commit=True)

            return HttpResponseRedirect("/personas/add_trait/{}".format(slug))

        else:
            print (character_form.errors)

    else:

        character_form = CharacterForm()

    return render(request, 'personas/add_character.html',
        {'character_form': character_form})


def add_trait(request, character_name_slug):

    TraitFormSet = formset_factory(TraitForm, extra=4, max_num=4)
    helper = TraitFormSetHelper()

    traits = Trait.objects.filter(character__slug=character_name_slug)

    character = Character.objects.get(slug=character_name_slug)

    if request.method == 'POST':

        formset = TraitFormSet(request.POST)

        if formset.is_valid():

            for f in formset:
                cd = f.cleaned_data
                trait_character = character
                name = cd.get('name')
                label = cd.get('label')
                slug = slugify(cd.get('name'))
                trait = Trait(
                    name=name, label=label, character=trait_character, slug=slug)

                trait.save()

            HttpResponseRedirect("/personas/index")

        else:
            print (formset.errors)
            raise forms.ValidationError("Not validating")

    else:

        formset = TraitFormSet()

        helper = TraitFormSetHelper()
        helper.add_input(Submit("submit", "Save"))
        helper.add_input(Submit("cancel", "Cancel"))

    return render(request, 'personas/add_trait.html', {'formset': formset, 'helper': helper,
        'slug': character_name_slug, 'character': character, 'traits': traits})


def chapter(request, chapter_name_slug):

    context_dict = {}

    try:
        chapter = Chapter.objects.get(slug=chapter_name_slug)
        scenes = Scene.objects.filter(chapter__title=chapter.title).order_by(
            'time')

        context_dict['chapter_title'] = chapter.title
        context_dict['chapter_id'] = chapter.id
        context_dict['slug'] = chapter_name_slug
        context_dict['story'] = chapter.story
        context_dict['description'] = chapter.description

        context_dict['scenes'] = scenes

        context_dict['characters'] = Character.objects.filter(
            scene__chapter__title=chapter.title).distinct()
        context_dict['locations'] = Location.objects.filter(
            scene__chapter__title=chapter.title).distinct()


        context_dict['notes'] = Note.objects.filter(
            chapter__title=chapter.title)[0:10]

        form = NoteForm(request.POST or None)
        context_dict['form'] = form

        if request.method == 'POST':
            if form.is_valid():

                form = context_dict['form']
                post_chapter = chapter
                post_creator = request.user
                form.save(chapter=post_chapter, creator=post_creator, commit=True)

                return HttpResponseRedirect("")

        else:

            context_dict['form'] = NoteForm()

    except Chapter.DoesNotExist:
        pass

    return render(request, 'personas/chapter.html', context_dict)


def story(request, story_name_slug):

    context_dict = {}

    try:
        story = Story.objects.get(slug=story_name_slug)
        chapters = Chapter.objects.filter(story__title=story.title)

        context_dict['chapters'] = chapters

        context_dict['story_title'] = story.title
        context_dict['author'] = story.author
        context_dict['publication_date'] = story.publication_date
        context_dict['image'] = story.image
        context_dict['genre'] = story.genre

        mainmaps = MainMap.objects.filter(
            story__title=story.title)
        context_dict['mainmaps'] = mainmaps

        #context_dict['slug'] = story_name_slug
        context_dict['description'] = story.description

        context_dict['notes'] = Note.objects.filter(
            story__title=story.title)

        scenes = Scene.objects.filter(chapter__story__title=story.title)

        context_dict['scenes'] = scenes

        context_dict['characters'] = Character.objects.filter(
                scene__chapter__story__title=story.title).distinct()
        context_dict['locations'] = Location.objects.filter(
                scene__chapter__story__title=story.title).distinct()

        form = NoteForm(request.POST or None)
        context_dict['form'] = form

        if request.method == 'POST':
            if form.is_valid():

                form = context_dict['form']
                post_story = story
                post_creator = request.user
                form.save(story=post_story, creator=post_creator, commit=True)

                return HttpResponseRedirect("")

        else:

            context_dict['form'] = NoteForm()

    except Story.DoesNotExist:
        pass

    return render(request, 'personas/story.html', context_dict)


def mainmap(request, mainmap_slug):
    context_dict = {}

    mainmap = MainMap.objects.get(slug=mainmap_slug)

    try:
        context_dict['map_name'] = mainmap.name
        context_dict['story'] = mainmap.story
        context_dict['base_latitude'] = mainmap.base_latitude
        context_dict['base_longitude'] = mainmap.base_longitude
        context_dict['tile'] = mainmap.tiles

        context_dict['locations'] = Location.objects.filter(
            scene__chapter__story__title=mainmap.story)

    except MainMap.DoesNotExist:
        pass

    return render(request, 'personas/mainmap.html', context_dict)


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = request.user

            if 'image' in request.FILES:
                profile.image = request.FILES['image']

            profile.save()

            registered = True

            return index(request)

        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'personas/register.html',
        {'user_form': user_form, 'profile_form': profile_form, 
        'registered': registered})


def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:

                login(request, user)
                return HttpResponseRedirect('/personas/')
            else:
                return HttpResponse("Your Personas account is disabled.")

        else:
            print("Invalid login details: {}, {}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, 'personas/login.html', {})


@login_required
def user_logout(request):
    logout(request)

    return HttpResponseRedirect('')








