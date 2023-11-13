from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from base_app.forms import DispositorForm, ParamedicForm


@login_required
def index(request):
    return render(request, 'base_app/index.html', {})


@login_required
def create_dispositor(request):
    if request.method == 'GET':
        form = DispositorForm()
        return render(request, 'base_app/create_dispositor.html', {'form': form})

    elif request.method == 'POST':
        form = DispositorForm(request.POST)
        if form.is_valid():
            form.save()

    return redirect('base_app:index')


@login_required
def create_paramedic(request):
    if request.method == 'GET':
        form = ParamedicForm()
        return render(request, 'base_app/create_dispositor.html', {'form': form})

    elif request.method == 'POST':
        form = ParamedicForm(request.POST)
        if form.is_valid():
            form.save()

    return redirect('base_app:index')
