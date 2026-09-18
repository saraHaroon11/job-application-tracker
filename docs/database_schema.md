Database Schema

Database Schema
This document describes the database design for the Job Application Tracking System: five models, their fields, and the relationships between them.
Overview of Relationships
Every Company, Job Application, Interview, and Application Note belongs to a specific User, either directly or through a chain of relationships, ensuring each user's data remains fully separate from every other user's. Skill is the one model that is shared across all users rather than being tied to a specific one.
At a high level: a User has many Companies. A Company has many Job Applications. A Job Application has many Interviews and many Application Notes. A Job Application is also linked to many Skills, and a Skill can belong to many Job Applications, forming a many-to-many relationship.
User (built into Django)
Django's built-in User model is used for authentication and is not custom-built for this project. It stores username, password (hashed), and email, and every other model in the system ties back to a User, either directly or indirectly.
 
 
 Company
Fields: user, name, website, industry, location, and created_at.
Relationship: each Company belongs to exactly one User. One User can have many Companies. A Company can have many Job Applications associated with it.

Job Application
Fields: user, company, job_title, job_url, location, salary_min, salary_max, skills (a many-to-many relationship to Skill), application_date, status, notes, created_at, and updated_at.
Relationship: each Job Application belongs to exactly one User and references exactly one Company. A Job Application can have many Interviews and many Application Notes associated with it, and can be linked to many Skills.
The status field uses a fixed set of choices: Saved, Applied, Screening, Interview, Offer, Rejected, and Withdrawn.
Two database indexes are defined on this model to support the application's most common query patterns: one combining user and status, and one combining user and application_date, along with a third combining company and application_date.


Interview
Fields: application (a foreign key to Job Application), interview_type, interview_date, interviewer, status, notes, created_at, and updated_at.
Relationship: each Interview belongs to exactly one Job Application. A Job Application can have many Interviews. Ownership by a specific User is determined indirectly, through the Interview's parent Job Application.
The interview_type field uses a fixed set of choices: Recruiter Screen, Technical Interview, Manager Interview, and Final Interview. The status field uses its own separate set of choices: Scheduled, Completed, Cancelled, and Rescheduled.
 
 
 Application Note
Fields: application (a foreign key to Job Application), content, created_at, and updated_at.
Relationship: each Application Note belongs to exactly one Job Application. A Job Application can have many Application Notes. As with Interview, ownership by a specific User is determined indirectly through the parent Job Application.


Skill
Fields: name.
Relationship: Skill is the only model not tied to a specific User. A Skill can be associated with many Job Applications, and a Job Application can be associated with many Skills, forming a many-to-many relationship. This design allows the same skill, such as Python or SQL, to be shared and reused across every user's applications, rather than each user needing to recreate their own separate copy of common skills.


Why This Design Was Chosen Structuring the data this way keeps a clear, simple hierarchy: User owns Company, Company owns Job Application, and Job Application owns both Interview and Application Note. Every view in the application enforces this hierarchy by filtering data based on the logged-in user, either directly through a user field, or indirectly by checking the user of a related Job Application. This design directly supports the project's core requirement that one user must never be able to view or modify another user's data, even by manually changing a URL.
Skill was deliberately kept separate from this per-user hierarchy, since technologies and roles are naturally shared concepts rather than private data, and reusing the same Skill entries across users avoids duplicate, inconsistent data such as multiple separate entries for "Python" and "python."

