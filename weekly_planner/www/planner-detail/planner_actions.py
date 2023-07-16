import frappe
from frappe import _
import uuid

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
def add_students(selected_student, planner_name):
    # Add students in the Planner Student table for each student selected
    for student in selected_student:
        frappe.db.sql('''INSERT INTO `tabPlanner Student` (parent, student) 
                      VALUES (%(p_name)s, %(student)s)''', {"p_name": planner_name, "student": student})

    return "success"


@frappe.whitelist()
def get_lesson_status_options():
    return frappe.db.sql('''SELECT status, abbreviation FROM `tabLesson Status` ORDER BY status''', as_dict=True)


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


@frappe.whitelist()
def build_lesson_entry_modal(status_abbr, lesson_date, org_lesson_value):
    # Get lesson status value based on abbreviation
    if org_lesson_value == "none":
        status_value = ""
        lesson_date = ""
    else:
        status_value = frappe.db.sql('''SELECT status FROM `tabLesson Status` WHERE abbreviation = %(status)s''', {"status": status_abbr}, as_dict=True)[0].status

    # Get all lesson status options
    status_options = ""
    for option in frappe.db.sql('''SELECT status FROM `tabLesson Status` ORDER BY status''', as_dict=True):
        status_options += '<option>' + option.status + '</option>'
    
    # Build the modal for the lesson entry
    modal_html =     '<div class="container px-2 py-2 border bg-light">'
    modal_html +=    '    <div class="row">'

    modal_html +=    '        <label>' + _("Lesson Status")
    modal_html +=    '            <input class="input-group-text text-align-left" list="options" name="status_options" id="selected_option" '
    modal_html +=    '            value="' + status_value + '" required></label>'

    modal_html +=    '        <datalist id="options">'
    modal_html +=                 status_options
    modal_html +=    '        </datalist>'
    modal_html +=    '    </div>'
    modal_html +=    '    <div class="row">'
    modal_html +=    '        <label>' + _("Date") + '<input class="input-group-text text-align-left" list="options" name="status_options" '
    modal_html +=    '            id="lesson_date" type="date" value="' + lesson_date + '" required></label>'
    modal_html +=    '    </div>'
    modal_html +=    '</div>'

    return modal_html


@frappe.whitelist()
def save_lesson_entry(lesson_name, planner_name, student, topic, status, lesson_date, org_lesson_value):
    # Get status id
    status_id = frappe.db.sql('''SELECT name FROM `tabLesson Status` WHERE status = %(status)s''', {"status": status}, as_dict=True)[0].name

    # Save the lesson entry
    if org_lesson_value == "none":
        # lesson_name = frappe.generate_hash("", 10)      # Generate unique name for the lesson entry
        lesson_name = uuid.uuid4()
        result = frappe.db.sql('''INSERT INTO `tabPlanner Lesson` (name, parent, student, topic, lesson_status, date) 
                        VALUES (%(name)s, %(p_name)s, %(student)s, %(topic)s, %(status)s, %(lesson_date)s)''', 
                        {"name": lesson_name, "p_name": planner_name, "student": student, "topic": topic, "status": status_id, 
                        "lesson_date": lesson_date})
    else:    
        result = frappe.db.sql('''UPDATE `tabPlanner Lesson` SET lesson_status = %(status)s, date = %(date)s 
                        WHERE name = %(name)s''', {"status": status_id, "date": lesson_date, "name": lesson_name})
    
    return result