# weekly_planner
import frappe
import webbrowser

def get_context(context):
    context.title = "Weekly Planner"
    context.banner_image = frappe.db.get_single_value("Website Settings", "banner_image")

    # Make sure user has the correct role
    context.invalid_role = True
    cur_user = frappe.get_user()
    cur_roles = cur_user.get_roles()
    is_head_instructor = "Head Instructor" in cur_roles
    is_instructor = "Instructor" in cur_roles

    planners = []

    # Retrieve Instructor from User
    instructor = frappe.get_all("Instructor", fields=["name", "instructor_name", "user", "employee"], filters={"user": frappe.session.user})

    context.invalid_role = not (is_head_instructor or is_instructor) or len(instructor) == 0

    # Load weekly planners (all for Head Instructor and System Manager, only for current instructor otherwise)
    if is_head_instructor:
        # Load all instructors reporting to current user
        if instructor[0].employee:
            sql = '''SELECT p.name, p.instructor, student_group, start_date, p.status, p.is_approved from `tabWeekly Planner` p
                INNER JOIN `tabInstructor` i ON p.instructor = i.name INNER JOIN `tabEmployee` e ON i.employee = e.name
                WHERE e.reports_to = %(head)s'''
            planners = frappe.db.sql(sql, {"head": instructor[0].employee}, as_dict=True)
            print(planners)
        else:
            frappe.throw("There is no linked Employee record for this Instructor. Please contact your System Administrator.")
            context.invalid_role = True

    elif is_instructor:
        # Test to see if instructor exists and throw an error if not
        if len(instructor) == 0:        
            frappe.throw("No instructor record found for user {0}".format(cur_user))
            context.invalid_role = True
        else:
            planners = frappe.get_all("Weekly Planner", filters={"instructor": instructor[0].instructor_name}, \
                fields=["name", "instructor", "student_group", "start_date", "status", "is_approved"])
    
    # Add record counters to each planner
    if not context.invalid_role:
        counter = 0
        for planner in planners:
            counter += 1
            planner.counter = counter
        
        context.weekly_planners = planners
        context.student_groups = frappe.get_all("Student Group", fields=["student_group_name"])
        context.instructor = instructor[0].instructor_name 
        context.is_head_instructor = is_head_instructor

    return context
