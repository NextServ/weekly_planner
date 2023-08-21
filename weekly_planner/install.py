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


def add_settings():
    settings = frappe.new_doc("tabSingle")
    settings.doctype = "Weekly Planner Settings"
    settings.field = "name"
    settings.value = "Weekly Planner Settings"
    settings.insert()

    settings = frappe.new_doc("tabSingle")
    settings.doctype = "Weekly Planner Settings"
    settings.field = "owner"
    settings.value = "Administrator"
    settings.insert()

    settings = frappe.new_doc("tabSingle")
    settings.doctype = "Weekly Planner Settings"
    settings.field = "creation"
    settings.value = datetime.now()
    settings.insert()

    settings = frappe.new_doc("tabSingle")
    settings.doctype = "Weekly Planner Settings"
    settings.field = "modified"
    settings.value = datetime.now()
    settings.insert()

    settings = frappe.new_doc("tabSingle")
    settings.doctype = "Weekly Planner Settings"
    settings.field = "modified_by"
    settings.value = "Administrator"
    settings.insert()

    settings = frappe.new_doc("tabSingle")
    settings.doctype = "Weekly Planner Settings"
    settings.field = "title"
    settings.value = "Weekly Planner"
    settings.insert()

    settings = frappe.new_doc("tabSingle")
    settings.doctype = "Weekly Planner Settings"
    settings.field = "welcome_text"
    settings.value = "This tool will allow your Instructors prepare their weekly lesson plans and submit them for approval. If you have Instructors under you, the table below will show you their weekly planners as well as your own."
    settings.insert()