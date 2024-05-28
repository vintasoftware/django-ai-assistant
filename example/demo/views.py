from django.shortcuts import render


def index(request):
    return render(request, "demo/index.html")


def htmx_chat(request):
    return render(request, "demo/htmx_chat.html")
