import frappe
import json
from frappe import _
from datetime import date, datetime
from weekly_planner.utils import diff_months
from weekly_planner.install import add_settings


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
def get_settings():
    # Check if settings exist and create if not
    if not frappe.db.get_single_value("Weekly Planner Settings", "title"):
        add_settings()

    title = frappe.db.get_single_value("Weekly Planner Settings", "title")
    welcome_text = frappe.db.get_single_value("Weekly Planner Settings", "welcome_text")
    show_student_age_in_view = frappe.db.get_single_value("Weekly Planner Settings", "show_student_age_in_view")
    show_student_age_in_print = frappe.db.get_single_value("Weekly Planner Settings", "show_student_age_in_print")
    
    # Build the body of the modal dialog
    modal_html =   '<div class="container px-2 py-2 border bg-light">'
    modal_html +=  '  <div class="row gx-5">'
    modal_html +=  '    <div class="col">'
    modal_html +=  '      <label>' + _("Title") + '</label>'
    modal_html +=  '      <input class="text-align-left bg-light" id="title" type="text" value="' + title + '" required>'
    modal_html +=  '    </div>'
    modal_html +=  '  </div>'
    modal_html +=  '  <br />'
    modal_html +=  '  <div class="row gx-5">'
    modal_html +=  '    <div class="col">'
    modal_html +=  '      <label>' + _("Welcome Text") + '</label><br />'
    modal_html +=  '      <textarea class="text-align-left bg-light" id="welcome_text" rows="5" cols="40" required>' + welcome_text + '</textarea>'
    modal_html +=  '    </div>'
    modal_html +=  '  </div>'
    modal_html +=  '  <br />'
    modal_html +=  '  <div class="form-check">'
    modal_html +=  '    <input class="form-check-input" type="checkbox" value="" id="show_student_age_in_view"' + (' checked' if show_student_age_in_view == 1 else '') + '>'
    modal_html +=  '    <label class="form-check-label" for="show_student_age_in_view">' + _("Show Student Age in View") + '</label>'
    modal_html +=  '  </div>'
    modal_html +=  '  <div class="form-check">'
    modal_html +=  '    <input class="form-check-input" type="checkbox" value="" id="show_student_age_in_print"' + (' checked' if show_student_age_in_print == 1 else '') + '>'
    modal_html +=  '    <label class="form-check-label" for="show_student_age_in_print">' + _("Show Student Age in Print") + '</label>'
    modal_html +=  '  </div>'
    modal_html +=  '</div>'

    return modal_html


@frappe.whitelist()
def save_settings(title, welcome_text, show_student_age_in_view, show_student_age_in_print):
    frappe.db.set_single_value(
        "Weekly Planner Settings",
        {
            "modified": datetime.now(),
            "modified_by": frappe.session.user,
            "title": title,
            "welcome_text": welcome_text,
            "show_student_age_in_view": show_student_age_in_view,
            "show_student_age_in_print": show_student_age_in_print
        }
    )


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
    reports_to = frappe.db.sql('''SELECT name from `tabInstructor`
        WHERE employee = (SELECT name FROM `tabEmployee` WHERE user_id = %(user_id)s)''', \
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
    topics = frappe.get_all("Planner Topic", filters={"parent": planner_name, "is_hidden": 0}, fields=["*"])
    lessons = frappe.db.sql('''SELECT p.name, p.date, p.student, p.topic, l.abbreviation from `tabPlanner Lesson` p
                            INNER JOIN `tabLesson Status` l ON p.lesson_status = l.name
                            WHERE parent = %(p_name)s''', {"p_name": planner_name}, as_dict=True)
    
    # Show age in view?
    show_age = frappe.db.get_single_value("Weekly Planner Settings", "show_student_age_in_view")

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
            table_html += "<th class='text-center'>" + student.last_name + " " + student.first_name
            if show_age:
                table_html += "<br>"
                table_html += "<span class='fs-6 fw-light fst-italic text-center'>" + str(years) + " Years " + str(months) + " Months</span>"
            table_html += "</th>"

        student_headers[student.student] = student.student
    
    table_html += "</tr></thead><tbody>"

    # Load up the rows
    topic_idx = 0
    for topic in topics:
        topic_idx += 1
        table_html += "<tr><td>" + str(topic_idx) + "</td>"
        table_html += "<td>" + topic.topic + "</td>"

        if not topic.topic in topic_headers:
            topic_headers.append(topic.topic)

            # loop through keys
            for col_header in student_headers.keys():
                item = [entry for entry in lessons if entry["topic"] == topic.topic and entry["student"] == col_header]
                table_html += "<td class='text-center'>"

                if item != []:
                    lesson_item = item[0].abbreviation + " " + item[0].date.strftime('%m-%d-%y')
                    table_html += "<span role='button' class='badge badge-pill badge-primary text-center'>" + lesson_item + \
                        "<p hidden>student: " + col_header + " | name: " + item[0].name + " | </span>"
                else:
                    table_html += "<span><p hidden>student: " + col_header + " | name: none | </span>"
                
                table_html += "</td>"

    table_html += "</tr>"

    return table_html


@frappe.whitelist()
def get_lesson_status_options():
    return frappe.db.sql('''SELECT status, abbreviation FROM `tabLesson Status` ORDER BY status''', as_dict=True)


@frappe.whitelist()
def get_students_for_selection(selected_campus, selected_group, planner_name):
    # Build the rest of the SQL statement based on whether there is value in selected_group and selected_campus
    sql = '''SELECT s.name, s.first_name, s.last_name, s.date_of_birth, g.parent FROM `tabStudent Group Student` g
                INNER JOIN `tabStudent` s ON g.student = s.name '''

    if selected_campus and selected_group:
        sql = sql + '''WHERE campus = %(campus)s AND student_group = %(group)s AND s.name NOT IN (SELECT student from `tabPlanner Student` WHERE parent = %(planner_name)s)'''
        students = frappe.db.sql(sql, {"campus": selected_campus, "group": selected_group, "planner_name": planner_name}, as_dict=True)
    elif selected_campus:
        sql = sql + '''WHERE campus = %(campus)s AND s.name NOT IN (SELECT student from `tabPlanner Student` WHERE parent = %(planner_name)s)'''
        students = frappe.db.sql(sql, {"campus": selected_campus, "planner_name": planner_name}, as_dict=True)
    elif selected_group:
        # frappe.msgprint(selected_group + " selected but no campus")
        sql += '''WHERE g.parent = %(group)s AND s.name NOT IN (SELECT student from `tabPlanner Student` WHERE parent = %(planner_name)s)'''
        students = frappe.db.sql(sql, {"group": selected_group, "planner_name": planner_name}, as_dict=True)
    else:
        students = frappe.db.sql('''SELECT s.name, s.first_name, s.last_name, s.date_of_birth, g.parent FROM `tabStudent` s
                                    LEFT JOIN `tabStudent Group Student` g ON s.name = g.student 
                                    WHERE s.name NOT IN (SELECT student from `tabPlanner Student` WHERE parent = %(planner_name)s)''', 
                                    {"planner_name": planner_name}, as_dict=True)

    return students


@frappe.whitelist()
def get_student_for_printing():
    sql = '''SELECT last_name, first_name, name from `tabStudent` 
            WHERE name IN (SELECT DISTINCT student from `tabPlanner Student`)'''
    students = frappe.db.sql(sql, as_dict=True)

    table_html =   '  <thead>'
    table_html +=  '    <tr>'
    table_html +=  '      <th>Last Name</th>'
    table_html +=  '      <th>First Name</th>'
    table_html +=  '      <th>ID</th>'
    table_html +=  '    </tr>'
    table_html +=  '  </thead>'
    table_html +=  '  <tbody>'

    for student in students:
        table_html +=  '  <tr>'
        table_html +=  '    <td>' + student.last_name + '</td>'
        table_html +=  '    <td>' + student.first_name + '</td>'
        table_html +=  '    <td>' + student.name + '</td>'
        table_html +=  '  </tr>'

    table_html +=  '  </tbody>'

    return table_html


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
def get_topics_for_selection(planner_name, show_action):
    # Retrieve topics that are not already in Planner Topic
    if show_action == "add":
        sql = '''SELECT t.name subject, c.parent, t.name record_key FROM `tabTopic` t
                LEFT JOIN `tabCourse Topic` c ON t.name = c.topic    
                WHERE t.name NOT IN (SELECT topic FROM `tabPlanner Topic` WHERE (parent = %(planner_name)s)
                AND (is_hidden = 0))'''
    else:
        sql = '''SELECT t.topic subject, c.parent, t.name record_key FROM `tabPlanner Topic` t
                LEFT JOIN `tabCourse Topic` c ON t.topic = c.topic
                WHERE (t.parent = %(planner_name)s) AND (is_hidden = 0)'''
    topics = frappe.db.sql(sql, {"planner_name": planner_name}, as_dict=True)

    return topics


@frappe.whitelist()
def save_topics(planner_name, insert_list, show_action):
    topics = json.loads(insert_list)
    
    planner_doc = frappe.get_doc("Weekly Planner", planner_name)
    append_count = 0
    recs_to_hide = []
    for t in topics:
        if show_action == "add":
            # Check to see if the topic already exists in the Planner Topic table
            if frappe.db.exists("Planner Topic", {"topic": t, "parent": planner_name}):
                recs_to_hide.append(t)

            else:
                planner_doc.append("topics", {"topic": t})
                append_count += 1
        else:
            frappe.db.sql('''UPDATE `tabPlanner Topic` SET is_hidden = 1 WHERE name = %1s''', t)

    if append_count:
        planner_doc.save()

    if len(recs_to_hide):
        for r in recs_to_hide:
            frappe.db.sql('''UPDATE `tabPlanner Topic` SET is_hidden = 0
                WHERE (topic = %(topic)s) AND (parent = %(planner_name)s)''', {"topic": r, "planner_name": planner_name})
   
    return


@frappe.whitelist()
def build_add_students_modal(planner_name):
    planner = frappe.get_doc("Weekly Planner", planner_name)
    campuses = frappe.get_all("Campus", fields=["campus_name"])
    groups = frappe.get_all("Student Group", fields=["student_group_name"])

    # Get the roles for the Instructor
    cur_user = frappe.get_user()
    cur_roles = cur_user.get_roles()
    is_hos = "Head of School" in cur_roles
    is_head = "Head Instructor" in cur_roles
    is_instructor_only = not (is_head or is_hos)

    body_html =  '<div class="container-fluid px-2 py-2 border bg-light">'
    body_html += '  <div class="row">'
    body_html += '    <div class="col">'
    body_html += '      <label>' + _("Filter by Campus (disabled for now)") + '</label>'
    body_html += '        <select class="form-select" aria-label="Campus Select" id="selected_campus" disabled>'
    body_html += '          <option selected value="">All Campuses</option>'

    # Build the campus options
    for campus in campuses:
        body_html += '      <option value="' + campus.campus_name + '">' + campus.campus_name + '</option>'

    body_html += '        </select>'
    body_html += '    </div>'
    body_html += '    <div class="col">'
    body_html += '      <label>' + _("Filter by Student Group") + '</label>'
    body_html += '      <select class="form-select" aria-label="Student Group Select" id="selected_group">'

    # Build the student group options
    if is_instructor_only:
        body_html += '     <option selected value="' + planner.student_group + '">' + planner.student_group + '</option>'
    else:
        body_html += '     <option selected value="">All Groups</option>'
        for g in groups:
            body_html += ' <option value="' + g.student_group_name + '">' + g.student_group_name + '</option>'
    
    body_html += '      </select>'
    body_html += '    </div>'
    body_html += '  </div>'
    body_html += '  <div class="row">'
    body_html += '    <div class="col">'
    body_html += '      <hr>'
    body_html += '      <div class="d-grid gap-2">'
    body_html += '        <button type="button" class="btn btn-primary" onclick="show_students()">' + _("Show Students") + '</button>'
    body_html += '      </div>'
    body_html += '    </div>'
    body_html += '  </div>'
    
    # Students table
    body_html += '  <br />'
    body_html += '  <table class="table table-md table-striped" style="width: 100%"  id="students_table"></table>'
    body_html += '</div>'
    
    return body_html


@frappe.whitelist()
def build_lesson_entry_modal(student, topic, lesson_name, status_abbr, lesson_date, org_lesson_value):
    # Get lesson status value based on abbreviation
    try:
        # Convert lesson_date to date object
        lesson_date = datetime.strptime(lesson_date, '%m-%d-%y').strftime('%Y-%m-%d')
    except:
        lesson_date = ""

    # Get student name
    student_name = frappe.get_doc("Student", student, ["first_name", "last_name"])
    
    # Get all lesson status options
    status_value = ""
    status_options = ""
    for option in frappe.db.sql('''SELECT status, is_default, abbreviation FROM `tabLesson Status` ORDER BY status''', as_dict=True):
        if (org_lesson_value == "none" and option.is_default) or (option.abbreviation == status_abbr):
            status_value = option.status
        else:
            status_options += '<option value="' + option.status + '">' + option.status + '</option>'
    
    # Build the modal for the lesson entry
    modal_html =   '<div class="container px-2 py-2">'
    modal_html +=  '  <div class="row gx-5">'
    modal_html +=  '    <div class="col">'
    modal_html +=           ("Student: ") + '<b>' + student_name.first_name + ' ' + student_name.last_name + '</b>'
    modal_html +=  '    </div>'
    modal_html +=  '  </div>'
    modal_html +=  '  <div class="row gx-5">'
    modal_html +=  '    <div class="col">'
    modal_html +=           ("Topic: ") + '<b>' + topic + '</b>'
    modal_html +=  '    </div>'
    modal_html +=  '  </div>'
    modal_html +=  '  <br />'
    modal_html +=   '<div class="container px-2 py-2 border bg-light">'
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
    status = frappe.db.sql('''SELECT name, abbreviation FROM `tabLesson Status` WHERE status = %(status)s''', {"status": status}, as_dict=True)
    status_id = status[0].name
    status_abbr = status[0].abbreviation

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
        lesson_name = lesson_doc.lessons[-1].name
        # print("* save_lesson_entry\n" + "new lesson_name: " + lesson_name)

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
        
        # frappe.db.set_value("Planner Lesson", lesson_name, {
        #     "lesson_status": status_id,
        #     "date": lesson_date
        # })
        original.lesson_status = status_id
        original.date = lesson_date
        original.save()

    # Change the date format of lesson_date to the format mm-dd-yy
    lesson_date = datetime.strptime(lesson_date, '%Y-%m-%d').strftime('%m-%d-%y')
    
    # Create an array of status_id and lesson_date
    table_html = "<span role='button' class='badge badge-pill badge-primary text-center'>" + status_abbr + " " + lesson_date + \
        "<p hidden>student: " + student + " | name: " + lesson_name + " | </span>"

    return_array = []
    return_array.append(table_html)
    return_array.append(lesson_name)
    return return_array


@frappe.whitelist()
def delete_lesson_entry(lesson_name):
    # Delete the lesson entry and change history
    frappe.db.delete("Planner Lesson History", {"planner_lesson": lesson_name})
    frappe.db.delete("Planner Lesson", lesson_name)

    return "success"
    

@frappe.whitelist()
def hos_show_all():
    cur_user = frappe.get_user()
    employee = frappe.get_doc("Employee", frappe.get_all("Employee", filters={"user_id": cur_user.name}, fields=["name"])[0])

    employee.hos_show_all = 1 if employee.hos_show_all == 0 else 0
    employee.save()



@frappe.whitelist()
def hex_to_rgb(hex_color):
    # Convert hex color to RGB tuple
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


@frappe.whitelist()
def get_brightness(rgb_color):
    # Calculate the brightness of the color (RGB)
    r, g, b = rgb_color
    return (r * 299 + g * 587 + b * 114) / 1000


@frappe.whitelist()
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