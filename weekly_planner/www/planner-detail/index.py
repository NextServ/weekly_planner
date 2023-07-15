# weekly_planner details
import frappe
from datetime import date

def get_context(context):
    context.banner_image = frappe.db.get_single_value("Website Settings", "banner_image")

    # Make sure user has the correct role
    acceptable_roles = ["Instructor", "Head Instructor", "System Manager"]
    context.invalid_role = True
    cur_user = frappe.get_user()
    cur_roles = cur_user.get_roles()

    for role in cur_roles:
        if role in acceptable_roles:
            context.invalid_role = False
            break

    # Get planner_name from url parameter
    planner_name = frappe.form_dict.get("planner-name")
    context.planner = frappe.get_doc("Weekly Planner", planner_name)
    
    # Remove %20 from planner_name
    if planner_name:    
        planner_name = planner_name.replace("%20", " ")

    # entries = {
    #     "math": {
    #         "juan": ["wed 1pm", "fri 8am"],
    #         "pedro": ["mon 1pm", "tue 10am"],
    #         "jorge": ["wed 1pm", "fri 10am"],
    #     },
    #     "science": {
    #         "juan": ["tue 2pm", "thu 9am"],
    #         "pedro": ["tue 2pm", "thu 10am"],
    #     },
    #     "philosophy": {
    #         "juan": ["wed 1pm", "fri 8am"],
    #         "jorge": ["fri 3pm"],
    #     },
    # }

    # # Load planner details
    # context.student_headers = frappe.get_all("Planner Student", filters={"parent": planner_name}, fields=["*"])
    # context.topic_headers = frappe.get_all("Planner Topic", filters={"parent": planner_name}, fields=["*"])
    # context.entries = frappe.get_all("Planner Lesson", filters={"parent": planner_name}, fields=["*"])
    # context.empty_planner = len(context.student_headers) + len(context.topic_headers) + len(context.entries)

    topic_headers, student_headers, planner_details = load_planner_details(planner_name) # this function returns three values
    context.topic_headers = topic_headers
    context.planner_details = planner_details
    context.student_headers = student_headers
    context.empty_planner = len(context.student_headers) + len(context.topic_headers) + len(context.planner_details)
    context.campuses = frappe.get_all("Campus", fields=["campus_name"])
    context.student_groups = frappe.get_all("Student Group", fields=["student_group_name"])

    return context


def load_planner_details(planner_name):
    # First load all students from Planner Detail
    students = frappe.db.sql('''SELECT p.student, s.first_name, s.last_name, s.date_of_birth
                             FROM `tabPlanner Student` p INNER JOIN `tabStudent` s
                             ON p.student = s.name
                             WHERE p.parent = %(p_name)s''', {"format": "%Y%m", "p_name": planner_name}, as_dict=True)

    # lessons = frappe.get_all("Planner Lesson", filters={"parent": planner_name}, fields=["*"])
    topics = frappe.get_all("Planner Topic", filters={"parent": planner_name}, fields=["*"])
    lessons = frappe.db.sql('''SELECT p.date, p.student, p.topic, l.abbreviation from `tabPlanner Lesson` p
                            INNER JOIN `tabLesson Status` l ON p.lesson_status = l.name
                            WHERE parent = %(p_name)s''', {"p_name": planner_name}, as_dict=True)

    # planner_details = [["" for row in range(num_students)] for col in range(num_topics)]
    planner_details = {}
    student_headers = {}
    topic_headers = []

    # Load up the columns
    for student in students:
        if student.student not in student_headers:
            student_info =  {}

            # Calculate age in years and months
            years = None
            months = None
            if student.date_of_birth:
                years = int(diff_months(date.today(), student.date_of_birth) / 12)
                months = years % 12

            # working_dict = "{'student': '" + student.student + "', 'first_name': '" + student.first_name + "', 'last_name': '" + student.last_name + "', "
            # working_dict = working_dict + "'years_old': '" + str(years) + "', 'months_old': '" + str(months) + "'}"
            student_info = {
                "student": student.student,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "years_old": years,
                "months_old": months,
                "date_of_birth": student.date_of_birth
            }

            student_headers[student.student] = student_info

    # Load up the rows
    for topic in topics:
        if not topic.topic in topic_headers:
            topic_headers.append(topic.topic)
            planner_details[topic.topic] = {}

            # loop through keys
            for col_header in student_headers.keys():
                topic_schedule = [entry for entry in lessons if entry["topic"] == topic.topic and \
                    entry["student"] == col_header]
                planner_details[topic.topic][col_header] = topic_schedule

    return topic_headers, student_headers, planner_details


def diff_months(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month
