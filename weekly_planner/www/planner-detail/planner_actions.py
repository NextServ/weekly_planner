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


@frappe.whitelist()
def duplicate_planner(planner_name, selected_group, plan_date, include_lessons):
    # Get the planner record
    planner = frappe.get_doc("Weekly Planner", planner_name)

    # Create a new planner record
    new_planner = frappe.new_doc("Weekly Planner")
    new_planner.instructor = planner.instructor
    new_planner.student_group = selected_group
    new_planner.start_date = plan_date 
    new_planner.description = planner.description
    new_planner.insert()

    # Create the students
    students = frappe.get_all("Planner Student", filters={"parent": planner.name}, fields=["*"])
    for s in students:
        new_planner.append("students", {"student": s.student})

    # Create the topics
    topics = frappe.get_all("Planner Topic", filters={"parent": planner.name}, fields=["*"])
    for t in topics:
        new_planner.append("topics", {"topic": t.topic})

    # Create the lessons
    if include_lessons:
        lessons = frappe.get_all("Planner Lesson", filters={"parent": planner.name}, fields=["*"])
        for l in lessons:
            new_planner.append("lessons", {
                "lesson_status": l.lesson_status,
                "date": plan_date,
                "topic": l.topic,
                "student": l.student
            })

    new_planner.save()

    return new_planner.name


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
                    table_html += "<span role='button' class='badge badge-pill badge-primary text-center'>" + lesson_item + \
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
    sql = '''SELECT t.name, parent FROM `tabTopic` t
            LEFT JOIN `tabCourse Topic` c ON t.name = c.topic    
            WHERE t.name NOT IN (SELECT topic FROM `tabPlanner Topic` WHERE parent = %(planner_name)s)'''
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
def build_lesson_entry_modal(lesson_name, status_abbr, lesson_date, org_lesson_value):
    # Get lesson status value based on abbreviation
    if org_lesson_value == "none":
        lesson_date = ""
    else:
        # Convert lesson_date to date object
        lesson_date = datetime.strptime(lesson_date, '%m-%d-%y').strftime('%Y-%m-%d')

    # Get all lesson status options
    status_value = ""
    status_options = ""
    for option in frappe.db.sql('''SELECT status, is_default, abbreviation FROM `tabLesson Status` ORDER BY status''', as_dict=True):
        if (org_lesson_value == "none" and option.is_default) or (option.abbreviation == status_abbr):
            status_value = option.status
        else:
            status_options += '<option value="' + option.status + '">' + option.status + '</option>'
    
    # Build the modal for the lesson entry
    modal_html =   '<div class="container px-2 py-2 border bg-light">'
    modal_html +=  '  <div class="row gx-5">'
    modal_html +=  '    <div class="col">'
    modal_html +=  '      <label>' + _("Status") + '</label>'
    modal_html +=  '      <select class="form-select form-select-md bg-light" name="lesson_status" id="lesson_status" aria-label="Lesson Status" required>'
    modal_html +=  '        <option value="' + status_value + '" selected>' + status_value + '</option>'
    modal_html +=           status_options
    modal_html +=  '      </select>'
    modal_html +=  '    </div>'
    modal_html +=  '    <div class="col">'
    modal_html +=  '      <label>' + _("Date") + '</label><br />'
    modal_html +=  '      <input class="text-align-left bg-light" id="lesson_date" type="date" value="' + lesson_date + '" required>'
    modal_html +=  '    </div>'
    modal_html +=  '  </div>'
    modal_html +=  '</div>'

    # Build the table only if this isn't a new lesson entry or history table is empty
    lesson_history = frappe.get_all("Planner Lesson History", fields=["*"], filters={"planner_lesson": lesson_name})
    if org_lesson_value == "none" or len(lesson_history) == 0:
        return modal_html
    
    modal_html +=  '<hr />'
    modal_html +=  '<h6>' + _("Change History") + '</h6>'
    modal_html +=  '<table class="table table-sm table-striped" style="width: 100%"  id="history_table">'
    modal_html +=  '  <thead>'
    modal_html +=  '    <tr>'
    modal_html +=  '      <th>Status</th>'
    modal_html +=  '      <th>Org Date</th>'
    modal_html +=  '      <th>Changed By</th>'
    modal_html +=  '    </tr>'
    modal_html +=  '  </thead>'
    modal_html +=  '  <tbody>'

    for h in lesson_history:
        modal_html +=  '  <tr>'
        modal_html +=  '    <td>' + h.lesson_status + '</td>'
        modal_html +=  '    <td>' + h.original_date.strftime("%m-%d-%y") + '</td>'
        modal_html +=  '    <td>' + h.changed_by + '</td>'
        modal_html +=  '  </tr>'

    modal_html +=  '  </tbody>'
    modal_html +=  '</table>'


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
        # Retrieve Instructor based on frappe.session.user
        instructor = frappe.db.sql('''SELECT i.name FROM `tabInstructor` i INNER JOIN `tabEmployee` e on i.employee = e.name
                        WHERE e.user_id = %(user_id)s''', {"user_id": frappe.session.user}, as_dict=True)[0].name
        
        # Save the original lesson entry to the history table
        original = frappe.get_doc("Planner Lesson", lesson_name)
        org_status = frappe.get_all("Lesson Status", fields=["status"], filters={"name": original.lesson_status})[0].status
        history = frappe.new_doc("Planner Lesson History")
        history.planner_lesson = lesson_name
        history.lesson_status = org_status
        history.original_date = original.date
        history.changed_by = instructor
        history.date_changed = datetime.today()
        history.insert()
        
        frappe.db.set_value("Planner Lesson", lesson_name, {
            "lesson_status": status_id,
            "date": lesson_date
        })
    
    return "success"


@frappe.whitelist()
def delete_lesson_entry(lesson_name):
    # Delete the lesson entry and change history
    frappe.db.delete("Planner Lesson History", {"planner_lesson": lesson_name})
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
