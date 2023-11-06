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

    sql =  '''SELECT student, student_name FROM `tabStudent Group Student` '''
    sql += '''WHERE (parent IN (SELECT parent FROM `tabStudent Group Instructor` WHERE instructor_name = %(instructor)s)) '''
    sql += '''AND (%(searchfield)s LIKE %(txt)s OR name LIKE %(txt)s)''' if txt else ''' '''
    sql += '''ORDER BY student_name '''
    sql += '''LIMIT %(page_len)s ''' if page_len else ''' '''
    sql += '''OFFSET %(start)s''' if start else ''' '''

    
    print('\nsql: ', sql)

    return frappe.db.sql(sql, ({'instructor': filters.get('instructor'), 'searchfield': searchfield, \
                                'txt': txt, 'page_len': page_len, 'start': start}))