from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("addtask", views.addtask, name="addtask"),
    path("update_task/<str:pk>", views.update_task, name="update_task"),
    path("delete_task/<str:pk>", views.delete_task, name="delete_task"),
    path("mark_done/<str:pk>", views.mark_done, name="mark_done"),
    path("mark_undone/<str:pk>", views.mark_undone, name="mark_undone"),
    path("managetasks", views.managetasks, name="managetasks"),
    path("rescheduletasks", views.rescheduletasks, name="rescheduletasks"),
    path("register", views.register, name="register"),
    path("profile", views.profile, name="profile"),
    path("login", views.login_user, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("google_auth", views.google_auth, name="google_auth"),
]