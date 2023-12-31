# weekly_planner
import frappe
import datetime
import requests
from frappe import _
from weekly_planner.utils import get_root_url
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
    is_reviewer = "Planner Reviewer" in cur_roles
    context.invalid_role = True

    # Check if HoS has set the Show All flag
    try:
        context.hos_show_all = frappe.get_all("Employee", filters={"user_id": cur_user.name}, fields=["hos_show_all"])[0].hos_show_all
    except:
        context.hos_show_all = False

    planners = []

    # Retrieve Instructor from User
    # instructor = frappe.get_all("Instructor", fields=["name", "instructor_name", "user", "employee"], filters={"user": frappe.session.user})
    sql = '''SELECT i.name, instructor_name, e.user_id AS user, i.employee FROM `tabInstructor` i
        INNER JOIN tabEmployee e on i.employee = e.name
        WHERE e.user_id = %(user)s'''
    instructor = frappe.db.sql(sql, {"user": frappe.session.user}, as_dict=True)

    context.invalid_role = not (is_hos or is_head_instructor or is_instructor or is_reviewer) or (len(instructor) == 0)
    if context.invalid_role:
        return context

    # Load weekly planners (all for Head Instructor and System Manager, only for current instructor otherwise)
    elif is_head_instructor or is_hos or is_reviewer:
        # Load all instructors reporting to current user
        if instructor[0].employee:
            sql = '''SELECT p.name, p.instructor, campus, student_group, start_date, DATE_ADD(start_date, INTERVAL 7 DAY) AS end_date, 
                p.status, p.is_approved FROM `tabWeekly Planner` p
                INNER JOIN `tabInstructor` i ON p.instructor = i.name INNER JOIN `tabEmployee` e ON i.employee = e.name '''
            
            if (is_hos and context.hos_show_all) or is_reviewer:
                planners = frappe.db.sql(sql, as_dict=True)
            else:
                sql += '''WHERE e.reports_to = %(head)s OR p.instructor = %(instructor)s'''                
                planners = frappe.db.sql(sql, {"head": instructor[0].employee, "instructor": instructor[0].name}, as_dict=True)

            context.student_groups = frappe.get_all("Student Group Instructor", fields=["parent"])

            # print(planners)
        else:
            frappe.throw("There is no linked Employee record for this Instructor. Please contact your System Administrator.")
            context.invalid_role = True

    elif is_instructor:
        # Test to see if instructor exists and throw an error if not
        sql = '''SELECT p.name, p.instructor, campus, student_group, start_date, DATE_ADD(start_date, INTERVAL 7 DAY) AS end_date, 
                p.status, p.is_approved FROM `tabWeekly Planner`p
                INNER JOIN `tabInstructor` i ON p.instructor = i.name INNER JOIN `tabEmployee` e ON i.employee = e.name 
                WHERE p.instructor = %(instructor)s'''
        planners = frappe.db.sql(sql, {"instructor": instructor[0].name}, as_dict=True)
        
        context.student_groups = frappe.get_all("Student Group Instructor", fields=["parent"], filters={"instructor": instructor[0].name})
    
    # Add record counters to each planner
    counter = 0
    for planner in planners:
        counter += 1
        planner.counter = counter
    
    context.version = get_version()
    context.weekly_planners = planners
    context.instructor = instructor[0].instructor_name 
    context.is_head_instructor = is_head_instructor
    context.is_hos = is_hos
    context.is_reviewer = is_reviewer

    return context