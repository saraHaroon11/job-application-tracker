from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import RegisterForm, CompanyForm, JobApplicationForm, InterviewForm, ApplicationNoteForm
from .models import Company, JobApplication, Interview, ApplicationNote, Skill


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "tracker/register.html", {"form": form})


@login_required
def dashboard_view(request):
    user = request.user
    today = timezone.now().date()

    applications = JobApplication.objects.filter(user=user)

    total_applications = applications.count()
    applications_this_month = applications.filter(
        application_date__year=today.year,
        application_date__month=today.month
    ).count()
    total_interviews = Interview.objects.filter(application__user=user).count()
    total_offers = applications.filter(status=JobApplication.Status.OFFER).count()
    total_rejections = applications.filter(status=JobApplication.Status.REJECTED).count()

    status_breakdown = applications.values("status").annotate(count=Count("id")).order_by("status")

    monthly_breakdown = (
        applications
        .annotate(month=TruncMonth("application_date"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    top_companies = (
        applications.values("company__name")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    top_skills = (
        Skill.objects.filter(applications__user=user)
        .annotate(count=Count("applications"))
        .order_by("-count")[:5]
    )

    upcoming_interviews = (
        Interview.objects.filter(application__user=user, interview_date__gte=timezone.now())
        .select_related("application")
        .order_by("interview_date")[:5]
    )

    chart_labels = [item["status"] for item in status_breakdown]
    chart_data = [item["count"] for item in status_breakdown]

    context = {
        "total_applications": total_applications,
        "applications_this_month": applications_this_month,
        "total_interviews": total_interviews,
        "total_offers": total_offers,
        "total_rejections": total_rejections,
        "status_breakdown": status_breakdown,
        "monthly_breakdown": monthly_breakdown,
        "top_companies": top_companies,
        "top_skills": top_skills,
        "upcoming_interviews": upcoming_interviews,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
    }
    return render(request, "tracker/dashboard.html", context)


@login_required
def company_list(request):
    companies = Company.objects.filter(user=request.user)
    return render(request, "tracker/company_list.html", {"companies": companies})


@login_required
def company_create(request):
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user
            company.save()
            return redirect("company_list")
    else:
        form = CompanyForm()
    return render(request, "tracker/company_form.html", {"form": form, "title": "Add Company"})


@login_required
def company_update(request, pk):
    company = get_object_or_404(Company, pk=pk, user=request.user)
    if request.method == "POST":
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect("company_list")
    else:
        form = CompanyForm(instance=company)
    return render(request, "tracker/company_form.html", {"form": form, "title": "Edit Company"})


@login_required
def company_delete(request, pk):
    company = get_object_or_404(Company, pk=pk, user=request.user)
    if request.method == "POST":
        company.delete()
        return redirect("company_list")
    return render(request, "tracker/company_confirm_delete.html", {"company": company})


@login_required
def application_list(request):
    # OPTIMIZED: select_related("company") performs a SQL JOIN so company
    # data is fetched in the same query as the applications, instead of
    # one extra query per row (N+1 problem). See query optimization docs.
    applications = JobApplication.objects.filter(user=request.user).select_related("company")

    search_query = request.GET.get("q", "").strip()
    if search_query:
        applications = applications.filter(
            Q(job_title__icontains=search_query) |
            Q(company__name__icontains=search_query) |
            Q(skills__name__icontains=search_query)
        ).distinct()

    status_filter = request.GET.get("status", "")
    if status_filter:
        applications = applications.filter(status=status_filter)

    company_filter = request.GET.get("company", "")
    if company_filter:
        applications = applications.filter(company__id=company_filter)

    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    if date_from:
        applications = applications.filter(application_date__gte=date_from)
    if date_to:
        applications = applications.filter(application_date__lte=date_to)

    sort_by = request.GET.get("sort", "newest")
    sort_map = {
        "newest": "-application_date",
        "oldest": "application_date",
        "company": "company__name",
    }
    applications = applications.order_by(sort_map.get(sort_by, "-application_date"))

    paginator = Paginator(applications, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "companies": Company.objects.filter(user=request.user),
        "search_query": search_query,
        "status_filter": status_filter,
        "company_filter": company_filter,
        "date_from": date_from,
        "date_to": date_to,
        "sort_by": sort_by,
        "status_choices": JobApplication.Status.choices,
    }
    return render(request, "tracker/application_list.html", context)


@login_required
def application_detail(request, pk):
    application = get_object_or_404(
        JobApplication.objects.select_related("company").prefetch_related(
            "interviews", "application_notes", "skills"
        ),
        pk=pk, user=request.user
    )
    context = {
        "application": application,
        "interview_form": InterviewForm(),
        "note_form": ApplicationNoteForm(),
    }
    return render(request, "tracker/application_detail.html", context)


@login_required
def application_create(request):
    if request.method == "POST":
        form = JobApplicationForm(request.POST, user=request.user)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            form.save_m2m()
            return redirect("application_list")
    else:
        form = JobApplicationForm(user=request.user)
    return render(request, "tracker/application_form.html", {"form": form, "title": "Add Job Application"})


@login_required
def application_update(request, pk):
    application = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == "POST":
        form = JobApplicationForm(request.POST, instance=application, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("application_detail", pk=application.pk)
    else:
        form = JobApplicationForm(instance=application, user=request.user)
    return render(request, "tracker/application_form.html", {"form": form, "title": "Edit Job Application"})


@login_required
def application_delete(request, pk):
    application = get_object_or_404(JobApplication, pk=pk, user=request.user)
    if request.method == "POST":
        application.delete()
        return redirect("application_list")
    return render(request, "tracker/application_confirm_delete.html", {"application": application})


@login_required
@require_POST
def update_status_ajax(request, pk):
    application = get_object_or_404(JobApplication, pk=pk, user=request.user)
    new_status = request.POST.get("status")

    valid_statuses = dict(JobApplication.Status.choices)
    if new_status not in valid_statuses:
        return JsonResponse({"success": False, "error": "Invalid status"}, status=400)

    application.status = new_status
    application.save()

    return JsonResponse({
        "success": True,
        "status": application.status,
        "status_label": valid_statuses[new_status],
    })


@login_required
def interview_create(request, app_pk):
    application = get_object_or_404(JobApplication, pk=app_pk, user=request.user)
    if request.method == "POST":
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.save()
    return redirect("application_detail", pk=application.pk)


@login_required
def interview_update(request, pk):
    interview = get_object_or_404(Interview, pk=pk, application__user=request.user)
    if request.method == "POST":
        form = InterviewForm(request.POST, instance=interview)
        if form.is_valid():
            form.save()
            return redirect("application_detail", pk=interview.application.pk)
    else:
        form = InterviewForm(instance=interview)
    return render(request, "tracker/interview_form.html", {"form": form, "application": interview.application})


@login_required
def interview_delete(request, pk):
    interview = get_object_or_404(Interview, pk=pk, application__user=request.user)
    app_pk = interview.application.pk
    if request.method == "POST":
        interview.delete()
        return redirect("application_detail", pk=app_pk)
    return render(request, "tracker/interview_confirm_delete.html", {"interview": interview})


@login_required
def note_create(request, app_pk):
    application = get_object_or_404(JobApplication, pk=app_pk, user=request.user)
    if request.method == "POST":
        form = ApplicationNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.application = application
            note.save()
    return redirect("application_detail", pk=application.pk)


@login_required
def note_delete(request, pk):
    note = get_object_or_404(ApplicationNote, pk=pk, application__user=request.user)
    app_pk = note.application.pk
    if request.method == "POST":
        note.delete()
        return redirect("application_detail", pk=app_pk)
    return render(request, "tracker/note_confirm_delete.html", {"note": note})


@login_required
def success_analysis(request):
    user = request.user

    analysis = (
        JobApplication.objects.filter(user=user)
        .values("job_title")
        .annotate(
            total_applications=Count("id", distinct=True),
            total_interviewed=Count("interviews", filter=Q(interviews__isnull=False), distinct=True),
            total_offers=Count("id", filter=Q(status=JobApplication.Status.OFFER), distinct=True),
        )
        .order_by("-total_applications")
    )

    results = []
    for row in analysis:
        total = row["total_applications"]
        interviewed = row["total_interviewed"]
        offers = row["total_offers"]

        app_to_interview = round((interviewed / total) * 100, 1) if total else 0
        interview_to_offer = round((offers / interviewed) * 100, 1) if interviewed else 0
        app_to_offer = round((offers / total) * 100, 1) if total else 0

        results.append({
            "job_title": row["job_title"],
            "total_applications": total,
            "total_interviewed": interviewed,
            "total_offers": offers,
            "app_to_interview": app_to_interview,
            "interview_to_offer": interview_to_offer,
            "app_to_offer": app_to_offer,
        })

    return render(request, "tracker/success_analysis.html", {"results": results})