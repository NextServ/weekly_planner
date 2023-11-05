// Copyright (c) 2023, Servio and contributors
// For license information, please see license.txt
frappe.ui.form.on("Monthly Behavioral Assessment", {
    onload(frm) {
        // Student field should only show students from the same instructor
        frm.set_query('student', () => {
            return {
                query: 'weekly_planner.doc_functions.get_students_from_instructor',
                filters: {
                    instructor: frm.doc.instructor
                }
            }
        });
    },
    
    refresh(frm) {
        // Retrieve instructor name from user
        frappe.call({
            method: "weekly_planner.doc_functions.get_instructor_name",
            args: {
                user_name: frappe.session.user
            },
            callback: function(data) {
                frm.set_value("instructor", data.message);
            }
        });
    },

   generate_lessons: function(frm) {
        frappe.msgprint("Generating Lessons");
    }
});
