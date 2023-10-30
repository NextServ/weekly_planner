// Copyright (c) 2023, Servio and contributors
// For license information, please see license.txt

frappe.ui.form.on("Monthly Behavioral Assessment", {
	refresh(frm) {

	},
    
    generate_lessons: function(frm) {
        frappe.msgprint("Generating Lessons");
    }
});
