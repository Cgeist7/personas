from django.conf.urls import patterns, url
from personas import views
#from djgeojson.views import GeoJSONLayerView

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^about', views.about, name='about'),
    url(r'^add_character/$', views.add_character, name='add_character'),
    url(r'^add_trait/(?P<character_name_slug>[\w\-]+)/$', views.add_trait, name='add_trait'),
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