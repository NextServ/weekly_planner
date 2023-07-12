// Copyright (c) 2023, Servio and contributors
// For license information, please see license.txt

frappe.ui.form.on('Weekly Planner', {
	refresh: function(frm) {
        frm.set_query("topic", "lessons", function() {
            return {
                "filters": {
                    "name": ["in", frm.doc.topics.map(row => row.topic)]
                }
            };
        });

        frm.set_query("student", "lessons", function() {
            return {
                "filters": {
                    "name": ["in", frm.doc.students.map(row => row.student)]
                }
            };
        });


        frm.add_custom_button(__('View Planner Detail'), function() {
            window.open(`/planner-detail?planner-name=${frm.doc.name}`, "_blank")
        });
	}
});
