from django.db import models
from django.contrib.auth.models import User

from datetime import datetime, timedelta, timezone
# Create your models here.

class Branch(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.code} {self.name}"


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
    def rel_deadline(self):
        return max(0.0, (self.deadline - datetime.now(timezone.utc))/timedelta(seconds=60))
    

    @property
    def rel_duration(self):
        
        return self.duration/timedelta(seconds=60)
    
    @property
    def priority(self):
        return 2*self.is_important+1*self.has_intrest + 1
    
    @property
    def loss(self):
        return (2*self.is_important+1*self.has_intrest + 1)*1e6
    
    def __str__(self):
        return f"{self.id} {self.name}"

class GoogleAuth(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="gauth")
    access_token = models.TextField()
    refresh_token = models.TextField()
    scope = models.TextField()

    def __str__(self):
        return f"{self.user.username}"