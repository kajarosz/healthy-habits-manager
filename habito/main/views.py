from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from .forms import HabitForm
from .models import Habit

# Create your views here.

def home(request):
	return render(request, 'main/home.html', {})

def create_habit(request):
	if request.method == 'POST':
		user_id = request.POST.get('user_id')
		category = request.POST.get('category')
		interval = request.POST.get('interval')
		freq = request.POST.get('freq')
		if request.POST.get('remind-checkbox') == 'checked':
			remind = True
		else:
			remind = False
		habit = Habit(user_id=user_id, category=category, interval=interval, freq=freq, remind=remind)
		habit.save()
		return redirect(reverse('main:dashboard'))
	else:
		form = HabitForm
		return render(request, 'main/create_habit.html', {'form': form})

def dashboard(request):
	habits = request.user.habit.all()
	return render(request, 'main/dashboard.html', {'habits': habits})