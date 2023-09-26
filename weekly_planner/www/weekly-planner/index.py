# weekly_planner
import frappe
import datetime
from frappe import _
from weekly_planner.__init__ import get_version

no_cache = 1

def get_context(context):
    context.title = _(frappe.db.get_single_value("Weekly Planner Settings", "title"))
    context.welcome_text = _(frappe.db.get_single_value("Weekly Planner Settings", "welcome_text"))
    context.banner_image = frappe.db.get_single_value("Website Settings", "banner_image")

    # Make sure user has the correct role
    cur_user = frappe.get_user()
    cur_roles = cur_user.get_roles()
    is_hos = "Head of School" in cur_roles
    is_head_instructor = "Head Instructor" in cur_roles
    is_instructor = "Instructor" in cur_roles

    # Retrieve Instructor from User
    # instructor = frappe.get_all("Instructor", fields=["name", "instructor_name", "user", "employee"], filters={"user": frappe.session.user})
    sql = '''SELECT i.name, instructor_name, e.user_id AS user, i.employee FROM `tabInstructor` i
        INNER JOIN tabEmployee e on i.employee = e.name
        WHERE e.user_id = %(user)s'''
    instructor = frappe.db.sql(sql, {"user": frappe.session.user}, as_dict=True)
    invalid_role = not (is_hos or is_head_instructor or is_instructor) or len(instructor) == 0

    context.invalid_role = invalid_role
    context.version = get_version()
    context.student_groups = frappe.get_all("Student Group", fields=["student_group_name"])
    context.instructor = instructor[0].instructor_name 
    context.is_head_instructor = is_head_instructor
    context.is_hos = is_hos

    return context