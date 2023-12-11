# Copyright (c) 2023, Servio and contributors
# For license information, please see license.txt

import frappe
# from weekly_planner.utils import x


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
			"fieldname": "iee_amount",
			"label": "IEE Sales Amount",
			"fieldtype": "Currency",
            'options': 'currency',
		},
		{
			"fieldname": "iee_count",
			"label": "IEE Student Count",
			"fieldtype": "Data",
		},
		{
			"fieldname": "iee_average",
			"label": "IEE Average Tuition",
			"fieldtype": "Currency",
            'options': 'currency',
		},
		{
			"fieldname": "regular_amount",
			"label": "Regular Sales Amount",
			"fieldtype": "Currency",
            'options': 'currency',
		},
		{
			"fieldname": "regular_count",
			"label": "Regular Student Count",
			"fieldtype": "Data",
		},
		{
			"fieldname": "regular_average",
			"label": "Regular Average Tuition",
			"fieldtype": "Currency",
            'options': 'currency',
		},
		{
			"fieldname": "late_amount",
			"label": "Late Sales Amount",
			"fieldtype": "Currency",
            'options': 'currency',
		},
		{
			"fieldname": "late_count",
			"label": "Late Student Count",
			"fieldtype": "Data",
		},
		{
			"fieldname": "late_average",
			"label": "Late Average Tuition",
			"fieldtype": "Currency",
            'options': 'currency',
		},
		# {
		# 	"fieldname": "posting_date",
		# 	"label": "Posting Date",
		# 	"fieldtype": "Date",
		# 	# "width": 100
		# },
	]

def get_filtered_data(filters):
	filter = get_filters(filters)

	campus_list = frappe.get_all(
		doctype='Campus',
		# pluck='campus_name'
		fields=['campus_name'],
		filters=filter
	)

	# Fees
	fees_docs = frappe.get_all(
		doctype='Fees',
		fields=['grand_total', 'program_enrollment']
	)

	program_enrollment_docs = frappe.get_all(
		doctype='Program Enrollment',
		fields=['name', 'campus', 'academic_year', 'enrollment_fees_method', 'fees_due_schedule_template'],
		# filters=filter,
	)


	for campus in campus_list:
		# Initialize each campus' data.
		campus['iee_count'] = 0
		campus['iee_amount'] = 0
		campus['iee_average'] = 0

		campus['regular_count'] = 0
		campus['regular_amount'] = 0
		campus['regular_average'] = 0

		campus['late_count'] = 0
		campus['late_amount'] = 0
		campus['late_average'] = 0

		# campus['academic_year'] = ""

		for student in program_enrollment_docs:
			if student.campus == campus.campus_name:
				# If IEE / Incentivized Early Enrollment.
				if student.enrollment_fees_method == "Custom":
					for fees in fees_docs:
						if fees.program_enrollment == student.name:
							print(fees.grand_total)
							campus['iee_count'] += 1
							campus['iee_amount'] += fees.grand_total
				else:
					# Some data in has no 'fees_due_schedule_template', this is maybe due to test data but have a catch for that either way.
					if student.fees_due_schedule_template is not None and "Late" not in student.fees_due_schedule_template:
						for fees in fees_docs:
							if fees.program_enrollment == student.name:
								campus['regular_count'] += 1
								campus['regular_amount'] += fees.grand_total
					else:
						for fees in fees_docs:
							if fees.program_enrollment == student.name:
								campus['late_count'] += 1
								campus['late_amount'] += fees.grand_total

		# Set averages per campus
		# Some campus dont have students, atleast for this test.	
		campus['iee_average'] = 0 if campus['iee_count'] == 0 else campus['iee_amount'] / campus['iee_count']
		campus['regular_average'] = 0 if campus['regular_count'] == 0 else campus['regular_amount'] / campus['regular_count']
		campus['late_average'] = 0 if campus['late_count'] == 0 else campus['late_amount'] / campus['late_count']

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
