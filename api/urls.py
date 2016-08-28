from django.conf.urls import url, include
from api import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),

    url(r'^(?i)login/(?P<code>[a-zA-z0-9]+)/$', views.auth, name='login'),
    url(r'^(?i)logout/$', views.revoke, name='logout'),

    url(r'^(?i)todo/$', views.ToDoList.as_view()),
    url(r'^(?i)todo/(?P<pk>[0-9]+)/$', views.ToDoDetail.as_view()),

    url(r'^(?i)markup/(?P<id>[0-9]+)/$', views.MarkupList.as_view(), name='markup_list'),
    url(r'^(?i)markup/(?P<id>[0-9]+)/(?P<pk>[0-9]+)/$', views.MarkupDetail.as_view(), name='markup_get_post_put'),

    url(r'^(?i)entry/$', views.EntryView.as_view(), name='entry_list'),

    url(r'^(?i)message/$', views.PortFolioMessageList.as_view(), name='message_list'),

    url('', include('rest_framework_social_oauth2.urls')),

]
