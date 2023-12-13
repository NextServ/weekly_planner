import frappe

# Retrieve instructor name based on user name
@frappe.whitelist()
def get_instructor_name(user_name):
    employee = frappe.get_doc('Employee', {'user_id': user_name})
    instructor = frappe.get_doc('Instructor', {'employee': employee.name})
    return instructor.instructor_name


# Student Query in Monthly Behavioral Assessment
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_students_from_instructor(doctype, txt, searchfield, start, page_len, filters):
    print('*** get_students_from_instructor ***\ninstructor: ', filters['instructor'], '\nsearchfield: ', searchfield)
    
    searchfields = frappe.get_meta("Student").get_search_fields()
    searchfields = " or ".join("s." + field + " like %(txt)s" for field in searchfields)

    sql =  """
        SELECT 
            sgs.student, sgs.student_name 
        FROM `tabStudent Group Student` sgs 
        INNER JOIN `tabStudent` s
            on s.name = sgs.student
        WHERE 
            (sgs.parent IN (SELECT parent FROM `tabStudent Group Instructor` WHERE instructor_name = %(instructor)s)) 
            AND (sgs.student LIKE %(txt)s OR sgs.student_name LIKE %(txt)s OR ({scond}))            
        ORDER BY sgs.student_name
        LIMIT %(start)s, %(page_len)s
    """.format(scond=searchfields)

    print('\nsql: ', sql)

    return frappe.db.sql(sql, ({'instructor': filters.get('instructor'), \
                                'txt': '%' + txt + '%', 'page_len': page_len, 'start': start}))


# Get Student Group from Student
@frappe.whitelist()
def get_student_group(student):
    # Check if student is empty
    if not student:
        return None
    
    sql =  '''SELECT parent FROM `tabStudent Group Student` '''
    sql += '''WHERE (student = %(student)s) LIMIT 1'''

    student_group = frappe.db.sql(sql, ({'student': student}))
    print('*** get_student_group ***\nstudent: ', student, '\nstudent_group: ', student_group)

    return student_group[0]


# Populate Learning Areas in Monthly Behavioral Assessment
@frappe.whitelist()
def generate_lesson_areas(doc_name, student, year, month):
    sql =  '''SELECT date, l.topic, c.parent 'course', student FROM `tabPlanner Lesson` l '''
    sql += '''INNER JOIN `tabCourse Topic` c ON c.topic = l.topic '''
    sql += '''WHERE (student = %(student)s) AND (YEAR(date) = %(year)s) AND (MONTHNAME(date) = %(month)s) '''
    sql += '''ORDER BY course ASC '''

    assessment = frappe.get_doc('Monthly Behavioral Assessment', doc_name)
    lessons = frappe.db.sql(sql, ({'student': student, 'year': year, 'month': month}), as_dict=True)

    # Delete the items first and then append the new ones
    # This is to avoid duplications
    for learning_area in assessment.learning_areas:
        learning_area.delete()

    for lesson in lessons:
        assessment.append('learning_areas', {'date': lesson.date, 'topic': lesson.topic, 'course': lesson.course})

    assessment.save()


# Delete Learning Areas in Monthly Behavioral Assessment
@frappe.whitelist()
def delete_learning_areas(doc_name, assess_month):
    assessment = frappe.get_doc('Monthly Behavioral Assessment', doc_name)

    for learning_area in assessment.learning_areas:
        learning_area.delete()

    assessment.assess_month = assess_month
    assessment.save()
