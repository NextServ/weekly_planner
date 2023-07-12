# weekly_planner details
import frappe
from datetime import date
import webbrowser

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

    return context


def load_planner_details(planner_name):
    # First load all students from Planner Detail
    students = frappe.db.sql('''SELECT p.student, s.first_name, s.last_name, s.date_of_birth
                             FROM `tabPlanner Student` p INNER JOIN `tabStudent` s
                             ON p.student = s.name
                             WHERE p.parent = %(p_name)s''', {"format": "%Y%m", "p_name": planner_name}, as_dict=True)

    topics = frappe.get_all("Planner Topic", filters={"parent": planner_name}, fields=["*"])
    lessons = frappe.get_all("Planner Lesson", filters={"parent": planner_name}, fields=["*"])

    # planner_details = [["" for row in range(num_students)] for col in range(num_topics)]
    planner_details = {}
    student_headers = {}
    topic_headers = []
    working_dict =  {}

    # Load up the columns
    for student in students:
        if student.student not in student_headers:

            # Calculate age in years and months
            years = int(diff_months(date.today(), student.date_of_birth) / 12)
            months = years % 12

            # working_dict = "{'student': '" + student.student + "', 'first_name': '" + student.first_name + "', 'last_name': '" + student.last_name + "', "
            # working_dict = working_dict + "'years_old': '" + str(years) + "', 'months_old': '" + str(months) + "'}"
            working_dict = {
                "student": student.student,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "years_old": years,
                "months_old": months
            }

            student_headers[student.student] = working_dict

    # Load up the rows
    for topic in topics:
        if not topic.topic in topic_headers:
            topic_headers.append(topic.topic)
            planner_details[topic.topic] = {}
            r = -1
            c = -1
            for col_header in student_headers:
                r += 1
                c += 1
                # lesson = [entry for entry in lessons if entry["topic"] == topic.topic and \
                #     entry["student"] == col_header["student"]]
                for entry in lessons:
                    if entry["topic"] == topic.topic and entry["student"] == col_header["student"]:
                        lesson = entry
                        break
                    else:
                        lesson = ""

                planner_details[topic.topic][col_header["student"]] = lesson

    return topic_headers, student_headers, planner_details


def diff_months(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month