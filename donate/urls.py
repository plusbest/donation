from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_user, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("register", views.register_user, name="register"),
    path("location", views.locate, name="location"),
    path("bag", views.new_bag, name="bag"),
    path("discover", views.discovery, name="discover"),
    path("settings", views.user_settings, name="settings"),
    path("ajax/bagload", views.ajax_bagload, name="ajax_bag_load"),
    path("ajax/donationspot", views.ajax_donationspot, name="ajax_donationspot"),
    path("ajax/bagrequest", views.ajax_bagrequest, name="ajax_bag_request"),
    path("ajax/modrequest", views.ajax_modrequest, name="ajax_mod_request"),
    path("ajax/notif", views.ajax_notifications, name="ajax_notif"),
    path("testform", views.test_form, name="testform"),
]