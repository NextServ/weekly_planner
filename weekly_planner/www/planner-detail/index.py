# weekly_planner details
import frappe
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

    topic_headers, student_headers, planner_details = load_planner_details(planner_name)
    context.topic_headers = topic_headers
    context.planner_details = planner_details
    context.student_headers = student_headers
    context.empty_planner = len(context.student_headers) + len(context.topic_headers) + len(context.planner_details)

    return context


def load_planner_details(planner_name):
    # First load all students from Planner Detail
    students = frappe.get_all("Planner Student", filters={"parent": planner_name}, fields=["*"])
    topics = frappe.get_all("Planner Topic", filters={"parent": planner_name}, fields=["*"])
    entries = frappe.get_all("Planner Lesson", filters={"parent": planner_name}, fields=["*"])
    # Build a array with number of columns equal to number of students and rows equal to number of topics
    num_students = len(students) + 1
    num_topics = len(topics)
    # planner_details = [["" for row in range(num_students)] for col in range(num_topics)]
    planner_details = {}
    student_headers = []
    topic_headers = []
    # Load up the columns
    for student in students:
        if student.student not in student_headers:
            student_headers.append(student.student)
    # Load up the rows
    row = -1
    for topic in topics:
        if not topic.topic in topic_headers:
            topic_headers.append(topic.topic)
            planner_details[topic.topic] = {}
            for col_header in student_headers:
                topic_schedule = [item for item in entries if item["topic"] == topic.topic and item["student"] == col_header]
                planner_details[topic.topic][col_header] = topic_schedule


    return topic_headers, student_headers, planner_details