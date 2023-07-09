# weekly_planner
import frappe
import webbrowser

def get_context(context):
    context.title = "Weekly Planner"
    context.banner_image = frappe.db.get_single_value("Website Settings", "banner_image")
    context.root_url = get_root_url()

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

    # Load weekly planners (all for Head Instructor and System Manager, only for current instructor otherwise)
    if is_head_instructor:
        planners = frappe.get_all("Weekly Planner", fields=["instructor", "student_group", "start_date", "docstatus"])
    elif is_instructor:
        # Retrieve Instructor from User
        instructor = frappe.get_all("Instructor", fields=["instructor_name", "user"], filters={"user": frappe.session.user})
        planners = frappe.get_all("Weekly Planner", filters={"instructor": instructor[0].instructor_name}, \
            fields=["instructor", "student_group", "start_date", "docstatus"])
    
    # Add record counters to each planner
    if not context.invalid_role:
        counter = 0
        for planner in planners:
            counter += 1
            planner.counter = counter
        
        context.weekly_planners = planners

    return context

def get_root_url():
    return frappe.utils.get_url()