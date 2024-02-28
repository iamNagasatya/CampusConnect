from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from proj.models import Student, Branch, Manager, Task
from proj.forms import UserForm, StudentForm, TaskForm

from datetime import datetime, timedelta
import heapq





@login_required
def home(request):
    return render(request, "pages/home.html")

@login_required
def managetasks(request):
    tasks = Task.objects.all()

    return render(request, "pages/managetasks.html", {"tasks" : tasks})

@login_required
def rescheduletasks(request):
    return render(request, "pages/rescheduletasks.html")

def register(request):
    if request.method == "POST":
        user_form = UserForm(request.POST)
        student_form = StudentForm(request.POST)

        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = student_form.save(commit=False)
            profile.user = user

            profile.save()
            return HttpResponseRedirect("/")
        else:
            print(user_form.errors, student_form.errors)
        
    else:
        user_form = UserForm()
        student_form = StudentForm()

    return render(request,
                  "pages/register.html", 
                  {
                      "user_form" : UserForm,
                      "student_form" : StudentForm()
                  }
            )

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect("/")
            else:
                return HttpResponse("User not Active")
        else:
            print("someone tried to login and failed")
            return HttpResponse("invalid login details supplied ")
        
    return render(request, "pages/login.html")


@login_required
def logout_user(request):
    logout(request)
    return HttpResponseRedirect("/login")

@login_required
def profile(request):
    student = Student.objects.get(user=request.user)
    return render(request, "pages/profile.html", {"student" : student})

# @login_required
# def addtask(request):
#     if request.method == 'POST':
#         taskname = request.POST["taskname"]
#         deadlinedate = request.POST["deadlinedate"]
#         deadlinetime = request.POST["deadlinetime"]
#         duration = request.POST["duration"]
#         isimportant = "isimportant" in request.POST
#         dt = datetime.strptime(f"{deadlinedate} {deadlinetime}", "%d/%m/%Y %I:%M %p")
#         hrs, mins = duration.split(":")
#         dur = timedelta(hours=int(hrs), minutes=int(mins))


#         if(dt<datetime.now()):
#             print("Dead")
#             return render(request, "base.html")
#         else:
#             print("Active")
#             job = Job(taskname, int(dur.total_seconds()), int(dt.timestamp()), isimportant)
#             jobs.append(job)
#             order, _ = plan()
#             return render(request, "base.html", {"plan" : order})
#     return render(request, "pages/addtask.html")

@login_required
def addtask(request):
    task_form = TaskForm()
    if request.method == 'POST':
        
        task_form = TaskForm(request.POST)
        print(task_form)
        task_form.save()

        return render(request, "pages/addtask.html", {
            "task_form" : task_form, 
            "success_msg" : f"Task added successfully"
        })
        
    return render(request, "pages/addtask.html", {"task_form": task_form})
    