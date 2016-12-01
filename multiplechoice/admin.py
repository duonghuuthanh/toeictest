from django.contrib import admin
from multiplechoice.models import Question, Answer, Message

class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "active", "created_date")
    list_filter = ("created_date", )
    search_fields = ("content", )
    inlines = [AnswerInline]

class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "body", "created_date")
    search_fields = ("subject", "body")

admin.site.register(Question, QuestionAdmin)
admin.site.register(Message, MessageAdmin)