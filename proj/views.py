from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from proj.models import Student, Branch, Task, GoogleAuth
from proj.forms import UserForm, StudentForm, TaskForm

from datetime import datetime, timedelta, timezone
import heapq

from scheduler.tasks import LinearDrop
from scheduler.algorithms import branch_bound_priority

from proj.tasks import notify
from webpush import send_user_notification

from proj.google_auth import *



def create_schedule(username):
    student = Student.objects.get(user__username=username) #fetch all student tasks
    tasks = student.tasks.filter(status=False) #uncompleted tasks
    tasks =  list(filter(lambda task : task.active, tasks)) #filter active tasks out of uncompleted tasks
    print(tasks)
    
    _tasks = [
        LinearDrop(
            duration=task.rel_duration, 
            t_release=task.rel_t_release if(task.schedule_after > datetime.now(timezone.utc)) else 0, 
            t_drop=task.rel_deadline, 
            l_drop=task.loss, 
            slope=task.priority
        )
        for task in tasks
    ]
    
    sol = branch_bound_priority(_tasks, [0.0])
    sch = sol["t"]
    print(sch)

    for i, task in enumerate(tasks):
        td = timedelta(minutes=sch[i])
        sched = datetime.now(timezone.utc) + td
        task.scheduled_at = sched
        task.save()

    if(student.gauth):
        gauth = student.gauth
        chk = True
        access_token = gauth.access_token
        refresh_token = gauth.refresh_token
        if gauth.expired:
            chk, access_token = refresh_access_token(refresh_token)
            gauth.access_token = access_token
            gauth.save()

        if(chk):
            print("Valid Credentials")
            creds = create_creds(access_token, refresh_token)
            batchPush(creds, tasks)

        else:
            print("User revoked the access to calender")
            gauth.delete()

    return tasks


@login_required
def home(request):
    if request.method == "POST":
        print("post update sched")
        tasks = create_schedule(request.user.username)
        tasks.sort(key= lambda task : task.scheduled_at)
        return render(request, "pages/home.html", {"tasks" : tasks})
    
    student = Student.objects.get(user=request.user) #fetch all student tasks
    tasks = student.tasks.filter(status=False) #uncompleted tasks
    tasks =  list(filter(lambda task : task.active, tasks)) #filter active tasks out of uncompleted tasks
    tasks.sort(key= lambda task : task.scheduled_at)

    return render(request, "pages/home.html", {"tasks" : tasks})

@login_required
def managetasks(request):
    student = Student.objects.get(user=request.user)
    tasks = student.tasks.all()
    return render(request, "pages/managetasks.html", {"tasks" : tasks})

@login_required
def rescheduletasks(request):
    student = Student.objects.get(user=request.user) #fetch all student tasks
    tasks = student.tasks.filter(status=False, is_recurring=False) #uncompleted tasks
    tasks =  list(filter(lambda task : not task.active, tasks))
    return render(request, "pages/rescheduletasks.html", {"tasks": tasks})

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
            return render(request, "pages/login.html", {"message" : "Registered Successfully"})
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
                return render(request, "pages/login.html", {"message" : "User not Active"})
        else:
            print("someone tried to login and failed")
            return render(request, "pages/login.html", {"message" : "Invalid login details supplied"})
        
    return render(request, "pages/login.html")


@login_required
def logout_user(request):
    logout(request)
    return render(request, "pages/login.html", {"message" : "User logged out successful"})

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
    student = Student.objects.get(user=request.user)
    task = Task.objects.get(id=pk)

    if( student.gauth and task.event_id):
        gauth = student.gauth
        access_token = gauth.access_token
        refresh_token = gauth.refresh_token
        chk = True

        if gauth.expired:
            chk, access_token = refresh_access_token(refresh_token)
            gauth.access_token = access_token
            gauth.save()

        if(chk):
            print("Valid Credentials")
            creds = create_creds(access_token, refresh_token)
            delete_event(creds, task.event_id)

        else:
            print("User revoked the access to calender")
            gauth.delete()

    task.delete()
    create_schedule(request.user.username)
    return HttpResponseRedirect("/managetasks")

@login_required
def mark_done(request, pk):
    task = Task.objects.get(id=pk)
    task.status = True
    task.save()
    create_schedule(request.user.username)
    return HttpResponseRedirect("/managetasks")

@login_required
def mark_undone(request, pk):
    task = Task.objects.get(id=pk)
    task.status = False
    task.save()
    create_schedule(request.user.username)
    return HttpResponseRedirect("/managetasks")


@login_required
def google_auth(request):
    student = Student.objects.get(user=request.user) 
    if request.method == "POST":
        return HttpResponse("Post method Not allowed for Google Auth !")
    
    if(request.GET.get("error")):
        return HttpResponse("Please give the necesarry permission for the Application to work")
    
    code = request.GET["code"]
    scope = request.GET["scope"]
    
    tokens = get_tokens(code)
    print(tokens)
    oauth = GoogleAuth(
        access_token = tokens["access_token"],
        refresh_token = tokens["refresh_token"],
        scope = tokens["scope"],
    )
    oauth.save()
    student.gauth = oauth
    student.save()
    print(code, scope)
    return HttpResponseRedirect("/")


def privacy(request):
    return render(request, "privacy-policy.html")

def terms(request):
    return render(request, "terms-of-service.html")