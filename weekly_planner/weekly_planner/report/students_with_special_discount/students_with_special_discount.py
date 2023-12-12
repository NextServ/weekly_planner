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
            'options': 'Campus',
			"width": 150
		},
		{
			"fieldname": "discount_100",
			"label": "Special Discount 100%",
			"fieldtype": "Data",
		},
		{
			"fieldname": "discount_50",
			"label": "Special Discount 50%",
			"fieldtype": "Data",
		},
		{
			"fieldname": "discount_25",
			"label": "Special Discount 25%",
			"fieldtype": "Data",
		},
		{
			"fieldname": "discount_25_segbag",
			"label": "Special Discount 25% SegBag",
			"fieldtype": "Data",
		},
		{
			"fieldname": "discount_20",
			"label": "Special Discount 20%",
			"fieldtype": "Data",
		},
		{
			"fieldname": "discount_10",
			"label": "Special Discount 10%",
			"fieldtype": "Data",
		},
		{
			"fieldname": "discount_5",
			"label": "Special Discount 5%",
			"fieldtype": "Data",
		},
		{
			"fieldname": "sibling_discount",
			"label": "Sibling Discount",
			"fieldtype": "Data",
		},
		{
			"fieldname": "old_student",
			"label": "Old Student",
			"fieldtype": "Data",
		},
		{
			"fieldname": "new_student",
			"label": "New Student",
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

	fees_docs = frappe.get_all(
		doctype='Fees',
		fields=['name', 'grand_total', 'program_enrollment']
	)

	fees_components_docs = frappe.get_all(
		doctype='Fee Component',
		fields=['parent', 'fees_category'],
		filters=[
			{
				# Check if Special Discount is in fees_category to save up time
				# Discount includes sibling discount which is a lot
				# 'fees_category' : ['like', '%Special Discount%']
				'fees_category' : ['like', '%Discount%']
			}
		]
	)

	def check_discount (campus, student):
		# print(campus)
		for fee in fees_docs:
			if fee.program_enrollment == student:
				for fee_component in fees_components_docs:
					if fee_component.parent == fee.name:
						if fee_component.fees_category == "Special Discount 100%":
							campus['discount_100'] += 1
						elif fee_component.fees_category == "Special Discount 50%":
							campus['discount_50'] += 1
						elif fee_component.fees_category == "Special Discount 25%":
							campus['discount_25'] += 1
						elif fee_component.fees_category == "Special Discount 25% SegBag":
							campus['discount_25_segbag'] += 1
						elif fee_component.fees_category == "Special Discount 20%":
							campus['discount_20'] += 1
						elif fee_component.fees_category == "Special Discount 10%":
							campus['discount_10'] += 1
						elif fee_component.fees_category == "Sibling Discount":
							campus['sibling_discount'] += 1

	for campus in campus_list:
		# Initialize each campus' data.
		campus['discount_100'] = 0
		campus['discount_50'] = 0
		campus['discount_25'] = 0
		campus['discount_25_segbag'] = 0
		campus['discount_20'] = 0
		campus['discount_10'] = 0
		campus['discount_5'] = 0
		campus['sibling_discount'] = 0
		campus['old_student'] = 0
		campus['new_student'] = 0

		for student in program_enrollment_docs:
			if student.campus == campus.campus_name:
				if student.student_category is not None and ("New" in student.student_category or "NS" in student.student_category):
					campus['new_student'] += 1
					check_discount(campus, student.name)
				else:
					campus['old_student'] += 1
					check_discount(campus, student.name)

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
