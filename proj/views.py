from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from proj.models import Student, Branch, Manager, Task, GoogleAuth
from proj.forms import UserForm, StudentForm, TaskForm

from datetime import datetime, timedelta, timezone
import heapq

from scheduler.tasks import LinearDrop
from scheduler.algorithms import branch_bound_priority

from proj.tasks import notify
from webpush import send_user_notification

from proj.google_auth import *



def get_tasks(username, active=True):
    student = Student.objects.get(user__username=username)
    tasks = student.tasks.filter(status=False)
    return [ task for task in tasks if(task.rel_deadline>0 if active else task.rel_deadline<0)]

def create_schedule(username):
    tasks = get_tasks(username)
    
    _tasks = [
        LinearDrop(
            duration=task.rel_duration, 
            t_release=task.rel_t_release, 
            t_drop=task.rel_deadline, 
            l_drop=task.loss, 
            slope=task.priority
        )
        for task in tasks
    ]
    sol = branch_bound_priority(_tasks, [0.0])
    print(sol)
    sch = sol["t"]
    print(sch)
    for i, task in enumerate(tasks):
        td = timedelta(minutes=sch[i])
        sched = datetime.now(timezone.utc) + td
        print(sched)
        task.scheduled_at = sched
        task.save()

    if( GoogleAuth.objects.filter(user__username=username)):
        gauth = GoogleAuth.objects.get(user__username=username)
        refresh_token = gauth.refresh_token
        chk, access_token = refresh_access_token(refresh_token)

        if(chk):
            print("Valid Credentials")
            creds = create_creds(access_token, refresh_token)
            batchPush(creds, tasks)
            
        else:
            print("User revoked the access to calender")
            gauth.delete()



@login_required
def home(request):
    student = Student.objects.get(user=request.user)
    tasks = student.tasks.filter(status=False)
    tasks = [ task for task in tasks if(task.rel_deadline>0)]
    tasks.sort(key= lambda task : task.scheduled_at)
    create_schedule(request.user.username)
    return render(request, "pages/home.html", {"tasks" : tasks})

@login_required
def managetasks(request):
    
    student = Student.objects.get(user=request.user)

    tasks = student.tasks.all()
    
    return render(request, "pages/managetasks.html", {"tasks" : tasks})

@login_required
def rescheduletasks(request):
    student = Student.objects.get(user=request.user)
    tasks = student.tasks.filter(status=False)

    _tasks = [ task for task in tasks if(task.rel_deadline<0) ]
    print(_tasks)
    return render(request, "pages/rescheduletasks.html", {"tasks": _tasks})

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



@login_required
def addtask(request):
    task_form = TaskForm()
    if request.method == 'POST':
        
        task_form_post = TaskForm(request.POST)
    
        task = task_form_post.save()
        student = Student.objects.get(user=request.user)

        task.created_by.add(student)
        task.save()
        create_schedule(request.user.username)

        # notify.apply_async(args=[request.user.username, task.name, task.description], eta=task.scheduled_at)
        return render(request, "pages/addtask.html", {
            "task_form" : task_form, 
            "success_msg" : f"Task added successfully"
        })
        
    return render(request, "pages/addtask.html", {"task_form": task_form})
    
@login_required
def update_task(request, pk):
    task = Task.objects.get(id=pk)
    task_form = TaskForm(instance=task)
    if request.method == 'POST':
        
        task_form = TaskForm(request.POST, instance=task)
        task = task_form.save()

        task.save()
        create_schedule(request.user.username)

        return render(request, "pages/addtask.html", {
            "task_form" : task_form, 
            "success_msg" : f"Updated successfully"
        })
        
    return render(request, "pages/addtask.html", {"task_form": task_form})
    
@login_required
def delete_task(request, pk):
    task = Task.objects.get(id=pk)

    if( GoogleAuth.objects.filter(user=request.user) and task.event_id):
        gauth = request.user.gauth
        refresh_token = gauth.refresh_token
        chk, access_token = refresh_access_token(refresh_token)

        if(chk):
            print("Valid Credentials")
            creds = create_creds(access_token, refresh_token)
            delete_event(creds, task.event_id)

        else:
            print("User revoked the access to calender")
            gauth.delete()

    task.delete()
    return HttpResponseRedirect("/managetasks")

@login_required
def mark_done(request, pk):
    task = Task.objects.get(id=pk)
    task.status = True
    task.save()
    return HttpResponseRedirect("/managetasks")

@login_required
def mark_undone(request, pk):
    task = Task.objects.get(id=pk)
    task.status = False
    task.save()
    return HttpResponseRedirect("/managetasks")


@login_required
def google_auth(request):
    if request.method == "POST":
        return HttpResponse("Post method Not allowed for Google Auth !")
    
    if(request.GET.get("error")):
        return HttpResponse("Please give the necesarry permission for the Application to work")
    
    code = request.GET["code"]
    scope = request.GET["scope"]
    
    tokens = get_tokens(code)
    print(tokens)
    oauth = GoogleAuth(
        user = request.user, 
        access_token = tokens["access_token"],
        refresh_token = tokens["refresh_token"],
        scope = tokens["scope"],
    )
    oauth.save()
    print(code, scope)
    return HttpResponseRedirect("/")