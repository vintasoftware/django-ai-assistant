from django.shortcuts import render


def react_index(request):
    return render(request, "demo/react_index.html")
