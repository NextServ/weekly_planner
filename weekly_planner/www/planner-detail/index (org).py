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

    # Load planner details
    context.student_headers = []
    context.lessons = {}
    if not context.invalid_role:
        context.student_headers, context.lessons, context.empty_planner = load_lessons(planner_name)

    return context


def load_lessons(planner_name):
    # First load all students from Planner Detail
    students = frappe.get_all("Planner Student", filters={"parent": planner_name}, fields=["*"])
    topics = frappe.get_all("Planner Topic", filters={"parent": planner_name}, fields=["*"])
    entries = frappe.get_all("Planner Lesson", filters={"parent": planner_name}, fields=["*"])

    # Create a dictionary of lessons
    lessons = {}
    student_headers = []
    empty_planner = len(students) + len(topics)

    # Load up the columns
    for student in students:
        if student.student not in student_headers:
            student_headers.append({"student": student.student})

    # Go through each entry and figure out which cell to stick it in
    entry_num = -1
    topics_added =""
    for entry in entries:
        entry_num += 1

        # Create placeholder string
        placeholder = "# | " * len(students)
        placeholder = placeholder[:-3]  # Remove last " | "

        # Get the student and topic
        for topic in topics:
            topics_added = topics_added + topic.topic + " | "
            if topic.topic not in topics_added:
                placeholder = topic.topic + " | " + placeholder
            
            if entry.topic == topic.topic:
                break
        
        col = 0
        for student in students:
            col += 1
            if entry.student == student.student:
                placeholder = nth_repl(placeholder, "#",  entry.lesson_status[0].upper() + " " + entry.date.strftime("%b-%d"), col)
                break
        
        # parse placeholder into a list using " | " as a delimiter
        lessons = parse_into_keys(placeholder)

    return student_headers, lessons, empty_planner


def nth_repl(s, sub, repl, n):
    find = s.find(sub)
    # If find is not -1 we have found at least one match for the substring
    i = find != -1
    # loop util we find the nth or we find no match
    while find != -1 and i != n:
        # find + 1 means we start searching from after the last match
        find = s.find(sub, find + 1)
        i += 1
    # If i is equal to n we found nth match so replace
    if i == n:
        return s[:find] + repl + s[find+len(sub):]
    return s

def parse_into_keys(placeholder):
    # placeholder = "0: 'Snake Addition Game 1 | F Aug-01 | #', 1: 'Large Motor Control | # | F Aug-01'"
    # parse placeholder into a list using " | " as a delimiter
    keys = ""
    num_rec = 0

    while True:
        if placeholder.find(":") == -1:
            break

        # Get the row #, it's always the first field
        keys = keys + "{" + placeholder[placeholder.find(":") -1] + ", "
        
        # Get the topic
        n1:int = placeholder.index("'")
        n2:int = placeholder.index(" |")
        keys = keys + placeholder[n1: n2] + "', "

        # Truncate placeholder to remove the row # and topic
        placeholder = placeholder[n2 + 3:]

        # Loop through the remainder until you reach another ":"
        while placeholder.index(" |") != "":
            # Get the next lesson
            n1 = 0
            n2 = placeholder.index(" |")
            lesson = placeholder[n1: n2]
            lesson = "''" if lesson == "#" else "'" + lesson + "'"
            keys = keys + lesson  + ", "

            # Truncate placeholder to remove the last lesson
            placeholder = placeholder[n2 + 3:]

            # If the next character is a "'", we are done with this row
            if placeholder[0] == "'":
                # Replace last "," with a "}, "
                keys = keys[:-2] + "}, "
                break     

    return keys