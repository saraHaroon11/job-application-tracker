

# Register your models here.
from django.contrib import admin

from .models import (
    Company,
    Skill,
    JobApplication,
    Interview,
    ApplicationNote,
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "industry", "location", "created_at")
    search_fields = ("name", "industry", "location")
    list_filter = ("industry", "location")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    search_fields = ("name",)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "job_title",
        "company",
        "user",
        "status",
        "application_date",
        "created_at",
    )
    search_fields = (
        "job_title",
        "company__name",
        "location",
    )
    list_filter = (
        "status",
        "application_date",
    )
    filter_horizontal = ("skills",)


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = (
        "application",
        "interview_type",
        "interview_date",
        "interviewer",
        "status",
    )
    search_fields = (
        "application__job_title",
        "interviewer",
    )
    list_filter = (
        "interview_type",
        "status",
    )


@admin.register(ApplicationNote)
class ApplicationNoteAdmin(admin.ModelAdmin):
    list_display = (
        "application",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "application__job_title",
        "content",
    )