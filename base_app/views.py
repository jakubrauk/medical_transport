import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from base_app.forms import DispositorForm, ParamedicForm, CustomAuthenticationForm
from base_app.models import EmergencyAlert


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm


@login_required
def index(request):
    return render(request, 'base_app/index.html', {})


@login_required
def create_dispositor(request):
    form = None
    if request.method == 'GET':
        form = DispositorForm()

    elif request.method == 'POST':
        form = DispositorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('base_app:index')
    return render(request, 'base_app/create_dispositor.html', {'form': form})


@login_required
def create_paramedic(request):
    form = None
    if request.method == 'GET':
        form = ParamedicForm()

    elif request.method == 'POST':
        form = ParamedicForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('base_app:index')

    return render(request, 'base_app/create_paramedic.html', {'form': form})


@csrf_exempt
def create_emergency_alert_api(request):
    # later authorization with token
    # args:
    # startPositionLatitude
    # startPositionLongitude
    # endPositionLatitude (optional)
    # endPositionLongitude (optional)
    # priority - [1, 2, 3]
    # additionalInfo - Text
    print('EMERGENCY ALERT API')

    if request.method == 'POST':
        if EmergencyAlert.api_data_valid(request.POST):
            # save Emergency alert
            emergency_alert = EmergencyAlert.create_from_api(request.POST)
            context = {
                'valid': True,
                'method': request.method
            }

            return JsonResponse(context, status=200)
        else:
            return JsonResponse({'body': 'Data is not valid', 'valid': False}, status=400)
    else:
        return JsonResponse({'body': 'Request method must be POST', 'valid': False}, status=405)



