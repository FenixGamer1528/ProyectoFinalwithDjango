
from django.shortcuts import render,HttpResponse




#metodo home 
def home(request):
    return render(request, 'core/home.html')

def about(request):
    return render(request, 'core/about.html')

def portfolio(request):
    return HttpResponse(request,"core/portfolio.html")

def contact(request):
    return render(request, "core/contact.html")

def index(request):
    return render(request, "core/index.html")

# Create your views here.
