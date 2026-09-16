README
Job Application Tracking System

A personal Job Application Tracker built with Django, allowing users to manage their own companies, job applications, interviews, and notes ; with search, filtering, sorting, pagination, a dashboard with analytics, and JavaScript-powered interactions.
Features :
1. User registration, login, and logout, with each user's data fully isolated from other users. 2. Company management with create, edit, and delete functionality. 3. Job application management including create, view, edit, delete, and status changes.          4. Interview tracking linked to individual job applications. 5. Notes linked to individual job applications. 6. Search by job title, company, or skill, with filtering by status, company, and date range, sorting by newest, oldest, or company name, and pagination on the results. 7. A dashboard with key stats, a status-breakdown chart built with Chart.js, top companies, top skills, and upcoming interviews. 8. An Application Success Analysis feature that calculates conversion rates grouped by job title, covering Application to Interview, Interview to Offer, and Application to Offer. 9. Three JavaScript features:
 A delete confirmation modal,  AJAX-based status updates with no page reload, and Client-side form validation.

Technology Stack

 1. Python and Django   2. SQLite as the default Django database
 3. the Django ORM       4. HTML        5. CSS          6. JavaScript 
 7.  Django Templates     8. Bootstrap 5.3 for styling    9. Chart.js for the dashboard chart 
10. Django Debug Toolbar, which was used during development for query optimization
11. Project Setup


Step 1  Clone the repository
 git clone (repository URL)
 cd job_application_tracker
Step 2  Create and activate a virtual environment
 python -m venv venv
 venv\Scripts\activate on Windows, or source venv/bin/activate on macOS and Linux
Step 3  Install dependencies
 pip install django django-debug-toolbar
Step 4  Apply migrations
 python manage.py migrate
Step 5  Create a superuser to access the admin panel
 python manage.py createsuperuser
Step 6  Run the development server
 python manage.py runserver
Step 7  Open the app
 Visit 127.0.0.1:8000/register/ to create an account, or 127.0.0.1:8000/admin/ to log in as the superuser and manage data directly.

 Sample Data
A small set of sample Companies, Skills, Job Applications, Interviews, and Notes was added through the Django admin panel to populate the dashboard, charts, and Application Success Analysis with realistic data. This data can be recreated by any user by registering an account and adding their own Companies, Skills, and Applications through the app itself, or by an administrator adding it through the admin panel.
 
Project Structure
The project root contains the jobtracker folder, holding the project-level settings and URL configuration, and the tracker folder, which is the main app containing models, views, forms, and templates. Templates are located under tracker/templates/tracker. A docs folder holds the project's written documentation, described below. The manage.py file sits at the project root.
 
 Documentation
The project includes three supporting documents as part of its deliverables. The SQL and ORM Queries document lists five non-trivial ORM queries used in the project, with raw SQL equivalents provided for two of them. The Query Optimization document describes an N and one query problem identified and fixed on the applications list page, including before and after query counts captured using Django Debug Toolbar. The Research Topic document is a written explanation of AJAX and Fetch with Django, the topic independently researched and implemented in this project.

Data Isolation and Security
Every view that reads or modifies a Company, Job Application, Interview, or Note filters by the logged-in user, either directly or, for models linked indirectly through a job application, by checking ownership through that relationship. This ensures one user cannot view or modify another user's data, including by manually changing a URL's ID parameter ; an invalid or mismatched ID returns a page-not-found response rather than exposing another user's data.

 Assumptions Made During Development
Skills are treated as a shared, application-wide list rather than being scoped to individual users, since they represent general technologies or roles rather than personal data. The count of "interviewed" applications in the Application Success Analysis reflects the number of distinct applications with at least one linked interview, not the total number of interview records, since a single application can have multiple interview rounds. The project uses SQLite, Django's default database, which is suitable for development and demonstration purposes.
