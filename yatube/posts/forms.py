from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('image', 'text', 'group')
        help_texts = {
            'group': 'Можете выбрать группу',
            'text': 'Здесь напишите свой текст', }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Напишите комментарий',
        }