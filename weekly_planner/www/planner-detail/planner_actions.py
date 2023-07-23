import frappe
from frappe import _
import json
from datetime import date, datetime


@frappe.whitelist()
def create_planner(instructor, selected_group, start_date, description):
    planner = frappe.new_doc("Weekly Planner")
    planner.instructor = instructor
    planner.student_group = selected_group
    planner.start_date = start_date
    planner.description = description
    planner.insert()

    return planner.name


@frappe.whitelist(methods=["POST"])
def delete_planner(planner_name):
    planner_name = planner_name.replace("%20", " ")
    frappe.delete_doc("Weekly Planner", planner_name)
    return "success"


@frappe.whitelist()
def submit_planner(planner_name):
    total_items = len(frappe.get_all("Planner Lesson", filters={"parent": planner_name}, fields=["name"]))
    if total_items == 0:
        return _("Planner must have at least one lesson entry.")

    # First check to see if the Reports To field of the Instructor's HR record has value
    reports_to = frappe.db.sql('''SELECT COUNT(reports_to) FROM `tabEmployee` WHERE user_id = %(user_id)s''', \
        {"user_id": frappe.session.user})
    
    # Also check if current user has Head Instructor role
    is_head = frappe.db.sql('''SELECT COUNT(name) FROM `tabHas Role` WHERE parent = %(user_id)s AND role = "Head Instructor"''', \
        {"user_id": frappe.session.user})
    
    print("reports to: " + str(reports_to) + " | is_head: " + str(is_head))
    
    if not reports_to and not is_head:
        return _("Instructor's HR record does not have a Reports To value. Please update the record and try again.")
    
    planner = frappe.get_doc("Weekly Planner", planner_name)
    planner.status = 1
    planner.save()

    return "success"


@frappe.whitelist()
def approve_planner(planner_name):
    reports_to = frappe.db.sql('''SELECT name FROM `tabInstructor` WHERE user = %(user_id)s''', \
        {"user_id": frappe.session.user}, as_dict=True)

    planner = frappe.get_doc("Weekly Planner", planner_name)
    if planner.is_approved:
        return _("Planner is already approved.")

    planner.is_approved = True
    planner.approved_by = reports_to[0].name
    planner.save()

    return "success"


@frappe.whitelist()
def build_planner_items(planner_name):
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

    # planner_details = [["" for row in range(num_students)] for col in range(num_topics)]
    student_headers = {}
    topic_headers = []

    # Build the table html
    table_html =  "<thead>"
    table_html += "  <tr>"
    table_html += "    <th>#</th>"
    table_html += "    <th>Topic</th>"

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
            table_html += "<th class='text-center'>" + student.last_name + " " + student.first_name + "<br>"
            table_html += "<span class='fs-6 text-center'><i>" + str(years) + " Years " + str(months) + " Months</i></span>"
            table_html += "</th>"

        student_headers[student.student] = student.student
    
    table_html += "</tr></thead><tbody>"

    # Load up the rows
    for topic in topics:
        table_html += "<tr><td>" + str(topic.idx) + "</td>"
        table_html += "<td>" + topic.topic + "</td>"

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


@frappe.whitelist()
def get_lesson_status_options():
    return frappe.db.sql('''SELECT status, abbreviation FROM `tabLesson Status` ORDER BY status''', as_dict=True)


@frappe.whitelist()
def get_students_for_selection(selected_campus, selected_group):
    # Build the rest of the SQL statement based on whether there is value in selected_group and selected_campus
    sql = '''SELECT s.name, s.first_name, s.last_name, s.date_of_birth, g.parent FROM `tabStudent Group Student` g
                INNER JOIN `tabStudent` s ON g.student = s.name '''

    if selected_campus and selected_group:
        sql = sql + '''WHERE campus = %(campus)s AND student_group = %(group)s AND s.name NOT IN (SELECT student from `tabPlanner Student`)'''
        students = frappe.db.sql(sql, {"campus": selected_campus, "group": selected_group}, as_dict=True)
    elif selected_campus:
        sql = sql + '''WHERE campus = %(campus)s AND s.name NOT IN (SELECT student from `tabPlanner Student`)'''
        students = frappe.db.sql(sql, {"campus": selected_campus}, as_dict=True)
    elif selected_group:
        # frappe.msgprint(selected_group + " selected but no campus")
        sql += '''WHERE g.parent = %(group)s AND s.name NOT IN (SELECT student from `tabPlanner Student`)'''
        students = frappe.db.sql(sql, {"group": selected_group}, as_dict=True)
    else:
        students = frappe.db.sql('''SELECT s.name, s.first_name, s.last_name, s.date_of_birth, g.parent FROM `tabStudent` s
                                    LEFT JOIN `tabStudent Group Student` g ON s.name = g.student 
                                    WHERE s.name NOT IN (SELECT student from `tabPlanner Student`)''', as_dict=True)

    return students


@frappe.whitelist()    
def save_students(planner_name, insert_list):
    # Add students in the Planner Student table for each student selected
    students = json.loads(insert_list)

    planner_doc = frappe.get_doc("Weekly Planner", planner_name)
    for s in students:
        planner_doc.append("students", {
            "student": s
        })

    planner_doc.save()
   
    return 


@frappe.whitelist()
def get_topics_for_selection(planner_name):
    # Retrieve topics that are not already in Planner Topic
    # select topic, course_name from `tabCourse Topic` t inner join `tabCourse` c on parent = c.name order by course_name, topic;
    sql = '''SELECT topic, course_name FROM `tabCourse Topic` t
            INNER JOIN `tabCourse` c ON t.parent = c.name    
            WHERE topic NOT IN (SELECT topic FROM `tabPlanner Topic` WHERE parent = %(planner_name)s)'''
    topics = frappe.db.sql(sql, {"planner_name": planner_name}, as_dict=True)

    return topics


@frappe.whitelist()
def save_topics(planner_name, insert_list):
    topics = json.loads(insert_list)
    
    planner_doc = frappe.get_doc("Weekly Planner", planner_name)
    for t in topics:
        planner_doc.append("topics", {
            "topic": t
        })

    planner_doc.save()
   
    return


@frappe.whitelist()
def build_lesson_entry_modal(status_abbr, lesson_date, org_lesson_value):
    # Get lesson status value based on abbreviation
    if org_lesson_value == "none":
        status_value = ""
        lesson_date = ""
    else:
        # Convert lesson_date to date object
        lesson_date = datetime.strptime(lesson_date, '%m-%d-%y').strftime('%Y-%m-%d')
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

    print(modal_html)
    
    return modal_html


@frappe.whitelist()
def save_lesson_entry(lesson_name, planner_name, student, topic, status, lesson_date, org_lesson_value):
    # Get status id
    status_id = frappe.db.sql('''SELECT name FROM `tabLesson Status` WHERE status = %(status)s''', {"status": status}, as_dict=True)[0].name

    # Save the lesson entry
    if org_lesson_value == "none":
        # lesson_name = frappe.generate_hash("", 10)      # Generate unique name for the lesson entry
        # lesson_name = uuid.uuid4()
        # result = frappe.db.sql('''INSERT INTO `tabPlanner Lesson` (name, parent, student, topic, lesson_status, date) 
        #                 VALUES (%(name)s, %(p_name)s, %(student)s, %(topic)s, %(status)s, %(lesson_date)s)''', 
        #                 {"name": lesson_name, "p_name": planner_name, "student": student, "topic": topic, "status": status_id, 
        #                 "lesson_date": lesson_date})
        lesson_doc = frappe.get_doc("Weekly Planner", planner_name)
        lesson_doc.append("lessons", {
            "student": student,
            "topic": topic,
            "lesson_status": status_id,
            "date": lesson_date
        })

        lesson_doc.save()


    else:    
        # result = frappe.db.sql('''UPDATE `tabPlanner Lesson` SET lesson_status = %(status)s, date = %(date)s 
        #                 WHERE name = %(name)s''', {"status": status_id, "date": lesson_date, "name": lesson_name})
        
        frappe.db.set_value("Planner Lesson", lesson_name, {
            "lesson_status": status_id,
            "date": lesson_date
        })
    
    return "success"


@frappe.whitelist()
def delete_lesson_entry(lesson_name):
    # Delete the lesson entry
    frappe.db.delete("Planner Lesson", lesson_name)

    return "success"


def hex_to_rgb(hex_color):
    # Convert hex color to RGB tuple
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def get_brightness(rgb_color):
    # Calculate the brightness of the color (RGB)
    r, g, b = rgb_color
    return (r * 299 + g * 587 + b * 114) / 1000


def adjust_text_color(hex_background_color):
    # Get the RGB values of the background color
    rgb_color = hex_to_rgb(hex_background_color)

    # Calculate the brightness of the background color
    brightness = get_brightness(rgb_color)

    # Choose text color based on the brightness
    if brightness >= 128:
        return '#000000'  # Black for light background
    else:
        return '#FFFFFF'  # White for dark background
