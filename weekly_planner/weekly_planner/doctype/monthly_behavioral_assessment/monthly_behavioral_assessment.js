// Copyright (c) 2023, Servio and contributors
// For license information, please see license.txt
frappe.ui.form.on("Monthly Behavioral Assessment", {
    onload(frm) {
        // Student field should only show students from the same instructor
        // frm.set_query('student', () => {
        //     return {
        //         query: 'weekly_planner.doc_functions.get_students_from_instructor',
        //         filters: {
        //             instructor: frm.doc.instructor
        //         }
        //     }
        // });
    },
    
    refresh(frm) {
        // Retrieve instructor name from user
        if (frm.is_new()) {
            frappe.call({
                method: "weekly_planner.doc_functions.get_instructor_name",
                args: {
                    user_name: frappe.session.user
                },
                callback: function(data) {
                    frm.set_value("instructor", data.message);
                }
            });

            // Default Year and Month to current month name  and year
            year = new Date().getFullYear();
            month = new Date().toLocaleString('default', { month: 'long' });

            frm.set_value("year", year);
            frm.set_value("month", month);
        }

        frm.toggle_display(['learning_areas', 'generate_lessons', 'student_group'], !frm.is_new());
        sg = frm.get_field('student_group');
        sg.$input.prop('readonly', true);

        if (!frm.doc.student_group) {
            frm.trigger('before_save');
            frm.save();
        }
    },

    before_save(frm) {
        // Retrieve Student Group from Student
        frappe.call({
            method: "weekly_planner.doc_functions.get_student_group",
            args: {
                student: frm.doc.student
            },
            callback: function(data) {
                // Convert data.message to string
                data.message = data.message.toString();
                frm.set_value("student_group", data.message);
            }
        });
    
    },

    generate_lessons: function(frm) {
        if (frm.is_dirty()) {
            frappe.throw(__("Please save the document before generating lessons."));
            return;
        }

        frappe.call({
            method: "weekly_planner.doc_functions.generate_lesson_areas",
            args: {
                doc_name: frm.doc.name,
                student: frm.doc.student,
                month: frm.doc.month,
                year: frm.doc.year
            },
            callback: function(data) {
                frm.reload_doc();
            }
        });
    }
});
