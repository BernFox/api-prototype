from django.conf.urls import *
from django.contrib import admin
from api import QuestAnswerResource

QuAs_res = QuestAnswerResource()

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'API.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(QuAs_res.urls)),
)
