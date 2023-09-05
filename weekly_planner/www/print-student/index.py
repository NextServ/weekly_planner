# weekly_planner details
import frappe

no_cache = 1

def get_context(context):
    context.banner_image = frappe.db.get_single_value("Website Settings", "banner_image")
    context.title = frappe.db.get_single_value("Weekly Planner Settings", "title")

    # Get planner_name from url parameter
    planner_name = frappe.form_dict.get("planner-name").replace("%20", " ")
    context.planner = frappe.get_doc("Weekly Planner", planner_name)
    context.start_date = frappe.form_dict.get("start-date")
    context.end_date = frappe.form_dict.get("end-date")
    context.limit = frappe.form_dict.get("limit-to-planner")
    
    
    student_id = frappe.form_dict.get("student")
    context.student = frappe.get_doc("Student", student_id)

    sql = """SELECT topic, date FROM `tabPlanner Lesson`
            WHERE (student = %(student)s) AND
            (date BETWEEN %(start_date)s AND %(end_date)s)"""
    
    if context.limit == "true":
        sql += " AND (parent = %(planner)s)"

    sql += " ORDER BY date ASC"
    print("print-student | get_context | sql: " + sql)

    context.lessons = frappe.db.sql(sql, {"student": student_id, "start_date": context.start_date, \
        "end_date": context.end_date, "planner": planner_name}, as_dict=True)

    return context
