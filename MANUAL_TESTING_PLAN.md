# Mentor-Mentee Matchmaker - Manual Testing Plan

## Overview
This document provides step-by-step instructions for manually testing the Mentor-Mentee Matchmaker application. The test data includes 3 mentors and 4 mentees in one cohort.

## Test Environment
- URL: http://localhost:8000
- Database: PostgreSQL (Docker container)
- All services running via Docker Compose

## Test Users

### Admin User
- Username: admin
- Password: admin123
- Role: System Administrator

### Mentor Users
1. Username: mentor1
   - Password: test123
   - Name: Alice Johnson
   - Role: Mentor

2. Username: mentor2
   - Password: test123
   - Name: Bob Smith
   - Role: Mentor

3. Username: mentor3
   - Password: test123
   - Name: Carol Williams
   - Role: Mentor

### Mentee Users
1. Username: mentee1
   - Password: test123
   - Name: David Brown
   - Role: Mentee

2. Username: mentee2
   - Password: test123
   - Name: Emma Davis
   - Role: Mentee

3. Username: mentee3
   - Password: test123
   - Name: Frank Miller
   - Role: Mentee

4. Username: mentee4
   - Password: test123
   - Name: Grace Wilson
   - Role: Mentee

## Sample CSV Files
Sample CSV files are available in the app container at:
- `/app/sample_mentor_template.csv` - Mentor CSV template
- `/app/sample_mentors_fixed.csv` - Fixed sample mentor data with 5 entries (use this one for testing)
- `/app/sample_mentee_template.csv` - Mentee CSV template
- `/app/sample_mentees.csv` - Sample mentee data with 6 entries

Note: The users referenced in the CSV files have been pre-created in the system to ensure successful import.

## Improved Participant Experience

### Enhanced Preferences Interface
Participants can now see detailed profile information when ranking candidates:

1. **Mentors** see detailed information for each mentee:
   - Desired expertise areas
   - Preferred location
   - Preferred languages
   - Additional notes

2. **Mentees** see detailed information for each mentor:
   - Job title and function
   - Expertise tags
   - Languages spoken
   - Location
   - Years of experience
   - Coaching topics
   - Bio/description

3. **Improved Ranking Experience**:
   - Drag-and-drop interface with visual feedback
   - Detailed profile cards for informed decision-making
   - Ability to see blocked candidates (same organization)

## Improved Admin Experience

### Admin Dashboard Access
As admin user:
1. Navigate to http://localhost:8000/
2. You will be automatically redirected to the Admin Dashboard at http://localhost:8000/admin_views/dashboard/
3. The dashboard provides:
   - Quick access to all admin functions
   - List of all cohorts with participant counts
   - Direct links to cohort management actions

### Cohort Management (Admin)
From the Admin Dashboard:
1. View all cohorts in the system
2. See participant counts for each cohort (mentors and mentees)
3. Access cohort-specific actions:
   - Dashboard: View cohort readiness and diagnostics
   - Run Matching: Execute the matching algorithm
   - Edit: Modify cohort details in Django admin

### Creating New Cohorts
1. From Admin Dashboard, click "Django Admin" button
2. Navigate to CORE > Cohorts
3. Click "ADD COHORT" button
4. Fill in cohort details:
   - Name: Unique cohort name
   - Status: DRAFT/OPEN/CLOSED/MATCHED
   - Cohort config: JSON configuration for scoring (optional)
5. Save the cohort

### Adding Participants to Cohorts
Method 1 - Via Django Admin:
1. Navigate to Django Admin (http://localhost:8000/admin/)
2. Go to CORE > Participants
3. Click "ADD PARTICIPANT" button
4. Fill in participant details:
   - Select the cohort
   - Select the user (create new user if needed)
   - Set role (MENTOR/MENTEE)
   - Enter display name
   - Set organization
5. Save the participant

Method 2 - Bulk Import:
1. Use CSV import functionality for bulk mentor/mentee creation
2. See CSV Import section below

## Test Scenarios

### 1. Login Process
1. Navigate to http://localhost:8000
2. Click on "Login" button
3. Test with admin credentials:
   - Username: admin
   - Password: admin123
4. Verify automatic redirect to Admin Dashboard
5. Test with mentor credentials:
   - Username: mentor1
   - Password: test123
6. Test with mentee credentials:
   - Username: mentee1
   - Password: test123
7. Verify successful login redirects to appropriate pages
8. Verify logout functionality works

### 2. Participant Profile Management
As mentor1 (Alice Johnson):
1. Login and select cohort
2. Go to profile page to update basic information
3. Navigate to "Manage Preferences" to rank candidates
4. View detailed profile information for each candidate
5. Use drag-and-drop to rank candidates by preference
6. Save preferences and submit when ready

As mentee1 (David Brown):
1. Login and select cohort
2. Go to profile page to update basic information
3. Navigate to "Manage Preferences" to rank candidates
4. View detailed profile information for each candidate
5. Use drag-and-drop to rank candidates by preference
6. Save preferences and submit when ready

### 3. Admin Dashboard Navigation
After logging in as admin:
1. Verify automatic redirect to Admin Dashboard (http://localhost:8000/admin_views/dashboard/)
2. Check quick action buttons:
   - Import Mentors
   - Download CSV Template
   - Django Admin
3. Verify cohort list shows:
   - "Engineering Mentoring Program 2026"
   - Status: OPEN
   - 8 mentors, 4 mentees
4. Test cohort action buttons:
   - Dashboard link
   - Run Matching link
   - Edit link (Django Admin)

### 4. Django Admin Interface
From Admin Dashboard:
1. Click "Django Admin" button
2. Login with admin credentials if prompted
3. Verify access to all models:
   - Cohorts
   - Participants
   - Users
   - Mentor Profiles
   - Mentee Profiles
   - Import Jobs
   - Preferences
   - Match Runs
   - Matches
   - Pair Scores
   - Active Match Runs

### 5. Mentor Functionality
Login as mentor1 (Alice Johnson):
1. Verify mentor dashboard is displayed
2. You should see "Engineering Mentoring Program 2026" cohort
3. Click on the cohort to view profile
4. Check mentor profile information:
   - Display name: Alice Johnson
   - Organization: TechCorp
   - Role: Mentor
5. Navigate to Preferences section
6. Verify you can see detailed mentee profiles with:
   - Desired expertise
   - Preferred location
   - Preferred languages
7. Try ranking mentees using drag-and-drop
8. Submit preferences

### 6. Mentee Functionality
Login as mentee1 (David Brown):
1. Verify mentee dashboard is displayed
2. You should see "Engineering Mentoring Program 2026" cohort
3. Click on the cohort to view profile
4. Check mentee profile information:
   - Display name: David Brown
   - Organization: TechCorp
   - Role: Mentee
5. Navigate to Preferences section
6. Verify you can see detailed mentor profiles with:
   - Job title and function
   - Expertise tags
   - Location
   - Years of experience
   - Coaching topics
   - Bio
7. Try ranking mentors using drag-and-drop
8. Submit preferences

### 7. CSV Import Functionality (Admin)
As admin:
1. Navigate to Admin Dashboard
2. Click "Import Mentors" button or go to http://localhost:8000/import/mentor-csv/
3. Download the CSV template to understand required format:
   - Columns: mentor_email,organization,job_title,function,expertise_tags,languages,location,years_experience,coaching_topics,bio
4. Try importing the fixed sample mentor CSV file (`/app/sample_mentors_fixed.csv` in container):
   - Contains 5 sample mentors with realistic data
   - Each with different expertise, locations, and experience levels
   - All referenced users have been pre-created in the system
5. Alternatively, create your own CSV with this format:
   ```
   mentor_email,organization,job_title,function,expertise_tags,languages,location,years_experience,coaching_topics,bio
   john.doe@example.com,TechCorp,Senior Developer,Engineering,"python,js,react","english",San Francisco,5,"career guidance,technical leadership",Experienced developer
   ```
6. Verify import jobs are tracked in Admin panel under "Import Jobs"
7. Check for import errors or warnings in the import job details

For mentee imports:
1. Look for mentee import functionality (may be part of admin views)
2. Use the mentee template (`/app/sample_mentee_template.csv`)
3. Try importing the sample mentee CSV file (`/app/sample_mentees.csv`):
   - Contains 6 sample mentees with different preferences
   - Each with preferred expertise, locations, and languages

### 8. Cohort Dashboard & Readiness (Admin)
As admin:
1. From Admin Dashboard, click the "Dashboard" button for a cohort
2. Or navigate directly to: http://localhost:8000/admin_views/cohort/[cohort_id]/dashboard/
3. Check diagnostics report:
   - Participant counts
   - Submission status
   - Profile completeness
4. View top pair scores if preferences have been submitted

### 9. Matching Process (Admin)
As admin:
1. Ensure participants have submitted preferences (you may need to submit them manually for testing)
2. From Admin Dashboard, click the "Run Matching" button for a cohort
3. Or navigate directly to: http://localhost:8000/admin_views/cohort/[cohort_id]/run-matching/
4. Select matching mode (Strict or Exception)
5. Run matching
6. Verify:
   - Matches are generated
   - Match scores are calculated using both rankings and profile compatibility
   - Results are displayed

### 10. Match Results Review (Admin)
As admin:
1. After running matching, view match results
2. Check that:
   - All mentors have matches (except possibly some)
   - Match scores are displayed
   - Pairings make sense based on expertise/preferences
3. Test override functionality:
   - Manually change a match
   - Add override reason
   - Verify override is flagged
4. Export matches to Excel
5. Verify exported file contains all match data

### 11. Participant Match Viewing
After matching is complete:
1. Login as mentor1 (Alice Johnson)
2. Navigate to cohort
3. Look for "My Match" or similar functionality
4. Verify assigned mentee is displayed with match score
5. Login as mentee1 (David Brown)
6. Navigate to cohort
7. Verify assigned mentor is displayed with match score

## Expected Results
1. All users can log in successfully
2. Admin can manage all aspects of the system through improved dashboard
3. Participants can see detailed profile information when ranking candidates
4. CSV imports work correctly with proper validation
5. Matching algorithm produces reasonable pairings based on both rankings and profile compatibility
6. Match results can be reviewed, modified, and exported
7. All users can view their match information

## Troubleshooting
1. If login fails:
   - Verify Docker containers are running: `docker compose ps`
   - Check Django logs: `docker compose logs app`
   - Reset passwords if needed

2. If database issues occur:
   - Restart containers: `docker compose down && docker compose up -d`
   - Re-run migrations if needed: `docker compose exec app python manage.py migrate`

3. If static files aren't loading:
   - Re-collect static files: `docker compose exec app python manage.py collectstatic --noinput`

## Data Reset (if needed)
To reset all data:
1. Stop containers: `docker compose down -v`
2. Start fresh: `docker compose up -d`
3. Run migrations: `docker compose exec app python manage.py migrate`
4. Create superuser: `docker compose exec app python manage.py createsuperuser --username admin --email admin@example.com --noinput`
5. Set password: `docker compose exec app python manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.get(username='admin'); u.set_password('admin123'); u.save()"`
6. Recreate test data: `docker compose exec app python create_test_data.py`