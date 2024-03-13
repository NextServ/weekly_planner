import frappe
from datetime import datetime


def after_install():
    pass


def after_sync():
    add_roles()


def add_roles():
    if not frappe.db.exists("Role", "Sales Partner"):
        frappe.get_doc({"doctype": "Role", "role_name": "Sales Partner", "desk_access": 0}).save()