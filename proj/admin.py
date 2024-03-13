from django.contrib import admin
from proj.models import Student, Branch, Manager, Task, GoogleAuth
# Register your models here.


admin.site.register(Student)
admin.site.register(Branch)
admin.site.register(Manager)
admin.site.register(Task)
admin.site.register(GoogleAuth)