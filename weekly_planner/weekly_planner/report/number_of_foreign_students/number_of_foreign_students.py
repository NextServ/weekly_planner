# Copyright (c) 2023, Servio and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	if not filters:
		filters={}

	columns = get_columns()
	data = get_filtered_data(filters)

	if not data:
		frappe.msgprint("No records found")
		# In case that no data is returned, swap the columns and data to retain chart
		return data, columns

	# This is the REQUIRED order or return empty array []
	# https://discuss.frappe.io/t/script-report-python-file-returns-advanced-use/33489/4
	# return columns, data, message, chart, report_summary
	return columns, data, None, None, None

def get_columns():
	return [
		{
			"fieldname": "campus_name",
			"label": "Campus",
			"fieldtype": "Data",
            # 'options': 'Campus'
			"width": 150
		},
		{
			"fieldname": "foreign_student",
			"label": "Foreign Student Count",
			"fieldtype": "Data",
		},

	]

def get_filtered_data(filters):
	filter = get_filters(filters)

	campus_list = frappe.get_all(
		doctype='Campus',
		# pluck='campus_name'
		fields=['campus_name'],
		filters=filter
	)

	program_enrollment_docs = frappe.get_all(
		doctype='Program Enrollment',
		fields=['name', 'campus', 'academic_year', 'student_category'],
		# filters=filter,
	)

	for campus in campus_list:
		# Initialize each campus' data.
		campus['foreign_student'] = 0

		for student in program_enrollment_docs:
			if student.campus == campus.campus_name:
				if student.student_category is not None and "Foreign" in student.student_category:
					campus['foreign_student'] += 1


	# breakpoint()
	return campus_list

def get_filters(filters):
	filter = [
		# {
		# 	"is_cancelled" : 0
		# }
	]
	for key, value in filters.items():
		if filters.get(key):
			filter.append({key: value})

	# Return a list/array of field objects with key value pair of name : query. 
	return filter
