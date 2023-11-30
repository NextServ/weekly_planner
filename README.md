## Weekly Planner

Weekly Planner for Monstessori Guides

### License

MIT

### Change Log

**0.5.0**
1. Duplicate Planner functionality now available (except the ability to include lessons)

2. Topics will still show in the Topics dialog even if they are not attached to a Course

3. Included a Help button and sidebar to show instructions on how to use the Planner Detail page

4. Fix bug on the Weekly Planner page where the planners of the head instructor are not showing

5. Fix bug where not all topics were showing in the Add Topics modal of Planner Detail

**0.5.5**
1. Displays Planner dates as a range of 7 days

**0.6.0**
1. Stores history of changes made to Planner Lessons

**0.6.5**
1. Deletes related history of changes if a lesson entry is deleted

**0.6.6**
1. Added the Head of School role that will show all planners regardless of the Reports To value

2. Added Help button to the Weekly Planner page

3. Added help content on both main and detail pages

**0.7.0**
1. Designate a Lesson Status as default

2. When adding a new Lesson, the default status will be selected

**0.7.1**
1. Disabled cache for the first page of the Weekly Planner

**0.7.2**
1. Disabled cache also for the planner detail page

**0.8.0**
1. Added the ability to print planner reports

**0.8.5**
1. Fixed bug where Head of School capabilities not showing up on main page

3. Fixed bug where the lesson entries are affecting other lesson entries

**0.8.7**
1. Fixed bug where New Planner button opened the wrong modal

2. Fixed the Approve Planner functionality when clicked from the Planner Detail page

**0.9.0**
1. Added Settings page

2. Change the format of the table in the Print Planner page so that now has borders

3. Added version number at the bottom left of the main page

4. Fixed the issue where students from DVO L1B aren't showing in the Show Students modal

**0.9.5**
1. Fixed the bug where the Approved Plan functionality is not working

2. Limit the students showing in the Show Students modal to only those that in the Instructor's Student Group

3. Show student names vertically in the Planner Report header

4. Allow Instructors to print the Planner Detail Report

**1.0.0**
1. Generate Student Lesson Report

2. Refactored diff_months()

3. Improved how the age appears on the Planner Detail page

**1.1.0**
1. Rewritten Planner Detail report that can be printed or saved as PDF properly

**1.1.1**
1. Fixed bug where the Planner Detail report is not opening in a new tab

**1.2.0**
1. Refactor the Planner Detail Report using frappe.local response instead of using PDFKit to generate the PDF

2. Refactor the Planner Detail Report so that it paginates properly

3. Added functionality to delete a Topic from the Planner Detail page

**1.3.0**
1. Add Campus columns in Main Table [Oct 11]; cannot add Program as Instructors can be assigned to multiple Programs

2. Head of School now has the option of only seeing planners of direct reports (default) or of all guides

3. Freeze the Topic column in the Planner Detail page

4. Freeze the entire header row in the Planner Detail page

5. Adding new lesson entries in the Planner Detail page no longer refreshes the whole page

**1.4.0**
1. Group Topics by Course in Planner Detail

2. Add another role like HoS but without Approval capabilities [Oct 13] - DONE (a)

3. If instructor/teacher of DVO L1C logs in, only DVO L1C student group appears and not all the student groups [Oct 18] - DONE (d)

4. Display Students in alphabetical order in Planner Detail - DONE (a)

**1.5.0 PLANNED**
1. Monthly Report [Oct 21] - DONE (g)

2. Color Codes [Oct 21] - DONE (a)

3. Added the Weekly Planning workspace - DONE (a)

4. Fixed the bug in Lesson Status where the default status is not being saved

5. Fixed the Weekly Planner Report so that it allows up to 35 students to be printed on a single page - DONE (c)

**1.5.1**
1. Allow end user to choose (and save) the paper size to use when printing the Weekly Planner Report

**1.5.2**
1. Restrict the Monthly Report list to only show assessments created by that guide and his/her supervisor. HoS can see all.

2. Fixed the following issues: ISS-2023-00063 and ISS-2023-00068

**1.5.3**
1. Fixed the following issues: ISS-2023-00067, ISS-2023-00069, ISS-2023-00070, and ISS-2023-00072

**1.5.4**

1. Allow end users to remove students from existing planners

2. Change the Show All icon on the Weekly Planner page

**1.5.5 PLANNED**
1. Fix bug where Planner Detail fails to display data if no color is assigned in Lesson Status