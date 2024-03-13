from proj.models import GoogleAuth


def google_account_connected(request):
    if request.user.is_authenticated:
        print("Authenticated user")
        res = bool(GoogleAuth.objects.filter(user=request.user))
    else:
        print("Anonymous user")
        res = False
    return {"google_account_connected" :  res }