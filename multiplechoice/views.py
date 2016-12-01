# from django.shortcuts import render
from django.views.generic import ListView, DetailView
from multiplechoice.models import Question

class QuestionList(ListView):
    model = Question
    queryset = Question.objects.filter(active=True).order_by('-created_date') # default = Question.objects.all()
    context_object_name = "questions" # default = object_list
    template = "multiplechoice/question_list.html" # default = question_list.html
    paginate_by = 5

class QuestionDetail(DetailView):
    model = Question
    content_object_name = "question" # defalt = object