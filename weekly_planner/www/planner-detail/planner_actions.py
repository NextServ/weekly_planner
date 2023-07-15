import frappe

@frappe.whitelist(methods=["POST"])
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
    pass


@frappe.whitelist()    
def add_students(selected_student, planner_name):
    # Add students in the Planner Student table for each student selected
    for student in selected_student:
        frappe.db.sql('''INSERT INTO `tabPlanner Student` (parent, student) 
                      VALUES (%(p_name)s, %(student)s)''', {"p_name": planner_name, "student": student})

    return "success"


@frappe.whitelist()
def add_topics():
    pass


@frappe.whitelist()
def save_lesson():
    pass


@frappe.whitelist()
def delete_lesson():
    pass


@frappe.whitelist()
def get_students_for_selection(selected_campus, selected_group):
    # Build the rest of the SQL statement based on whether there is value in selected_group and selected_campus
    sql = ""

    if selected_campus and selected_group:
        sql = sql + '''WHERE campus = %(campus)s AND student_group = %(group)s'''
        students = frappe.db.sql(sql, {"campus": selected_campus, "group": selected_group}, as_dict=True)
    elif selected_campus:
        sql = sql + '''WHERE campus = %(campus)s'''
        students = frappe.db.sql(sql, {"campus": selected_campus}, as_dict=True)
    elif selected_group:
        # frappe.msgprint(selected_group + " selected but no campus")
        sql = '''SELECT s.name, s.first_name, s.last_name, s.date_of_birth FROM `tabStudent Group Student` g
                INNER JOIN `tabStudent` s ON g.student = s.name 
                WHERE g.parent = %(group)s'''
        students = frappe.db.sql(sql, {"group": selected_group}, as_dict=True)
    else:
        students = frappe.db.sql('''SELECT first_name, last_name, date_of_birth FROM `tabStudent`''', as_dict=True)

    return students


@frappe.whitelist()
def get_topics_for_selection(planner_name):
    # Retrieve topics that are not already in Planner Topic
    sql = '''SELECT name, topic_name FROM `tabTopic` WHERE name NOT IN
            (SELECT topic FROM `tabPlanner Topic` WHERE parent = %(planner_name)s)'''
    topics = frappe.db.sql(sql, {"planner_nam": planner_name}, as_dict=True)

    return topics