# weekly_planner details
import frappe
import datetime

no_cache = 1

def get_context(context):
    context.banner_image = frappe.db.get_single_value("Website Settings", "banner_image")
    context.title = frappe.db.get_single_value("Weekly Planner Settings", "title")
    context.show_age = frappe.db.get_single_value("Weekly Planner Settings", "show_student_age_in_view")

    # Make sure user has the correct role
    context.invalid_role = True
    cur_user = frappe.get_user()
    cur_roles = cur_user.get_roles()
    context.is_hos = "Head of School" in cur_roles
    context.is_head = "Head Instructor" in cur_roles
    context.is_instructor = "Instructor" in cur_roles
    context.invalid_role = not (context.is_head or context.is_instructor or context.is_hos)

    # Get planner_name from url parameter
    planner_name = frappe.form_dict.get("planner-name")
    context.planner = frappe.get_doc("Weekly Planner", planner_name)
    context.is_approved = context.planner.is_approved

    # Concatenate planner.start_date with start_date + 7 days
    context.start_date = context.planner.start_date.strftime("%m/%d/%Y")
    context.end_date = (context.planner.start_date + datetime.timedelta(days=7)).strftime("%m/%d/%Y")
    
    # Remove %20 from planner_name
    if planner_name:    
        planner_name = planner_name.replace("%20", " ")

    context.empty_planner = len(frappe.get_all("Planner Student", filters={"parent": planner_name}, fields=["name"])) + \
        len(frappe.get_all("Planner Topic", filters={"parent": planner_name}, fields=["name"]))

    print(context.empty_planner)

    return context
