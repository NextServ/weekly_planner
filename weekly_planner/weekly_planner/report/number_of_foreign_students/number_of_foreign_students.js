// Copyright (c) 2023, Servio and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Number of Foreign Students"] = {
	"filters": [
		{
			"fieldname": "campus_name",
			"label": "Campus",
			"fieldtype": "Link",
            'options': 'Campus'
		},
	]
};
