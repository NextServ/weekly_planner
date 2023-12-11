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
		# {
		# 	"fieldname": "name",
		# 	"label": "name",
		# 	"fieldtype": "Data",
        #     # 'options': 'Campus'
		# 	"width": 150
		# },
		{
			"fieldname": "payment_mode",
			"label": "Payment Modes",
			"fieldtype": "Data",
            # 'options': 'Campus'
		},
		{
			"fieldname": "count",
			"label": "Enrolled Count",
			"fieldtype": "Data",
            # 'options': 'Campus'
			"width": 150
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

	payment_modes = [
		{
			"payment_mode": "Incentivized Early Enrollment",
			"total": 0,
			"count": 0
		},
		{
			"payment_mode": "Semi-Annual",
			"total": 0,
			"count": 0
		},
		{
			"payment_mode": "Annual",
			"total": 0,
			"count": 0
		},
		{
			"payment_mode": "Quarterly",
			"total": 0,
			"count": 0
		},
		{
			"payment_mode": "Monthly",
			"total": 0,
			"count": 0
		}
	]

	# Fees
	fees_docs = frappe.get_all(
		doctype='Fees',
		fields=['grand_total', 'program_enrollment']
	)

	program_enrollment_docs = frappe.get_all(
		doctype='Program Enrollment',
		fields=['name', 'enrollment_fees_method', 'fees_due_schedule_template'],
		# filters=filter,
	)

	def add_to_total(index, program_enrollment_name):
		for fees in fees_docs:
			if fees.program_enrollment == program_enrollment_name:
				payment_modes[index]['total'] += fees.grand_total

	# 0-IEE, 1-Semi-Annual, 2-Annual, 3-Quarterly, 4-Monthly
	for program_enrollment in program_enrollment_docs:
		# If theres no Fees Due Schedule Template set, this is automatically early enrollment.
		if program_enrollment.fees_due_schedule_template is None:
			payment_modes[0]['count'] += 1
			add_to_total(0, program_enrollment.name)
		elif "Semi-Annual" in program_enrollment.fees_due_schedule_template:
			payment_modes[1]['count'] += 1
			add_to_total(1, program_enrollment.name)
		elif "Annual" in program_enrollment.fees_due_schedule_template:
			payment_modes[2]['count'] += 1
			add_to_total(2, program_enrollment.name)
		elif "Quarterly" in program_enrollment.fees_due_schedule_template:
			payment_modes[3]['count'] += 1
			add_to_total(3, program_enrollment.name)
		elif "Monthly" in program_enrollment.fees_due_schedule_template:
			payment_modes[4]['count'] += 1
			add_to_total(4, program_enrollment.name)

	# breakpoint()

	return payment_modes

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
