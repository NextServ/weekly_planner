import frappe

def monthly_behavioral_assessment_query(user):
    if not user:
        user = frappe.session.user

    # Print for Testing
    # print("============================")
    # print(frappe.get_roles(user))
    # print("============================")
    # breakpoint()

    employee_code = frappe.db.sql("""SELECT name 
                                  FROM `tabEmployee` 
                                  WHERE user_id=%s""", (user), as_dict=True)

    if employee_code:
        # If there's any "Head of School" in the role, save process time and return without filter. (all)
        if any("Head of School" in role for role in frappe.get_roles(user)):
            return
        
        # If there's a "Head Instructor" return everything you own and every instructor's doc that reports to you.
        elif any("Head Instructor" in role for role in frappe.get_roles(user)):
            reports_to = frappe.db.sql("""SELECT A.employee_name 
                               FROM `tabEmployee` A 
                               LEFT JOIN `tabInstructor` B 
                               ON A.name = B.employee 
                               WHERE A.reports_to = %s""", (employee_code[0].name),as_dict=True)

            # Initialize empty string to store who report to the current user
            reports_to_list = []
            for item in reports_to:
                reports_to_list.append(item.employee_name)

            format_strings = ','.join('"{0}"'.format(instructor) for instructor in reports_to_list)
            return "(`tabMonthly Behavioral Assessment`.owner = {user} OR `tabMonthly Behavioral Assessment`.instructor IN ({reports_to}))".format(user=frappe.db.escape(user), reports_to = format_strings)

    # If you're an instructor/don't or not an employee, return everything you own instead.
    # Catch all.
    return "(`tabMonthly Behavioral Assessment`.owner = {user})".format(user=frappe.db.escape(user))