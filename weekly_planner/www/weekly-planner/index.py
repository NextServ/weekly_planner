# weekly_planner
import frappe
import webbrowser

def get_context(context):
    context.title = "Weekly Planner"
    context.banner_image = frappe.db.get_single_value("Website Settings", "banner_image")

    # Make sure user has the correct role
    acceptable_roles = ["Instructor", "Head Instructor", "System Manager"]
    context.invalid_role = True
    cur_user = frappe.get_user()
    cur_roles = cur_user.get_roles()
    is_head_instructor = "Head Instructor" in cur_roles
    is_instructor = "Instructor" in cur_roles
    planners = []

    for role in cur_roles:
        if role in acceptable_roles:
            context.invalid_role = False
            break

    # Retrieve Instructor from User
    instructor = frappe.get_all("Instructor", fields=["name", "instructor_name", "user"], filters={"user": frappe.session.user})
    print(instructor)

    # Load weekly planners (all for Head Instructor and System Manager, only for current instructor otherwise)
    if is_head_instructor:
        planners = frappe.get_all("Weekly Planner", fields=["name", "instructor", "student_group", "start_date", "docstatus"])
    elif is_instructor:
        # Test to see if instructor exists and throw an error if not
        if len(instructor) == 0:        
            frappe.throw("No instructor record found for user {0}".format(frappe.session.user))
            context.invalid_role = True
        else:
            planners = frappe.get_all("Weekly Planner", filters={"instructor": instructor[0].instructor_name}, \
                fields=["name", "instructor", "student_group", "start_date", "docstatus"])
    
    # Add record counters to each planner
    if not context.invalid_role:
        counter = 0
        for planner in planners:
            counter += 1
            planner.counter = counter
        
        context.weekly_planners = planners
        context.student_groups = frappe.get_all("Student Group", fields=["student_group_name"])
        context.instructor = instructor[0].instructor_name if frappe.session.user != "Administrator" else "Administrator"
        context.is_head_instructor = is_head_instructor

    return context
