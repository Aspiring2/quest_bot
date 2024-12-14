from django.urls import path
from django.http import HttpResponse

# Временное представление для тестирования
def index(request):
    return HttpResponse("Hello, this is the bot app!")

urlpatterns = [
    path('', index, name='bot_index'),
]
