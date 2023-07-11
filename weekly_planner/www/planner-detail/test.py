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
    is_head_instructor = "Head Instructor" in cur_roles
    is_instructor = "Instructor" in cur_roles

    for role in cur_roles:
        if role in acceptable_roles:
            context.invalid_role = False
            break

    # Get planner_name from url parameter
    planner_name = frappe.form_dict.get("planner-name")
    
    # Remove %20 from planner_name
    if planner_name:    
        planner_name = planner_name.replace("%20", " ")

    # Load planner details
    context.planner_heading = []
    context.planner_details = []
    if not context.invalid_role:
        context.planner_heading, context.planner_details = load_planner_details(planner_name)

    return context


def load_planner_details(planner_name):
    # First load all students from Planner Detail
    students = frappe.get_all("Planner Student", filters={"parent": planner_name})
    topics = frappe.get_all("Planner Topic", filters={"parent": planner_name})
    entries = frappe.get_all("Planner Lesson", filters={"parent": planner_name}, fields=["*"])

    # Build a array with number of columns equal to number of students and rows equal to number of topics
    num_students = len(students) + 1
    num_topics = len(topics)
    planner_details = [["" for row in range(num_students)] for col in range(num_topics)]
    planner_heading = []
    
    # Load up the columns
    for student in students:
        planner_heading.append(student.student)

    # Load up the rows
    row = -1
    for topic in topics:
        row += 1
        planner_details[row][0] = ["topic: '" + str(topic.topic) + "'"]

    # Load up the entries
    for entry in entries:
        # Find the row
        row = 0
        for topic in topics:
            row += 1
            if topic.topic == entry.topic:
                break

        # Find the column
        col = 0
        for student in students:
            col += 1
            if student.student == entry.student:
                break

        planner_details[row][col] = "lesson: '" + str(entry.lesson) + "'"

    return planner_heading, planner_details
