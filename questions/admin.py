from django.contrib import admin
from django import forms
from questions.models import Question


class QuestionsAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = ("",)
        fields = [
            "msg_id",
            "user",
            "text"
        ]
        widgets = {
            'text': forms.Textarea(attrs={'rows': 10, 'cols': 100})
        }


@admin.register(Question)
class QuestionsAdmin(admin.ModelAdmin):
    form = QuestionsAdminForm
    list_display = ['msg_id', 'user', 'text']
    search_fields = ('msg_id', 'text')
    list_display_links = ('msg_id', 'text',)