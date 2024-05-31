from django.shortcuts import render


def react_index(request):
    return render(request, "demo/react_index.html")


def htmx_index(request, thread_id=None):
    return render(request, "demo/htmx_index.html")
