from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="tracker/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),

    path("companies/", views.company_list, name="company_list"),
    path("companies/add/", views.company_create, name="company_create"),
    path("companies/<int:pk>/edit/", views.company_update, name="company_update"),
    path("companies/<int:pk>/delete/", views.company_delete, name="company_delete"),

    path("applications/", views.application_list, name="application_list"),
    path("applications/add/", views.application_create, name="application_create"),
    path("applications/<int:pk>/", views.application_detail, name="application_detail"),
    path("applications/<int:pk>/edit/", views.application_update, name="application_update"),
    path("applications/<int:pk>/delete/", views.application_delete, name="application_delete"),

    path("applications/<int:app_pk>/interviews/add/", views.interview_create, name="interview_create"),
    path("interviews/<int:pk>/edit/", views.interview_update, name="interview_update"),
    path("interviews/<int:pk>/delete/", views.interview_delete, name="interview_delete"),

    path("applications/<int:app_pk>/notes/add/", views.note_create, name="note_create"),
    path("notes/<int:pk>/delete/", views.note_delete, name="note_delete"),
    path("analytics/", views.success_analysis, name="success_analysis"),
    path("applications/<int:pk>/update-status/", views.update_status_ajax, name="update_status_ajax"),

]