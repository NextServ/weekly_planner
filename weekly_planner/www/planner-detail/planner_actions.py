import frappe

@frappe.whitelist()
def delete_planner(planner_name):
    # # Delete Planner Student
    # frappe.db.sql('''DELETE FROM `tabPlanner Student` WHERE parent = %(p_name)s''', {"p_name": planner_name})
    # # Delete Planner Topic
    # frappe.db.sql('''DELETE FROM `tabPlanner Topic` WHERE parent = %(p_name)s''', {"p_name": planner_name})
    # # Delete Planner Lesson
    # frappe.db.sql('''DELETE FROM `tabPlanner Lesson` WHERE parent = %(p_name)s''', {"p_name": planner_name})
    # # Delete Planner
    # frappe.db.sql('''DELETE FROM `tabPlanner` WHERE name = %(p_name)s''', {"p_name": planner_name})
    return "success"


@frappe.whitelist()
def new_planner():
    return


@frappe.whitelist()
def show_students():
    return


@frappe.whitelist()    
def add_students():
    return


@frappe.whitelist()
def add_topics():
    return


@frappe.whitelist()
def save_lesson():
    return


@frappe.whitelist()
def delete_lesson():
    return