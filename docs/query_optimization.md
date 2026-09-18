Query Optimization Report

Page investigated: 
The Job Applications list page (/applications/), which loads each application together with its related Company , exactly the kind of page this section asks to investigate, since it combines a user's data with a related model on every row.
Tool used: 
Django Debug Toolbar, which reports the exact number of SQL queries executed to render a page and lets each query be expanded to view its full SQL text.

Before Optimization

 (unoptimized):
 applications = JobApplication.objects.filter(user=request.user)
Result: 7 queries were required to render the page, with 2 applications shown on that page. The query breakdown from Debug Toolbar was:
 Query 1 : session lookup (Django framework housekeeping)
 Query 2 : logged-in user lookup (Django framework housekeeping)
 Query 3 : COUNT(*) query for pagination
 Query 4 : fetching companies to populate the filter dropdown
 Query 5 : the paginated applications list itself
 Query 6 : fetching the company for application row 1
 Query 7 : fetching the company for application row 2
Queries 6 and 7 are the problem:
 one extra query is run per row, just to fetch that row's company name. With only 2 rows on the page this added 2 extra queries; with 20 applications on a page, this same pattern would add 20 extra queries.
What Caused the Performance Issue?
This is the classic N+1 query problem. The initial query fetches N application rows but does not include their related company data. Then, for every single row, Django's template lazily triggers a brand-new query the moment the company name is accessed , one query to get the list, plus N more queries, one per row, to fetch each one's company. As the number of applications on a page grows, the number of queries grows right alongside it. A page with 50 applications would run roughly 50 additional queries just for company lookups alone.
The Fix :
applications = JobApplication.objects.filter(user=request.user).select_related("company")
select_related("company") tells Django to perform a SQL INNER JOIN against the tracker_company table in the same query that fetches the applications, since company is a ForeignKey — a "to-one" relationship. The company data arrives already attached to each application object, so displaying the company name in the template requires no additional database trip.

After Optimization :


Result: 5 queries  the same page, the same data displayed, but 2 fewer queries than before.
The key change is visible directly in the SQL. The separate application-list query and the two per-row company queries collapsed into a single query:
SELECT ... FROM tracker_jobapplication INNER JOIN tracker_company ON (tracker_jobapplication.company_id = tracker_company.id) WHERE tracker_jobapplication.user_id = 1 ORDER BY tracker_jobapplication.application_date DESC LIMIT 2

Why the Fix Improved Performance :
Fewer round trips to the database , each query carries fixed overhead such as connection handling and parsing, and going from 7 to 5 queries removes two of those round trips for this small page. The saving compounds further as more applications are shown per page or as more users use the app at once.
The query no longer scales with the number of rows , before the fix, doubling the number of applications shown per page would have doubled the number of company lookups too. After the fix, the query count stays constant no matter how many applications are on the page, because the join fetches everything in a single pass.
Same result, less work ,the page renders identically from the user's perspective. This is a backend efficiency gain with no visible or functional change, which is exactly what query optimization should achieve.

Additional Optimizations Already Applied Elsewhere :
The same select_related and prefetch_related pattern was also applied in two other places. The application_detail view uses select_related("company") for the ForeignKey, and prefetch_related on interviews, application notes, and skills for the reverse ForeignKey and many-to-many relationships, which would otherwise trigger their own N+1 problems when the detail page loops through each application's interviews and notes. The dashboard's upcoming interviews query also uses select_related("application"), since the template displays each interview's parent application title.

Suggested Database Indexes :
The JobApplication model already defines indexes on the fields most commonly searched and filtered in this application: a combined index on user and status, a combined index on user and application_date, and a combined index on company and application_date.
These directly support the application's most frequent query patterns. The user-and-status index supports the dashboard's status-breakdown stats and the status filter on the applications list. The user-and-application_date index supports sorting by newest or oldest, the "this month" stat, and date-range filtering. The company-and-application_date index supports the "top companies applied to" analytic and the company filter.
No further indexes were identified as necessary for the current query patterns, since the ForeignKey fields for user and company are automatically indexed by Django and the underlying database engine by default.
