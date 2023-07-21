# weekly_planner details
import frappe

def get_context(context):
    context.banner_image = frappe.db.get_single_value("Website Settings", "banner_image")

    # Make sure user has the correct role
    acceptable_roles = ["Instructor", "Head Instructor", "System Manager"]
    context.invalid_role = True
    cur_user = frappe.get_user()
    cur_roles = cur_user.get_roles()

    for role in cur_roles:
        if role in acceptable_roles:
            context.invalid_role = False
            break

    # Get planner_name from url parameter
    planner_name = frappe.form_dict.get("planner-name")
    context.planner = frappe.get_doc("Weekly Planner", planner_name)
    
    # Remove %20 from planner_name
    if planner_name:    
        planner_name = planner_name.replace("%20", " ")

    context.empty_planner = len(frappe.get_all("Planner Student", filters={"parent": planner_name}, fields=["name"])) + \
        len(frappe.get_all("Planner Topic", filters={"parent": planner_name}, fields=["name"]))
    context.campuses = frappe.get_all("Campus", fields=["campus_name"])
    context.student_groups = frappe.get_all("Student Group", fields=["student_group_name"])

    print(context.empty_planner)

    return context
