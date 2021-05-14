from django.shortcuts import render

def home(request):
    return render(request, 'home.html',)

def about(request):
    return render(request, 'about.html',)

def statistics(request):
    return render(request, 'statistics.html',)

def map(request):
    return render(request, 'map.html',)

def mappage(request):
    return render(request, 'mappage.html',)