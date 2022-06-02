from hashlib import md5
from datetime import datetime, timedelta
from .exceptions import DatabaseQueryException
from .models import Action
import re

MD5_SECRET = 'healthy habits are awesome'

def hash_md5(password: str) -> str:
    result = md5(password.encode("utf-8"))
    result.update(MD5_SECRET.encode("utf-8"))
    return result.hexdigest()


regex_email = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

def is_email_valid(email):
    if re.fullmatch(regex_email, email):
      return True
    else:
      return False

regex_pass = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

def is_pass_valid(password):
    if re.fullmatch(regex_pass, password):
      return True
    else:
      return False

def current_dashboard(user):
  habits = user.habits
  daily_habits = []
  weekly_habits = []
  monthly_habits = []
  now = datetime.utcnow()
  day_from, day_to = day_interval(now)
  week_from, week_to = week_interval(now)
  month_from, month_to = month_interval(now)
  for habit in habits:
      habit_json = habit.json()
      actions = habit.actions
      if habit_json['recurrence'] == 'DAILY':
        habit_json = no_of_actions(habit_json, actions, day_from, day_to)
        daily_habits.append(habit_json)
      elif habit_json['recurrence'] == 'WEEKLY':
        habit_json = no_of_actions(habit_json, actions, week_from, week_to)
        weekly_habits.append(habit_json)
      elif habit_json['recurrence'] == 'MONTHLY':
        habit_json = no_of_actions(habit_json, actions, month_from, month_to)
        monthly_habits.append(habit_json)
  result = {'user': user.id,
    'daily_habits': daily_habits,
    'weekly_habits': weekly_habits,
    'monthly_habits': monthly_habits}
  return result

def no_of_actions(habit_json, actions, date_from, date_to):
  actions = list(filter(lambda Action: date_from <= Action.timestamp < date_to, actions))
  actions_no = len(actions)
  habit_json.update({'completed': actions_no})
  return habit_json

def actions_from_current_interval(user, habit):
  now = datetime.utcnow()
  habit_json = habit.json()
  if habit_json['recurrence'] == 'DAILY':
    date_from, date_to = day_interval(now)
  elif habit_json['recurrence'] == 'WEEKLY':
    date_from, date_to = week_interval(now)
  elif habit_json['recurrence'] == 'MONTHLY':
    date_from, date_to = month_interval(now)
  try:
    actions = Action.query.filter_by(user=user.id, habit=habit.id).order_by(Action.id.desc()).all()
    actions = list(filter(lambda Action: date_from < Action.timestamp < date_to, actions))
    if actions:
      last_action = actions[-1]
    else:
      last_action = None
  except:
      message = 'Error occured while filtering database.'
      raise DatabaseQueryException(message)
  return last_action

def day_interval(time):
  day_from = time.replace(hour=0, minute=0, second=0, microsecond=0)
  day_to = day_from + timedelta(hours=23, minutes=59, seconds=59)
  return day_from, day_to

def week_interval(time):
  weekday = time.weekday()
  week_from = time.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=weekday)
  week_to = week_from + timedelta(days=6)
  return week_from, week_to

def month_interval(timestamp):
  month_from = timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
  if timestamp.month in [1, 3, 5, 7, 8, 10, 12]:
      month_to = timestamp.replace(day=31, hour=0, minute=0, second=0, microsecond=0)
  elif timestamp.month in [2, 4, 6, 9, 11]:
      month_to = timestamp.replace(day=30, hour=0, minute=0, second=0, microsecond=0)
  else:
      if timestamp.year % 4 == 0:
          month_to = timestamp.replace(day=29, hour=0, minute=0, second=0, microsecond=0)
      else:
          month_to = timestamp.replace(day=28, hour=0, minute=0, second=0, microsecond=0)
  return month_from, month_to