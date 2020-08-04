from django import forms
from halls.models import Video

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['url']
        labels = {'url':'YouTube Url'}

class SearchForm(forms.Form):
    search_term = forms.CharField(max_length=256, label='Search for Videos:')
