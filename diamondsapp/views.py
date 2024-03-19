from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def home(request):
	template = loader.get_template('diamond/home.html')
	context = {}
	return HttpResponse(template.render(context, request))