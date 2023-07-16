frappe.ready(function() {
    // $('#items_table').DataTable();
    const table = new DataTable('#items_table');

    $('#modal_add_topics').on('show.bs.modal', function (e) {
        // alert("modal shown");
        show_topics(e);
    })

    // Listen for the click on the body of the table
    table.on('click', 'td', function (e) {
        // Get the cell data clicked on
        row = table.row(this).data()
        cell = table.cell(this).data()

        show_lesson_modal(row, cell);
    })
})


function getQueryVariable(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    
    for (var i=0;i<vars.length;i++) {
      var pair = vars[i].split("=");
      if (pair[0] == variable) {
        return pair[1];
      }
    } 
    alert('Query Variable ' + variable + ' not found');
}


function go_to_main() {
    // Go back to the main page
    window.open("/weekly-planner", "_self");
}


function delete_planner(e) {
    planner_name = getQueryVariable("planner-name");
    // alert(planner_name)

    // Delete the planner
    frappe.call({
        method: "weekly_planner.www.planner-detail.planner_actions.delete_planner",
        args: {
            "planner_name": planner_name
        },

        callback: function(r) {
            if (r.message == "success") {
                // Go back to the main page
                window.open("/weekly-planner", "_self");
            } else {
                alert("Error deleting planner");
            }
        }
    });
}


function show_students(e) {
    clear_students_table();

    // Retrieve students from Frappe
    frappe.call({
        method: "weekly_planner.www.planner-detail.planner_actions.get_students_for_selection",
        args: {
            "selected_campus": document.getElementById("selected_campus").value,
            "selected_group": document.getElementById("selected_group").value,
        },

        callback: function(students) {
            if (students.message) {
                var lesson_body = document.getElementById("students_table");

                // Show the students tableClass 1
                lesson_body.innerHTML = "";

                // Build the lesson_body with columns student, campus and group using the dataset returned from get_students_for_selection method
                var lesson_body_html = '<thead><tr><th>First Name</th><th>Last Name</th><th>DOB</th></tr></thead><tbody>';
                
                students.message.forEach((student) => {
                    lesson_body_html += '<tr><td>' + student.first_name + '</td><td>' + student.last_name + '</td><td>' + 
                        student.date_of_birth + '</td></tr>';
                });
                lesson_body_html += '</tbody>';

                // Add the table to the page
                lesson_body.innerHTML = lesson_body_html;

                // todo: Adjust modal in case the table is too big
                // myModal.handleUpdate()
                
                
                const table = new DataTable('#students_table');                

                table.on('click', 'tbody tr', function (e) {
                    e.currentTarget.classList.toggle('selected');
                });
                
                document.querySelector('#clear_button').addEventListener('click', function () {
                    // todo: fix this
                    table.rows('.selected').nodes().each((row) => row.classList.toggle('selected'));
                });

                // Add selected students to the planner
                document.querySelector('#add_button').addEventListener('click', function () {
                    // Get the selected students
                    var selected_students = table.rows('.selected').data();

                    // Output to console.log details of each student in selected_students
                    selected_students.forEach((student) => {
                        console.log(student);
                    });

                    // Add the selected students to the planner
                    // frappe.call({
                    //     method: "weekly_planner.www.planner-detail.planner_actions.add_students",
                    //     args: {
                    //         "selected_students": selected_students,
                    //         "planner_name": planner_name
                    //     },

                    //     return: function(r) {
                    //         if (!r.exc) {
                    //             // Go back to the main page
                    //             reload_items_table();
                    //         } else {
                    //             frappe.show_alert(
                    //                 {
                    //                     message: __("Error loading students!"),
                    //                     indicator: "red",
                    //                 },
                    //                 3
                    //             );
                    //         }
                    //     }
                    // });
                });
            }
        }
    });
}


function clear_students_table() {
    // Check to see if students_table already has rows; if it does, delete all rows
    var lesson_body = document.getElementById("students_table");
    
    // Clear the sudent_table if there are rows in it
    if (lesson_body.rows.length > 0) {
        // Clear the table
        lesson_body.innerHTML = "";

        var table = DataTable('#students_table')
        table.empty();
    }
    
}


function reload_items_table() {
    // Refresh the items table
    var container = document.getElementById("items_table");
    var content = container.innerHTML;
    container.innerHTML= content; 
}


function show_topics(e) {
    // Retrieve topics from Frappe
    planner_name = getQueryVariable("planner-name");
    planner_name = planner_name.replace("%20", " ");  // remove %20s

    frappe.call({
        method: "weekly_planner.www.planner-detail.planner_actions.get_topics_for_selection",
        args: {
            "planner_name": planner_name
        },

        callback: function(topics) {
            if (topics.message) {
                var topics_table = document.getElementById("topics_table");

                // Show the topics table
                topics_table.innerHTML = "";

                // Build the topics_table with columns topic, campus and group using the dataset returned from get_topics method
                var topics_table_html = '<thead><tr><th>Topic</th></tr></thead><tbody>';
                
                topics.message.forEach((topic) => {
                    topics_table_html += '<tr><td>' + topic.topic_name + '</td></tr>';
                });
                topics_table_html += '</tbody>';

                // Add the table to the page
                topics_table.innerHTML = topics_table_html;
                const table = new DataTable('#topics_table');                

                table.on('click', 'tbody tr', function (e) {
                    e.currentTarget.classList.toggle('selected');
                });
                
                document.querySelector('#clear_button').addEventListener('click', function () {
                })
            }
        }
    });
}


function show_lesson_modal(row, cell) {
    // Parse row and cell to get field values
    var center_pos = cell.indexOf("center") + 8;
    var status_len = 0;
    var student_pos = cell.indexOf("student:") + 9;
    var student_len = cell.indexOf(" |", student_pos);
    var lesson_pos = cell.indexOf("name:") + 6;
    var lesson_len = cell.indexOf(" |", lesson_pos);

    // Go through each char of cell to find the a character that is not a space 
    // and use that as the start of the status_abbr
    var status_abbr = "";
    var valid_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    for (var i = center_pos; i < student_pos; i++) {
        if (valid_letters.search(cell[i]) > 0) {
            status_len = cell.indexOf(" ", i)
            status_abbr = cell.substring(i, status_len);
            break;
        }
    }

    // Values to be saved later
    var planner_name = getQueryVariable("planner-name").replace("%20", " ");  // remove %20s
    var lesson_name = cell.substring(lesson_pos, lesson_len);
    var student = cell.substring(student_pos, student_len);
    var topic = row[1]    
    var lesson_date = cell.substring(status_len + 1, status_len + 11); // Length of date based on this format: 2021-01-01

    var org_lesson_value = lesson_name
    
    console.log("lesson name: " + lesson_name + "\nstudent: " + student + " \ntopic: " + topic + " \nlesson_date: " + lesson_date + " \nstatus_abbr: " + status_abbr + "\norg_lesson_val: " + org_lesson_value);

    // Retrieve Lesson Status options from Frappe
    frappe.call({
        method: "weekly_planner.www.planner-detail.planner_actions.build_lesson_entry_modal",

        args: {
            "status_abbr": status_abbr,
            "lesson_date": lesson_date,
            "org_lesson_value": org_lesson_value,
        },

        callback: function(r) {
            if (r.exc) {
                frappe.msgprint(__("Missing Status Options data!"));
                return;
            } else {
                var lesson_modal_body = document.getElementById("lesson_modal_body");
                lesson_modal_body.innerHTML = r.message;
                // console.log(r.message);

                $('#modal_add_lesson').modal('show');

                document.querySelector('#save_lesson_button').addEventListener('click', function () {
                    // Save the lesson entry
                    if (document.getElementById("selected_option").value == "") {
                        alert(__("Lesson Status is required!"));
                        return;
                    } else if (document.getElementById("lesson_date").value == "") {
                        alert(__("Lesson Date is required!"));
                        return;
                    }

                    frappe.call({
                        method: "weekly_planner.www.planner-detail.planner_actions.save_lesson_entry",
                        args: {
                            "lesson_name": lesson_name,
                            "planner_name": planner_name,
                            "student": student,
                            "topic": topic,
                            "status": document.getElementById("selected_option").value,
                            "lesson_date": document.getElementById("lesson_date").value,
                            "org_lesson_value": org_lesson_value
                        },
                        callback: function(response) {
                            if (response.exc) {
                                frappe.msgprint(__("Error saving Lesson Entry!"));
                                return;
                            } else {
                                // Reload the page
                                location.reload();                                
                            }
                        }   
                    });
                });
            }
        }
    });
}
