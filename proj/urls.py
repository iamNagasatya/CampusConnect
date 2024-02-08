from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("addtask", views.addtask, name="addtask"),
    path("managetasks", views.managetasks, name="managetasks"),
    path("rescheduletasks", views.rescheduletasks, name="rescheduletasks"),
    path("register", views.register, name="register"),
    path("profile", views.profile, name="profile"),
    path("login", views.login_user, name="login"),
    path("logout", views.logout_user, name="logout"),
]