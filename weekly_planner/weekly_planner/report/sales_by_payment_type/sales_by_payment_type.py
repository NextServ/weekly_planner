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
			"label": "Payment Name",
			"fieldtype": "Link",
            'options': 'DragonPay Payment Request',
			"width": 150
		},
		{
			# This options to party_type since it's a dynamic link, meaning it will link to whatever the party_type is (Customer/Student doctype)
			"fieldname": "party",
			"label": "Party",
			"fieldtype": "Dynamic Link",
            'options': 'party_type',
			"width": 150
		},
		{
			"fieldname": "mobile_no",
			"label": "Mobile Number",
			"fieldtype": "Data",
			'options': 'Phone',
		},
		{
			"fieldname": "mode",
			"label": "Payment Type",
			"fieldtype": "Data",
		},
		{
			"fieldname": "long_name",
			"label": "Payment Method",
			"fieldtype": "Data",
		},
		{
			"fieldname": "collection_request_status",
			"label": "Collection Request Status",
			"fieldtype": "Data",
		},
		{
			"fieldname": "applied_amount",
			"label": "Applied Amount",
			"fieldtype": "Currency",
            'options': 'currency',
		},
		{
			"fieldname": "payment_method_charge_amount",
			"label": "Payment Method Charge Amount",
			"fieldtype": "Currency",
            'options': 'currency',
		},
		{
			"fieldname": "amount",
			"label": "Amount",
			"fieldtype": "Currency",
            'options': 'currency',
			"width": 150
		},
	]

def get_filtered_data(filters):
	filter = get_filters(filters)

	filtered_data = frappe.get_all(
		doctype='DragonPay Payment Request',
		fields=['name', 'party_type', 'party', 'mobile_no', 'mode', 'long_name', 'collection_request_status', 'applied_amount', 'payment_method_charge_amount', 'amount'],
		filters=filter,
		# or_filters=[
		# 	["account", "=", "2023-Gada Electronics-Income"],
		# 	["account", "=", "2023-Gada Electronics-Expense"],
		# ]
	)

	# Process the mode
	# 1=online banking
	# 2=over the counter
	for data in filtered_data:
		if data['mode'] == 1:
			data['mode']='Online Banking'
		elif data['mode'] == 2:
			data['mode']='Over the Counter'

	# breakpoint()

	return filtered_data

def get_filters(filters):
	filter = [
		# Ignore the mode 0
		{
			"mode" : ["!=", "0"]
		}
	]
	for key, value in filters.items():
		if filters.get(key):
			filter.append({key: value})

	# Return a list/array of field objects with key value pair of name : query. 
	return filter