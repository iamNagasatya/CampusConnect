from django.db import models
from django.contrib.auth.models import User

from recurrence.fields import RecurrenceField

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

# Create your models here.

IST = ZoneInfo("Asia/Kolkata")

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
    is_recurring = models.BooleanField(default=False)
    recurrence = RecurrenceField(include_dtstart=False, blank=True, null=True)
    
    @staticmethod
    def ist(dt):
        return dt.astimezone(tz=IST)
    
    @staticmethod
    def rel_minutes(dt):
        return (dt - datetime.now(timezone.utc))/timedelta(seconds=60)

    @property
    def rel_deadline(self):
        return self.rel_minutes(self.deadline)

    @property
    def rel_t_release(self):
        return self.rel_minutes(self.schedule_after)


    @property
    def active(self):
        now = datetime.now(timezone.utc)
        eroju = datetime.now(IST)
        ninna = eroju - timedelta(days=1)
        _deadline = self.ist(self.deadline)

        if self.is_recurring:
            next_rec_day = self.recurrence.after(ninna, dtstart=ninna)
            if next_rec_day and next_rec_day.date() == eroju.date():
                self.deadline = self.deadline.replace(year=now.year, month=now.month, day=now.day)
                self.schedule_after = self.schedule_after.replace(year=now.year, month=now.month, day=now.day)
                print("Active rec", self.name)
                self.save()
            else:
                return False
        res = now < self.deadline
        print("res", res)
        return res

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
    