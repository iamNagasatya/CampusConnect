from django.contrib import admin
from proj.models import Student, Branch, Task, GoogleAuth, Announcement

from proj.tasks import notify



class AnnouncementAdmin(admin.ModelAdmin):

    model = Announcement

    def save_related(self, request, form, formsets, change):

        super().save_related(request, form, formsets, change)
        announcement = form.instance
        for user in announcement.users.all():
            print("Announcements", user.username)
            notify.apply_async(args=[user.username, announcement.name, announcement.description], eta=announcement.scheduled)

        


admin.site.register(Announcement, AnnouncementAdmin)

admin.site.register(Student)
admin.site.register(Branch)
admin.site.register(Task)
admin.site.register(GoogleAuth)