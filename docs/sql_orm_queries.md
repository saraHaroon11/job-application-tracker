SQL and Django ORM Assessment

This document lists five non-trivial ORM queries used in the Job Application Tracking System ,explains where each one is used and provides the raw SQL equivalent for two of them.
Query 1 : Applications Grouped by Status
Used in:
 dashboard_view, where it powers the "Applications by Status" chart on the dashboard.
ORM query:
 status_breakdown = JobApplication.objects.filter(user=user).values("status").annotate(count=Count("id")).order_by("status")
Raw SQL equivalent:
 SELECT status, COUNT(id) AS count FROM tracker_jobapplication WHERE user_id = %s GROUP BY status ORDER BY status;
Explanation:
 The values("status") call tells Django to group rows by the status column, and annotate(count=Count("id")) counts how many rows fall into each group. Together, this is Django's way of expressing SQL's GROUP BY combined with COUNT().

Query 2 : Applications with Company Info
Used in:
 application_list, where it prevents an N+1 query problem when displaying each application's company name.
ORM query:
 applications = JobApplication.objects.filter(user=request.user).select_related("company")
Conceptual SQL: select_related("company") causes Django to perform a SQL INNER JOIN against the tracker_company table within the same query, instead of issuing a separate query for each row to fetch its company.

Query 3 : Applications Submitted This Month
Used in:
 dashboard_view, where it powers the "This Month" stat card.
ORM query:
 applications_this_month = JobApplication.objects.filter(user=user, application_date__year=today.year, application_date__month=today.month).count()
Conceptual SQL: This filters rows where the year and month extracted from application_date match the current year and month, then counts the matching rows.

 Query 4 : Applications Per Month
Used in:
 dashboard_view, where it supports the "applications per month" analytic.
ORM query:
 monthly_breakdown = JobApplication.objects.filter(user=user).annotate(month=TruncMonth("application_date")).values("month").annotate(count=Count("id")).order_by("month")
Conceptual SQL: TruncMonth truncates each application_date down to the first day of its month, similar to using DATE_TRUNC in PostgreSQL, and the query then groups and counts rows by that truncated value.

Query 5 :  Application Success Analysis
Used in: 
success_analysis, where it powers the conversion-rate table.
ORM query:
 analysis = JobApplication.objects.filter(user=user).values("job_title").annotate(total_applications=Count("id", distinct=True), total_interviewed=Count("interviews", filter=Q(interviews__isnull=False), distinct=True), total_offers=Count("id", filter=Q(status=JobApplication.Status.OFFER), distinct=True)).order_by("-total_applications")
Raw SQL equivalent:
 SELECT ja.job_title, COUNT(DISTINCT ja.id) AS total_applications, COUNT(DISTINCT iv.id) AS total_interviewed, COUNT(DISTINCT CASE WHEN ja.status = 'Offer' THEN ja.id END) AS total_offers FROM tracker_jobapplication ja LEFT JOIN tracker_interview iv ON iv.application_id = ja.id WHERE ja.user_id = %s GROUP BY ja.job_title ORDER BY total_applications DESC;
Explanation: 
This groups all of a user's applications by job title, then counts three things per group in a single query: the total number of applications, how many distinct applications had at least one linked interview (via a LEFT JOIN to the Interview table), and how many ended with an Offer status (using a conditional CASE WHEN). The conversion percentages , Application to Interview, Interview to Offer, and Application to Offer , are then calculated afterward in Python from these three counts since simple division reads more clearly there than nested inside the query itself.
