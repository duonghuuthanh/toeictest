from django.conf.urls import url
from multiplechoice.views import QuestionList, QuestionDetail

urlpatterns = [
    url(r'^$', QuestionList.as_view(), name='question-list'),   
    url(r'^(?P<pk>[0-9]+)/$', QuestionDetail.as_view(), name='question-detail')
]