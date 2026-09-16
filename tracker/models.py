

# Create your models here.
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class Company(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="companies"
    )
    name = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_company_per_user"
            )
        ]
        indexes = [
            models.Index(fields=["user", "name"]),
        ]

    def __str__(self):
        return self.name


class Skill(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="skills"
    )
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_skill_per_user"
            )
        ]

    def __str__(self):
        return self.name


class JobApplication(models.Model):

    class Status(models.TextChoices):
        SAVED = "Saved", "Saved"
        APPLIED = "Applied", "Applied"
        SCREENING = "Screening", "Screening"
        INTERVIEW = "Interview", "Interview"
        OFFER = "Offer", "Offer"
        REJECTED = "Rejected", "Rejected"
        WITHDRAWN = "Withdrawn", "Withdrawn"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_applications"
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="applications"
    )

    job_title = models.CharField(max_length=200)
    job_url = models.URLField(blank=True)
    location = models.CharField(max_length=200, blank=True)

    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name="applications"
    )

    application_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SAVED
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-application_date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "application_date"]),
            models.Index(fields=["company", "application_date"]),
        ]

    def clean(self):
     if (
        self.salary_min is not None
        and self.salary_max is not None
        and self.salary_min > self.salary_max
    ):
        raise ValidationError(
            "Minimum salary cannot be greater than maximum salary."
        )

    def __str__(self):
        return f"{self.job_title} - {self.company.name}"


class Interview(models.Model):

    class InterviewType(models.TextChoices):
        RECRUITER = "Recruiter Screen", "Recruiter Screen"
        TECHNICAL = "Technical Interview", "Technical Interview"
        MANAGER = "Manager Interview", "Manager Interview"
        FINAL = "Final Interview", "Final Interview"

    class Status(models.TextChoices):
        SCHEDULED = "Scheduled", "Scheduled"
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"
        RESCHEDULED = "Rescheduled", "Rescheduled"

    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="interviews"
    )

    interview_type = models.CharField(
        max_length=30,
        choices=InterviewType.choices
    )

    interview_date = models.DateTimeField()

    interviewer = models.CharField(
        max_length=200,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["interview_date"]

    def __str__(self):
        return f"{self.interview_type} - {self.application.job_title}"


class ApplicationNote(models.Model):
    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="application_notes"
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note - {self.application.job_title}"

