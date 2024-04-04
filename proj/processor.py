from proj.models import GoogleAuth, Student


def google_account_connected(request):
    user = request.user
    if user.is_authenticated and not user.is_staff and not user.is_superuser:
        print("Authenticated user")
        student = Student.objects.get(user__username=user.username) 
        res = bool(student.gauth)
    else:
        print("Anonymous user")
        res = False
    return {"google_account_connected" :  res }

def get_announcements(request):
    user = request.user
    if user.is_authenticated and not user.is_staff and not user.is_superuser:
        print("Authenticated user")
        res = user.announcements.all()
    else:
        print("Anonymous user")
        res = []
    return {"announcements" :  res }

