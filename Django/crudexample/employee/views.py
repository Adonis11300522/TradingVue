from django.shortcuts import render

# Create your views here.
def show(request):  
    return HttpResponse("Http request is: "+request.method)  