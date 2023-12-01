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
			"fieldname": "name",
			"label": "Student Type",
			"fieldtype": "Data",
            # 'options': 'Program Enrollment'
			# "width": 150
		},
		{
			"fieldname": "count",
			"label": "Total Students",
			"fieldtype": "Data",
		},
		{
			"fieldname": "total",
			"label": "Total Amount",
			"fieldtype": "Currency",
            'options': 'currency',
			"width": 150
		},
	]

def get_filtered_data(filters):
	filter = get_filters(filters)

	student_type = [
		{
			"name": "New Students",
			"total": 0,
			"count": 0
		},
		{
			"name": "Old Students",
			"total": 0,
			"count": 0
		},
	]

	# Fees
	fees_docs = frappe.get_all(
		doctype='Fees',
		fields=['grand_total', 'program_enrollment']
	)

	program_enrollment_docs = frappe.get_all(
		doctype='Program Enrollment',
		fields=['name', 'enrollment_fees_method', 'fees_due_schedule_template', 'student_category'],
		# filters=filter,
	)

	def add_to_total(index, program_enrollment_name):
		for fees in fees_docs:
			if fees.program_enrollment == program_enrollment_name:
				student_type[index]['total'] += fees.grand_total

	# 0-New Students, 1-Old or any type of student
	for program_enrollment in program_enrollment_docs:
		# If the student_category is not null and theres "New" or "NS"
		if program_enrollment.student_category is not None and ("New" in program_enrollment.student_category or "NS" in program_enrollment.student_category):
			student_type[0]['count'] += 1
			add_to_total(0, program_enrollment.name)
		else:
			student_type[1]['count'] += 1
			add_to_total(1, program_enrollment.name)

	# breakpoint()

	return student_type

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
