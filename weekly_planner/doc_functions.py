import frappe

# Retrieve instructor name based on user name
@frappe.whitelist()
def get_instructor_name(user_name):
    employee = frappe.get_doc('Employee', {'user_id': user_name})
    instructor = frappe.get_doc('Instructor', {'employee': employee.name})
    return instructor.instructor_name


# Student Query in Monthly Behavioral Assessment
@frappe.whitelist()
def get_students_from_instructor(doctype, txt, searchfield, start, page_len, filters):
    print('*** get_students_from_instructor ***\ninstructor: ', filters['instructor'], '\nsearchfield: ', searchfield)

    sql =  '''SELECT student_name FROM `tabStudent Group Student` '''
    sql += '''WHERE (parent IN (SELECT parent FROM `tabStudent Group Instructor` WHERE instructor_name = %(instructor)s)) '''
    sql += '''AND (%(searchfield)s LIKE %(txt)s OR name LIKE %(txt)s)''' if txt else ''' '''
    sql += '''ORDER BY student_name '''
    sql += '''LIMIT %(page_len)s ''' if page_len else ''' '''
    sql += '''OFFSET %(start)s''' if start else ''' '''

    
    print('\nsql: ', sql)

    return frappe.db.sql(sql, ({'instructor': filters['instructor'], 'searchfield': searchfield, \
                                'txt': txt, 'page_len': page_len, 'start': start}), as_dict=True)


# Get Student Group from Student
@frappe.whitelist()
def get_student_group(student):
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

    assessment = frappe.get_doc('Monthly Behavioral Assessment', doc_name)
    lessons = frappe.db.sql(sql, ({'student': student, 'year': year, 'month': month}), as_dict=True)

    for lesson in lessons:
        assessment.append('learning_areas', {'date': lesson.date, 'topic': lesson.topic, 'course': lesson.course})

    assessment.save()