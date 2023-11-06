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