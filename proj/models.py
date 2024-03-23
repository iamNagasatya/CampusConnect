from django.db import models
from django.contrib.auth.models import User

from datetime import datetime, timedelta, timezone
# Create your models here.

class Branch(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.code} {self.name}"

class GoogleAuth(models.Model):
    access_token = models.TextField()
    refresh_token = models.TextField()
    scope = models.TextField()
    date_inserted    = models.DateTimeField(auto_now_add=True)
    date_last_update = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.who.user.username}"
    
    @property
    def expired(self):
        td = datetime.now(timezone.utc) - self.date_last_update
        return td > timedelta(minutes=58)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    SECTION_CHOICES = (("A", "Section A"), ("B", "Section B"), ("C", "Section C"), ("D", "Section D") )
    section = models.CharField(
        max_length=1,
        choices=SECTION_CHOICES,
        default="A",
    )
    year_of_joining = models.CharField(max_length=4)
    gauth = models.OneToOneField(GoogleAuth, on_delete=models.SET_NULL, related_name="who", null=True, blank=True)


    def __str__(self):
        return f"{self.user.username} {self.branch.name}"



class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    MANAGERMENT_CHOICES = (("S", "Section Level"), ("B", "Branch Level"), ("C", "College Level"))
    section = models.CharField(
        max_length=1,
        choices=MANAGERMENT_CHOICES,
        default="S",
    )

    def __str__(self):
        return f"{self.user.username} {self.user.get_full_name()}"



def get_now():
    return (datetime.now(timezone.utc)).replace(second=0, microsecond=0)

def get_now_with_hour():
    return (datetime.now(timezone.utc)+timedelta(hours=1)).replace(second=0, microsecond=0)


class Task(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    schedule_after = models.DateTimeField(default= get_now)
    deadline = models.DateTimeField(default= get_now_with_hour)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(default="01:00:00")
    is_important = models.BooleanField(default=False)
    is_fixed = models.BooleanField(default=False)
    has_intrest = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    created_by = models.ManyToManyField(Student, related_name="tasks")
    event_id = models.CharField(max_length=200, null=True, blank=True)

    @property
    def active(self):
        rem = self.deadline - datetime.now(timezone.utc)
        return rem.seconds > 0


    @property
    def rel_deadline(self):
        return self.deadline.hour * 60 + self.deadline.minute
    
    @property
    def rel_t_release(self):
        return self.schedule_after.hour * 60 + self.schedule_after.minute

    @property
    def rel_duration(self):
        return self.duration/timedelta(seconds=60)
    
    @property
    def priority(self):
        p = 2*self.is_important+1*self.has_intrest + 1
        if self.is_fixed:
            p+0.5
        return p
    
    @property
    def loss(self):
        return self.priority * 1500
    
    def __str__(self):
        return f"{self.name} deadline: {self.rel_deadline:.2f} t_release: {self.rel_t_release:.2f} duration: {self.rel_duration:.2f}"


    
class Announcement(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    scheduled = models.DateTimeField(null=True, blank=True)
    users = models.ManyToManyField(User, related_name="announcements")
    