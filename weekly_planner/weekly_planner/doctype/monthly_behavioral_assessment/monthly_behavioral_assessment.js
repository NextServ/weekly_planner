// Copyright (c) 2023, Servio and contributors
// For license information, please see license.txt
frappe.ui.form.on("Monthly Behavioral Assessment", {
    onload(frm) {
        if (!frm.doc.instructor) return;

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
        if (frm.is_new()) {
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

            // Default Year and Month to current month name  and year
            year = new Date().getFullYear();
            month = new Date().toLocaleString('default', { month: 'long' });

            frm.set_value("assess_year", year);
            frm.set_value("assess_month", month);
        } else {
            // Prevent any changes after saving to preserve document name and the integrity of the learning areas generated
            let inst = frm.get_field('instructor');
            let st = frm.get_field('student');
            let yr = frm.get_field('assess_year');
            let mo = frm.get_field('assess_month');
            inst.$input.prop('readonly', true);
            st.$input.prop('readonly', true);
            yr.$input.prop('readonly', true);
            mo.$input.prop('readonly', true);
        }
        
        frm.toggle_display(['learning_areas', 'generate_lessons', 'student_group'], !frm.is_new());
        let sg = frm.get_field('student_group');
        sg.$input.prop('readonly', true);

        if (!frm.doc.student_group) {
            frm.trigger('before_save');
            frm.save();
        }
    },

    before_save(frm) {
        if (!frm.doc.student) return;
        
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

    assess_month: function(frm) {
        // Warn that changing the month will delete all learning areas
        if (frm.is_new() || !frm.is_dirty()) return;

        // Preserve the new month value
        new_month = frm.doc.assess_month;

        frappe.confirm(
            'Changing the month will delete all learning areas. Are you sure you want to continue?',
            () => {

                frappe.call({
                    method: "weekly_planner.doc_functions.delete_learning_areas",
                    args: {
                        doc_name: frm.doc.name,
                        assess_month: new_month
                    },
                    callback: function(data) {
                        frm.reload_doc();
                    }
                });
                
                frm.set_value("assess_month", new_month);
            },
            () => {
                frm.set_value("assess_month", frm.doc.month);
            }
        );
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
                month: frm.doc.assess_month,
                year: frm.doc.assess_year
            },
            callback: function(data) {
                frm.reload_doc();
            }
        });
    }
});
