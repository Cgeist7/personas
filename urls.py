from django.conf.urls import patterns, url
from personas import views
#from djgeojson.views import GeoJSONLayerView

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^about', views.about, name='about'),
    url(r'^add_character/$', views.add_character, name='add_character'),
    url(r'^add_trait/(?P<character_name_slug>[\w\-]+)/$', views.add_trait, name='add_trait'),
    url(r'^add_skills/(?P<character_name_slug>[\w\-]+)/$', views.add_skills, name='add_skills'),
    url(r'^add_ability_artifact/(?P<character_name_slug>[\w\-]+)/$', views.add_ability_artifact, name='add_ability_artifact'),
    url(r'^add_relationships/(?P<character_name_slug>[\w\-]+)/$', views.add_relationships, name='add_relationships'),
    #url(r'^delete_skill/?P<pk>\d+/$', views.SkillDelete.as_view(), name='delete_skill'),
    url(r'^create_story/$', views.create_story, name="create_story"),
    url(r'^add_chapter/(?P<story_title_slug>[\w\-]+)/$', views.add_chapter, name='add_chapter'),
    url(r'^add_scene/(?P<story_title_slug>[\w\-]+)/$', views.add_scene, name='add_scene'),
    url(r'^register/$', views.register, name='register'),
    url(r'^collections/$', views.collections, name='collections'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^mainmap/(?P<mainmap_slug>[\w\-]+)/$', views.mainmap, name='mainmap'),
    url(r'^character/(?P<character_name_slug>[\w\-]+)/$', views.character, name='character'),
    url(r'^location/(?P<location_name_slug>[\w\-]+)/$', views.location, name='location'),
    url(r'^scene/(?P<scene_name_slug>[\w\-]+)/$', views.scene, name='scene'),
    url(r'^chapter/(?P<chapter_name_slug>[\w\-]+)/$', views.chapter, name='chapter'),
    url(r'^story/(?P<story_name_slug>[\w\-]+)/$', views.story, name='story'),
#url(r'^data.geojson$', GeoJSONLayerView.as_view(model=MushroomSpot), name='data'),
    )