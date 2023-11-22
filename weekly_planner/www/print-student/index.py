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
    context.instructor = frappe.form_dict.get("planner-instructor")
    context.student_group = frappe.form_dict.get("student-group")
    
    student_id = frappe.form_dict.get("student")
    context.student_id = frappe.form_dict.get("student")
    context.student = frappe.get_doc("Student", student_id)

    # sql = """SELECT topic, date FROM `tabPlanner Lesson`
    #         WHERE (student = %(student)s) AND
    #         (date BETWEEN %(start_date)s AND %(end_date)s)"""
    sql = """SELECT P.topic, P.date, P.student, C.parent, C.topic
            FROM `tabPlanner Lesson` P 
            INNER JOIN `tabCourse Topic` C
            ON P.topic = C.topic
            WHERE (student = %(student)s) AND
            (date BETWEEN %(start_date)s AND %(end_date)s)"""
    
    if context.limit == "true":
        sql += " AND (parent = %(planner)s)"

    sql += " ORDER BY date ASC"
    print("print-student | get_context | sql: " + sql)

    context.lessons = frappe.db.sql(sql, {"student": student_id, "start_date": context.start_date, \
        "end_date": context.end_date, "planner": planner_name}, as_dict=True)
    
    sql2 = """SELECT M.assessment, M.things_to_bring, M.supplementary_work, M.comments
            FROM `tabMonthly Behavioral Assessment` M
            INNER JOIN `tabPlanner Lesson` P
            ON M.student = P.student
            WHERE (M.student = %(student)s)"""

    context.monthly_behavioral_assessment = frappe.db.sql(sql2, {"student": student_id}, as_dict=True)

    # Just in case the student does not have a record the the monthly behavioral assessment, put a blank string data for display to avoid error
    if len(context.monthly_behavioral_assessment) < 1:
        context.monthly_behavioral_assessment = [
            {
                "assessment": " ",
                "things_to_bring": " ",
                "supplementary_work": " ",
                "comments": " ",
            }
        ]
        
    return context