// Copyright (c) 2023, Servio and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales by Enrollment Phase"] = {
	"filters": [
		{
			"fieldname": "campus_name",
			"label": "Campus",
			"fieldtype": "Link",
            'options': 'Campus'
		},
	]
};
