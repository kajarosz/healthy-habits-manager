from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from .forms import HabitForm
from .models import Habit

# Create your views here.

def home(request):
	return render(request, 'main/home.html', {})

def create_habit(request, pk):
	if request.method == 'POST':
		form = HabitForm(request.POST or None)
		if form.is_valid():
			form.user_id = pk
			form.save()
			return redirect(reverse('main:home'))
	else:
		form = HabitForm
		return render(request, 'main/create_habit.html', {'form': form})