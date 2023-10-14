import frappe
from datetime import datetime


def after_install():
    pass


def after_sync():
    add_roles()
    add_settings()


def add_roles():
    if not frappe.db.exists("Role", "Head Instructor"):
        frappe.get_doc({"doctype": "Role", "role_name": "Head Instructor", "desk_access": 1}).save()

    if not frappe.db.exists("Role", "Head of School"):
        frappe.get_doc({"doctype": "Role", "role_name": "Head Instructor", "desk_access": 1}).save()

    if not frappe.db.exists("Role", "Planner Reviewer"):
        frappe.get_doc({"doctype": "Role", "role_name": "Planner Reviewer", "desk_access": 1}).save()


def add_settings():
    frappe.db.set_single_value(
        "Weekly Planner Settings",
        {
            "name": "Weekly Planner Settings",
            "owner": "Administrator",
            "creation": datetime.now(),
            "modified": datetime.now(),
            "modified_by": "Administrator",
            "title": "Weekly Planner",
            "welcome_text": "This tool will allow your Instructors prepare their weekly lesson plans and submit them for approval. If you have Instructors under you, the table below will show you their weekly planners as well as your own.",
            "show_student_age_in_view": 1,
            "show_student_age_in_print": 1,
        },
    )