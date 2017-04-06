from django.conf.urls import url, include
from django.contrib import admin
from api import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),

    # authentication
    url(r'^(?i)login/(?P<code>[a-zA-z0-9]+)/$', views.authenticate, name='login'),
    url(r'^(?i)refresh/(?P<refresh_token>[a-zA-z0-9]+)/$', views.refresh_access_token, name='logout'),
    url(r'^(?i)logout/(?P<access_token>[a-zA-z0-9]+)/$', views.revoke_access_token, name='logout'),
    url(r'^auth/', include('rest_framework_social_oauth2.urls')),

    url(r'^admin/', admin.site.urls),


    url(r'^(?i)articles/$', views.ArticleView.as_view(), name='article_list'),
    url(r'^(?i)articles/(?P<title>(.*?))/$', views.ArticleView.as_view(), name='article_title'),
]
