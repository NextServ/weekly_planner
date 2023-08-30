import frappe
from datetime import date, datetime

@frappe.whitelist()
def build_planner_report(planner_name):
    # Remove %20 from planner_name
    if planner_name:    
        planner_name = planner_name.replace("%20", " ")

    print("build_planner_report() / planner_name: " + planner_name)

    # First load all students from Planner Detail
    students = frappe.db.sql('''SELECT p.student, s.first_name, s.last_name, s.date_of_birth
                             FROM `tabPlanner Student` p INNER JOIN `tabStudent` s
                             ON p.student = s.name
                             WHERE p.parent = %(p_name)s''', {"p_name": planner_name}, as_dict=True)

    # lessons = frappe.get_all("Planner Lesson", filters={"parent": planner_name}, fields=["*"])
    topics = frappe.get_all("Planner Topic", filters={"parent": planner_name}, fields=["*"])
    lessons = frappe.db.sql('''SELECT p.name, p.date, p.student, p.topic, l.abbreviation from `tabPlanner Lesson` p
                            INNER JOIN `tabLesson Status` l ON p.lesson_status = l.name
                            WHERE parent = %(p_name)s''', {"p_name": planner_name}, as_dict=True)
    
    # Check if show age is enabled
    show_age = frappe.db.get_single_value("Weekly Planner Settings", "show_student_age_in_print")

    # planner_details = [["" for row in range(num_students)] for col in range(num_topics)]
    student_headers = {}
    topic_headers = []

    # Build the table html
    table_html =  "<thead>"
    table_html += "  <tr>"
    table_html += "    <th style='width: 15px'>Topic</th>"

    # Load up the columns
    for student in students:
        if student.student not in student_headers:
            # Calculate age in years and months
            years = None
            months = None
            if student.date_of_birth:
                years = int(diff_months(date.today(), student.date_of_birth) / 12)
                months = years % 12

            # working_dict = "{'student': '" + student.student + "', 'first_name': '" + student.first_name + "', 'last_name': '" + student.last_name + "', "
            # working_dict = working_dict + "'years_old': '" + str(years) + "', 'months_old': '" + str(months) + "'}"
            table_html += "<th class='rotated-text' style='width: 5px'>" + student.last_name + " " + student.first_name
            if show_age:
                table_html += "<br>"
                table_html += "<span class='fs-6 rotated-text'><i>" + str(years) + " Years " + str(months) + " Months</i></span>"
            table_html += "</th>"

        student_headers[student.student] = student.student
    
    table_html += "</tr></thead><tbody>"

    # Load up the rows
    for topic in topics:
        table_html += "<tr><td>" + topic.topic + "</td>"

        if not topic.topic in topic_headers:
            topic_headers.append(topic.topic)

            # loop through keys
            for col_header in student_headers.keys():
                item = [entry for entry in lessons if entry["topic"] == topic.topic and entry["student"] == col_header]
                table_html += "<td class='text-center'>"

                if item != []:
                    print(item)
                    lesson_item = item[0].abbreviation + " " + item[0].date.strftime('%m-%d-%y')
                    table_html += "<span class='badge badge-pill badge-primary text-center'>" + lesson_item + \
                        "<p hidden>student: " + col_header + " | name: " + item[0].name + " | </span>"
                else:
                    table_html += "<span><p hidden>student: " + col_header + " | name: none | </span>"
                
                table_html += "</td>"

    table_html += "</tr>"

    return table_html


@frappe.whitelist()
def diff_months(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


