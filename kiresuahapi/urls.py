from django.conf.urls import url, include
from django.contrib import admin


urlpatterns = [
    url('', include('rest_framework_social_oauth2.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls'))
]
