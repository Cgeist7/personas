from django import forms
from django.forms.models import modelform_factory
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from personas.models import Nation, Location, Character, Organization, Relationship, Membership, Trait, SpecialAbility, Item, Story, Scene, Chapter, Skill, Note, Communique, UserProfile
#from treasuremap.forms import LatLongField

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions


class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = "__all__"
        exclude = ['slug', 'creator']

    def __init__(self, *args, **kwargs):
        super(CharacterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout.append(
            FormActions(
                HTML("""<a role="button" class="btn btn-default"
                        href="#">Cancel</a>"""),
                Submit('save', 'Submit'),))

    def save(self, creator, commit=True):
        instance = super(CharacterForm, self).save(commit=False)
        instance.slug = slugify(instance.name)
        instance.creator = creator
        instance.save()
        return instance


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["name", "value", "s_type"]

    def __init__(self, *args, **kwargs):
        super(SkillForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.layout = Layout(Row('name','value'),
            's_type',
        )
        self.helper.layout.append(
            FormActions(
                HTML("""<a role="button" class="btn btn-default"
                        href="#">Cancel</a>"""),
                Submit('save', 'Submit'),))


class SkillFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(SkillFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(Row('name','value'),
            's_type',
        )
        self.render_required_fields = True,

class TraitForm(forms.ModelForm):
    class Meta:
        model = Trait
        fields = ['name', 'label']

    def __init__(self, *args, **kwargs):
        super(TraitForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout.append(
            FormActions(
                HTML("""<a role="button" class="btn btn-default"
                        href="#">Cancel</a>"""),
                Submit('save', 'Submit'),))


class TraitFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(TraitFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            'label',
            'name',
        )
        self.render_required_fields = True,


class SpecialAbilityForm(forms.ModelForm):
    class Meta:
        model = SpecialAbility
        fields = ["name", "description",]

    def __init__(self, *args, **kwargs):
        super(SpecialAbilityForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.layout = Layout(
            'name',
            'description',
        )
        self.helper.layout.append(
            FormActions(
                HTML("""<a role="button" class="btn btn-default"
                        href="#">Cancel</a>"""),
                Submit('save', 'Submit'),))


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["name", "description",]

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.layout = Layout(
            'name',
            'description',
        )
        self.helper.layout.append(
            FormActions(
                HTML("""<a role="button" class="btn btn-default"
                        href="#">Cancel</a>"""),
                Submit('save', 'Submit'),))


class SceneForm(forms.ModelForm):
    class Meta:
        model = Scene
        fields = ['title', 'description', 'location']


class NoteForm(forms.ModelForm):
    # Something isn't working here

    class Meta:
        model = Note
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout.append(
            FormActions(
                HTML("""<a role="button" class="btn btn-default"
                        href="#">Cancel</a>"""),
                Submit('save', 'Submit'),))

    def save(self, creator, character=None, scene=None, location=None, organization=None, chapter=None, story=None, commit=True):
        instance = super(NoteForm, self).save(commit=False)
        instance.character = character
        instance.creator = creator
        instance.scene = scene
        instance.location = location
        instance.chapter = chapter
        instance.story = story
        instance.organization = organization
        instance.save(creator, character, scene, chapter, story, organization, location)
        return instance


class CommuniqueForm(forms.ModelForm):
    # Something isn't working here

    class Meta:
        model = Communique
        fields = ('content', 'receiver')

    def __init__(self, *args, **kwargs):
        super(CommuniqueForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout.append(
            FormActions(
                HTML("""<a role="button" class="btn btn-default"
                        href="#">Cancel</a>"""),
                Submit('save', 'Submit'),))

    def save(self, author, commit):
        instance = super(CommuniqueForm, self).save(commit=False)
        instance.author = author
        instance.save(author)
        return instance


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.layout.append(
            FormActions(
                HTML("""<a role="button" class="btn btn-default"
                        href="#">Cancel</a>"""),
                Submit('save', 'Submit'),))



class UserProfileForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = UserProfile
        fields = ('website', 'image')

