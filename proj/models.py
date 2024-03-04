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


class Task(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    deadline = models.DateTimeField()
    scheduled_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField()
    is_important = models.BooleanField(default=False)
    is_fixed = models.BooleanField(default=False)
    has_intrest = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    created_by = models.ManyToManyField(Student, related_name="tasks")

    @property
    def rel_deadline(self):
        return (self.deadline - datetime.now(timezone.utc)).total_seconds()

    @property
    def rel_duration(self):
        
        return self.duration.total_seconds()
    
    @property
    def priority(self):
        return 2*self.is_important+1*self.has_intrest + 1
    
    @property
    def loss(self):
        return (2*self.is_important+1*self.has_intrest + 1)*1000000
    
    def __str__(self):
        return f"{self.name} {self.deadline}"


    