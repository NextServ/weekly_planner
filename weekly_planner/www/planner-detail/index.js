frappe.ready(function() {
    // $('#items_table').DataTable();
    new DataTable('#items_table');

})

function go_to_main() {
    // Go back to the main page
    window.open("/weekly-planner", "_self");
}

function delete_planner(e = event) {
    // alert("Planner name:" + e.currentTarget.getAttribute('planner-name'));
    planner_name = e.currentTarget.getAttribute('planner-name');

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

function show_students(e = event) {
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
                var student_table = document.getElementById("students_table");

                // Show the students tableClass 1
                student_table.innerHTML = "";

                // Build the student_table with columns student, campus and group using the dataset returned from get_students_for_selection method
                var student_table_html = '<thead><tr><th>First Name</th><th>Last Name</th><th>DOB</th></tr></thead><tbody>';
                
                students.message.forEach((student) => {
                    student_table_html += '<tr><td>' + student.first_name + '</td><td>' + student.last_name + '</td><td>' + 
                        student.date_of_birth + '</td></tr>';
                });
                student_table_html += '</tbody>';

                // Add the table to the page
                student_table.innerHTML = student_table_html;
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
    var student_table = document.getElementById("students_table");
    
    // Clear the sudent_table if there are rows in it
    if (student_table.rows.length > 0) {
        // Clear the table
        student_table.innerHTML = "";

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