from django.conf.urls import url, include
from django.contrib import admin
from api import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'articles', views.ArticleViewSet)
router.register(r'tags', views.TagViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),

    # authentication
    url(r'^(?i)login/(?P<code>[a-zA-z0-9]+)/$', views.authenticate, name='login'),
    url(r'^(?i)refresh/(?P<refresh_token>[a-zA-z0-9]+)/$', views.refresh_access_token, name='logout'),
    url(r'^(?i)logout/(?P<access_token>[a-zA-z0-9]+)/$', views.revoke_access_token, name='logout'),
    url(r'^auth/', include('rest_framework_social_oauth2.urls')),

    url(r'^admin/', admin.site.urls),

    url(r'^(?i)search/(?P<search_term>[a-zA-z0-9]+)/$', views.search_articles_tags, name='search'),
    url(r'^(?i)articles/$', views.ArticleViewSet, name='article_list'),
    url(r'^(?i)articles/(?P<selector>(.*?))/$', views.ArticleViewSet, name='article_title'),

    url(r'^(?i)tags/$', views.TagViewSet, name='tag_list'),
]
