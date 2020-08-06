from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.http import Http404, JsonResponse
from django.forms.utils import ErrorList
from halls.models import Hall, Video
from halls.forms import VideoForm, SearchForm
import urllib, requests
 

YOUTUBE_API_KEY = 'AIzaSyDgE_S8q_HG_Y747L9COW0JmNq3wVuQxXc'

# Create your views here.

def home(request):
    return render(request, 'home.html')

def dashboard(request):
    halls = Hall.objects.filter(user=request.user)
    return render(request, 'dashboard.html',{'halls':halls})

def add_video(request, pk):
    form = VideoForm()
    search_form = SearchForm()
    # restric Hall viewsing &/or editing to specific logged in user
    hall = Hall.objects.get(pk=pk)
    if not hall.user == request.user:
        raise Http404

    if request.method == 'POST':
        # Create video for specific Hall
        form = VideoForm(request.POST)
        if form.is_valid():
            video = Video()
            video.hall = hall
            video.url = form.cleaned_data['url']
            parsed_url = urllib.parse.urlparse(video.url)
            video_id = urllib.parse.parse_qs(parsed_url.query).get('v')
            if video_id:
                video.youtube_id =video_id[0]
                response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id[0]}&key={YOUTUBE_API_KEY}')
                json = response.json()
                title = json['items'][0]['snippet']['title']            
                video.title = title                    
                video.save()
                return redirect('detail_hall', pk)
            else:
                errors = form._errors.setdefault('url', ErrorList())
                errors.append('Needs to be a YouTube url')

    return render(request, 'add_video.html',{'form':form, 'search_form':search_form,'hall':hall})

def video_search(request):
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        encoded_search_term = urllib.parse.quote(search_form.cleaned_data['search_term'])
        response = request.GET(f'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=6&q={ encoded_search_term }&key={ YOUTUBE_API_KEY }')    
        return JsonResponse(response.json())
    return JsonResponse({'error':'Not able to validate form'})

class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'

    # Auto login user when they sign up
    def form_valid(self, form):
        view = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return view

# Class based views are good for CRUD while function based views are for more complex and/or custom views.
class CreateHall(generic.CreateView):
    model = Hall
    fields = ['title']
    template_name = 'create_hall.html'
    success_url = reverse_lazy('dashboard')

    # custom form validator with logged in user
    def form_valid(self, form):
        # get the user object. And adding a user into the form
        form.instance.user = self.request.user
        # super will validate all the info
        super(CreateHall, self).form_valid(form)
        # redirect user to page
        return redirect('home')

class DetailHall(generic.DetailView):
    model = Hall
    template_name = 'detail_hall.html'

class UpdateHall(generic.UpdateView):
    model = Hall
    template_name = 'update_hall.html'
    fields = ['title']
    success_url = reverse_lazy('dashboard')

class DeleteHall(generic.DeleteView):
    model = Hall
    template_name = 'delete_hall.html'
    success_url = reverse_lazy('dashboard')

