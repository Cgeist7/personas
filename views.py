from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse_lazy
from django.forms.formsets import formset_factory
from django.contrib.auth import logout, login, authenticate
from django.db.models import F, Q
from django.views.generic.edit import DeleteView, UpdateView, FormView, CreateView
from crispy_forms.layout import Submit, HTML
from crispy_forms.helper import FormHelper
from personas.models import Nation, Location, Character, Organization, Relationship, Membership, Trait, SpecialAbility, Item, Story, MainMap, Chapter, Scene, Skill, Note, Communique
from personas.forms import CharacterForm, NoteForm, CommuniqueForm, UserForm, UserProfileForm, SkillForm, TraitForm, TraitFormSetHelper, SkillFormSetHelper, ItemForm, SpecialAbilityForm, RelationshipForm
from personas.forms import StoryForm, ChapterForm, SceneForm


'''class SkillDelete(DeleteView):
    model = Skill
    success_url = reverse_lazy('delete_skill')
    template_name = 'delete_skill.html' 


class StoryCreate(CreateView):
    model = Story
    template_name = 'personas/create_story.html'
    success_url = "/personas/add_character" '''


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
        context_dict['story'] = character.story
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


@login_required
def add_character(request):

    if request.method == 'POST':
        character_form = CharacterForm(request.POST, request.FILES)

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


@login_required
def create_story(request):

    if request.method == 'POST':
        story_form = StoryForm(request.POST, request.FILES)

        creator = request.user

        if story_form.is_valid():
            slug = slugify(story_form.cleaned_data['title'])

            story_form.save(creator=creator, commit=True)

            return HttpResponseRedirect("/personas/story/{}".format(slug))

        else:
            print (story_form.errors)

    else:

        story_form = StoryForm()

    return render(request, 'personas/create_story.html',
        {'story_form': story_form})


@login_required
def add_trait(request, character_name_slug):

    traits = Trait.objects.filter(character__slug=character_name_slug)

    character = Character.objects.get(slug=character_name_slug)
    story = character.story

    if request.method == 'POST':

        form = TraitForm(request.POST)

        if form.is_valid():
            trait_character = character

            #for f in formset:
            cd = form.cleaned_data
            if not cd.get('name'):
                pass
            else:
                name = cd.get('name')
                label = cd.get('label')
                slug = slugify(cd.get('name'))
                trait = Trait(
                    name=name, label=label,
                    character=trait_character, slug=slug)

                trait.save()
                form = TraitForm()

            return HttpResponseRedirect("")

        else:
            print (form.errors)

    else:

        form = TraitForm()

    return render(request, 'personas/add_trait.html', {'form': form,
        'slug': character_name_slug, 'character': character,
        'traits': traits, 'story':story})


@login_required
def add_skills(request, character_name_slug):

    #SkillFormSet = formset_factory(SkillForm, extra=10, max_num=10)
    #helper = SkillFormSetHelper()

    skills = Skill.objects.filter(character__slug=character_name_slug)

    character = Character.objects.get(slug=character_name_slug)

    story = character.story

    general_skills = Skill.objects.filter(
            character__slug=character_name_slug).filter(s_type="General")
    investigative_skills = Skill.objects.filter(
            character__slug=character_name_slug).filter(s_type="Investigative")

    if request.method == 'POST':

        form = SkillForm(request.POST or None)

        if form.is_valid():
            skill_character = character

            #for f in formset:
            cd = form.cleaned_data
            if cd.get('name') == None:
                pass
            else:
                name = cd.get('name')
                value = cd.get('value')
                s_type = cd.get('s_type')
                skill = Skill(
                    name=name, value=value, character=skill_character, s_type=s_type)

                skill.save()
                form = SkillForm()

            HttpResponseRedirect("")

        else:
            print (form.errors)

    else:
        form = SkillForm()

        #helper = SkillFormSetHelper()
        #helper.add_input(Submit("submit", "Save"))
        #helper.add_input(Submit("cancel", "Cancel"))

    return render(request, 'personas/add_skills.html', {'form': form,
        'slug': character_name_slug, 'character': character,
        'general_skills': general_skills,
        'investigative_skills':investigative_skills, 'story':story})


@login_required
def add_ability_artifact(request, character_name_slug):

    abilities = SpecialAbility.objects.filter(character__slug=character_name_slug)
    artifacts = Item.objects.filter(character__slug=character_name_slug)

    character = Character.objects.get(slug=character_name_slug)
    story = character.story

    if request.method == 'POST':

        ability_form = SpecialAbilityForm(request.POST or None, prefix="ability")
        artifact_form = ItemForm(request.POST or None, prefix="artifact")

        if ability_form.is_valid():

            ability_data = ability_form.cleaned_data

            if ability_data.get('name') == None:
                pass
            else:
                name = ability_data.get('name')
                description = ability_data.get('description')
                ability = SpecialAbility(
                    name=name, description=description, character=character)

                ability.save()
                ability_form = SpecialAbilityForm()

        if artifact_form.is_valid():

            artifact_data = artifact_form.cleaned_data
            if artifact_data.get('name') == None:
                pass
            else:
                name = artifact_data.get('name')
                description = artifact_data.get('description')
                slug = slugify(name)
                artifact = Item(
                    name=name, description=description, character=character, slug=slug)

                artifact.save()
                artifact_form = ItemForm()

            HttpResponseRedirect("")

        else:
            print (ability_form.errors, artifact_form.errors)

    else:
        ability_form = SpecialAbilityForm()
        artifact_form = ItemForm()

        #helper = SkillFormSetHelper()
        #helper.add_input(Submit("submit", "Save"))
        #helper.add_input(Submit("cancel", "Cancel"))

    return render(request, 'personas/add_ability_artifact.html', {
        'slug': character_name_slug, 'character': character,
        'abilities': abilities, 'artifacts': artifacts, 'story':story,
        'ability_form':ability_form, "artifact_form": artifact_form
        })


@login_required
def add_relationships(request, character_name_slug):

    relationships = Relationship.objects.filter(Q(to_character__slug=character_name_slug) |
        Q(from_character__slug=character_name_slug))

    character = Character.objects.get(slug=character_name_slug)

    story = character.story
    data = {"from_character": character}

    if request.method == 'POST':

        relationship_form = RelationshipForm(request.POST or None)

        if relationship_form.is_valid():

            relationship_data = relationship_form.cleaned_data

            if relationship_data.get('to_character') == None:
                pass
            else:
                to_character = relationship_data.get('to_character')
                relationship_description = relationship_data.get('relationship_description')
                weight = relationship_data.get('weight')
                relationship_class = relationship_data.get('relationship_class')
                relationship = Relationship(
                    from_character=character,
                    to_character=to_character,
                    relationship_description=relationship_description,
                    relationship_class=relationship_class, weight=weight)

                relationship.save()
                relationship_form = RelationshipForm(story=story)

            HttpResponseRedirect("")

        else:
            print (relationship_form.errors)

    else:
        relationship_form = RelationshipForm(story=story)

    return render(request, 'personas/add_relationships.html', {
        'slug': character_name_slug, 'character': character, 'story':story,
        'relationships': relationships, 'relationship_form':relationship_form})


@login_required
def add_chapter(request, story_title_slug):

    story = Story.objects.get(slug=story_title_slug)

    chapters = Chapter.objects.filter(story__slug=story_title_slug).order_by("-number")

    characters = Character.objects.filter(story=story)

    if request.method == 'POST':

        chapter_form = ChapterForm(request.POST or None)

        if chapter_form.is_valid():

            chapter_data = chapter_form.cleaned_data

            if chapter_data.get('title') == None:
                pass
            else:
                title = chapter_data.get('title')
                number = chapter_data.get('number')
                chapter_description = chapter_data.get('description')
                chapter_slug = slugify(chapter_data.get('title'))
                chapter = Chapter(title=title, story=story, number=number,
                    description=chapter_description, slug=chapter_slug)

                chapter.save()
                chapter_form = ChapterForm()

            HttpResponseRedirect("personas/chapter/{}".format(chapter_slug))

        else:
            print (chapter_form.errors)

    else:
        chapter_form = ChapterForm()

    return render(request, 'personas/add_chapter.html', {
        'slug': story_title_slug, 'story':story,
        'chapters': chapters, 'chapter_form':chapter_form})


@login_required
def add_scene(request, story_title_slug):

    story = Story.objects.get(chapter__story__slug=story_title_slug)

    scenes = Scene.objects.filter(chapter__story__slug=story_title_slug).order_by("-number")

    characters = Character.objects.filter(story=story)

    if request.method == 'POST':

        scene_form = SceneForm(request.POST or None)

        if scene_form.is_valid():

            scene_data = scene_form.cleaned_data

            if scene_data.get('title') == None:
                pass
            else:
                title = scene_data.get('title')
                location = scene_data.get('location')
                time = scene_data.get('time')
                chapter = scene.data.get('chapter')
                characters = scene_data.get('characters')
                scene_description = scene_data.get('description')
                scene_slug = slugify(scene_data.get('title'))
                scene = Scene(title=title, location=location, time=time,
                    description=scene_description, slug=scene_slug,
                    characters=characters)

                scene.save()
                scene_form = SceneForm()

            HttpResponseRedirect("")

        else:
            print (scene_form.errors)

    else:
        scene_form = SceneForm()

    return render(request, 'personas/add_scene.html', {
        'slug': story_title_slug, 'story':story, 'scenes': scenes,
        'scene_form':scene_form, 'characters':characters})


def chapter(request, chapter_name_slug):

    context_dict = {}

    try:
        chapter = Chapter.objects.get(slug=chapter_name_slug)
        scenes = Scene.objects.filter(chapter__title=chapter.title).order_by(
            'time')

        context_dict['chapter_title'] = chapter.title
        context_dict['chapter'] = chapter
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

        context_dict['story'] = story
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
                story=story).distinct()
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
        profile_form = UserProfileForm(request.POST, request.FILES)

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








