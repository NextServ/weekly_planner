// Copyright (c) 2023, Servio and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lesson Status', {
	before_save: function(frm) {
		// Locate the previous record marked as Default
		frappe.db.get_value('Lesson Status', {'is_default': 1}, 'name', function(r) {
			// If found, unmark it
			if (r.name) {
				frappe.db.set_value('Lesson Status', r.name, 'is_default', 0);
			}
		});
	}
});