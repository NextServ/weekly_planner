frappe.ready(function() {
    planner_name = getQueryVariable("planner-name").replace(/%20/g, " ");  // remove %20s

    // Build items table
    frappe.call({
        method: "weekly_planner.www.planner-detail.planner_actions.build_planner_items",
        args: {
            "planner_name": planner_name
        },

        callback: function(r) {
            if (r.message) {
                var items_table = document.getElementById("items_table");
                items_table.innerHTML = r.message;
                
                const targets = [];
                const columns = document.querySelectorAll('#items_table th');
                for (let i = 2; i < columns.length; i++) {
                    targets.push(i);
                }

                const table = new DataTable('#items_table', {
                    order: [[0, 'asc']],
                    scrollX: true,
                    scrollY: true,
                    searching: false,
                    columnDefs: [
                        {"targets": 1, "width": "50px", "orderable": true},
                        {"targets": targets, "orderable": false}
                    ],
                    fixedColumns: {
                        left: 2
                    },
                    fixedHeader: true
                });
            
                // Listen for the click on the body of the table
                table.on('click', 'td', function (e) {
                    // Get the cell data clicked on
                    row = table.row(this).data()
                    cell = table.cell(this)
                    cell_data = cell.data()
                    // console.log("row: " + row + "\ncell: " + cell);

                    // Check if the cell contains "<span>"
                    if (cell_data.includes("<span")) {
                        show_lesson_modal(row, cell_data);
                    } else {
                        // User clicked a topic; prompt if user wants to delete the topic
                        
                    }

                })
            }
        }
    });

    // Check for Add Students button clicked
    $('#modal_add_students').on('show.bs.modal', function (e) {
        show_add_students_modal(planner_name);
    })

    // Check for Add Topics button clicked
    $('#btn_del_students').on('click', function (e) {
        show_students("Delete");
    })

    // Check for Add Topics button clicked
    $('#btn_add_topics').on('click', function (e) {
        show_topics('add');
    })

    // Check for Delete Topics button clicked
    $('#btn_del_topics').on('click', function (e) {
        show_topics('delete');
    })

    $('#save_lesson_button').on('click', function (e) {
        // Save the lesson entry
        if (document.getElementById("lesson_status").value == "") {
            alert(__("Lesson Status is required!"));
            return;
        } else if (document.getElementById("lesson_date").value == "") {
            alert(__("Lesson Date is required!"));
            return;
        }

        // console.log("Lesson Status: " + document.getElementById("lesson_status").value)
        save_button = document.getElementById("save_lesson_button");

        frappe.call({
            method: "weekly_planner.www.planner-detail.planner_actions.save_lesson_entry",
            args: {
                "lesson_name": save_button.getAttribute("lesson_name"),
                "planner_name": planner_name,
                "student": save_button.getAttribute("student"),
                "topic": save_button.getAttribute("topic"),
                "status": document.getElementById("lesson_status").value,
                "lesson_date": document.getElementById("lesson_date").value,
                "org_lesson_value": save_button.getAttribute("org_lesson_value")
            },
            callback: function(r) {
                if (r.exc) {
                    frappe.msgprint(__("Error saving Lesson Entry!"));
                    return;
                } else {
                    cell.data(r.message[0]).draw('false');
                    document.getElementById("delete_lesson_button").setAttribute("lesson_name", r.message[1]);
                }
            }   
        });
    });
    
    $('#delete_lesson_button').on('click', function (e) {
        // Confirm that the user wants to delete this lesson entry
        if (!confirm("Are you sure you want to delete this lesson entry?")) {
            // User clicked "Cancel"
            return;
        }

        frappe.call({
            method: "weekly_planner.www.planner-detail.planner_actions.delete_lesson_entry",
            args: {
                "lesson_name": document.getElementById("delete_lesson_button").getAttribute("lesson_name"),
            },
            callback: function(response) {
                if (response.exc) {
                    frappe.msgprint(__("Error deleting Lesson Entry!"));
                    return;
                } else {
                    // Reload the page
                    location.reload();                                
                }
            }
        });
    })

    // Check for Delete Planner button click
    $("#modal_action_secondary").on("click", function(e) {
        if (document.getElementById("modal_action_title").innerHTML == __("Delete Planner")) {
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
                        alert(r.message);
                    }
                }
            });
        }
    });
 
    // Check for Submit Planner button click
    $("#modal_action_primary").on("click", function(e) {
        if (document.getElementById("modal_action_title").innerHTML == __("Submit Planner")) {
            frappe.call({
                method: "weekly_planner.www.planner-detail.planner_actions.submit_planner",
                args: {
                    "planner_name": planner_name
                },

                callback: function(r) {
                    if (r.message == "success") {
                        // Go back to the main page
                        window.open("/weekly-planner", "_self");
                    } else {
                        alert(r.message);
                    }
                }
            });
        }
    });

    // Check for Approve Planner button click
    $("#modal_action_primary").on("click", function(e) {
        if (document.getElementById("modal_action_title").innerHTML == __("Approve Planner")) {
            frappe.call({
                method: "weekly_planner.www.planner-detail.planner_actions.approve_planner",
                args: {
                    "planner_name": planner_name
                },

                callback: function(r) {
                    if (r.message == "success") {
                        // Go back to the main page
                        window.open("/weekly-planner", "_self");
                    } else {
                        alert(r.message);
                    }
                }
            });
        } else if (document.getElementById("modal_action_title").innerHTML == __("Duplicate Planner")) {
            var selected_group = document.getElementById("selected_group").value
            var plan_date = document.getElementById("plan_date").value

            if (!selected_group || !plan_date) {
                alert(__("Student Group and Start Date are mandatory entries."))
                return
            }

            frappe.call({
                method: "weekly_planner.www.planner-detail.planner_actions.duplicate_planner",
                args: {
                    "planner_name": planner_name,
                    "selected_group": selected_group,
                    "plan_date": plan_date,
                    "include_lessons": document.getElementById("check_include_lessons").value
                },

                callback: function(r) {
                    if (!r.exc) {
                        // Load the new planner
                        window.open("planner-detail/index.html?planner-name=" + r.message);
                    } else {
                        alert(r.message);
                    }
                }
            });
        }
    });
})

$("#modal_print_planner_button").on("click", function(e) {
    // I have to call from a python file. For some reasons i cant do a simple frappe.get_doc here.
    frappe.call({
        method: "weekly_planner.www.planner-detail.planner_actions.fetch_paper_size",
        args: {
            "planner_name": planner_name,
        },

        callback: function(r) {
            if (r.exc) {
                frappe.msgprint(__("Error remembering print size"));
                return;
            }
            if(r.message){
                // console.log(r.message)
                $("#selected_paper_size").val(r.message).change();
            }
        }
    });
})

$("#print_planner_button").on("click", function(e) {
    let is_remember = $('#remember_selected_paper_size').is(":checked")
    let paper_size = $('#selected_paper_size').find(":selected").text();

    if(is_remember){
        frappe.call({
            method: "weekly_planner.www.planner-detail.planner_actions.remember_paper_size",
            args: {
                "planner_name": planner_name,
                "paper_size": paper_size
            },
    
            callback: function(r) {
                if (r.exc) {
                    frappe.msgprint(__("Error remembering print size"));
                    return;
                }
                // console.log(r.message)
            }
        });
    }
    print_planner(paper_size)
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


function duplicate_planner(e) {
    planner_name = getQueryVariable("planner-name").replace(/%20/g, " ");  // remove %20s
    planner = frappe.get_doc("Weekly Planner", planner_name);
    
    // Open and build the modal
    var action_modal_title = document.getElementById("modal_action_title");
    var action_modal_body = document.getElementById("modal_action_body");
    var action_modal_primary = document.getElementById("modal_action_primary");
    var action_modal_secondary = document.getElementById("modal_action_secondary");

    var body_html = __("Please fill in the Student Group and Start Date below:");
    body_html +=    '<br /><br />'
    body_html +=    '<div class="container border bg-light">';
    body_html +=    '   <div class="row">';
    body_html +=    '       <label>' + __("Student Group") + '<input class="input-group-text" list="student_groups" name="selected_group" id="selected_group"/></label>';
    body_html +=    '       <br />';
    body_html +=    '   </div>';
    body_html +=    '   <div class="row">';
    body_html +=    '       <div class="col align-self-start">';
    body_html +=    '           <label>' + __("Start Date") + '<input class="input-group-text text-align-left" id="plan_date" type="date" required></label>';
    body_html +=    '       </div>';
    body_html +=    '       <div class="col align-self-center">';
    body_html +=    '           <div class="form-check">';
    body_html +=    '               <input class="form-check-input" type="checkbox" value="" id="check_include_lessons">';
    body_html +=    '               <label class="form-check-label" for="check_include_lessons">';
    body_html +=                        __('Include lesson entries');
    body_html +=    '               </label>';
    body_html +=    '           </div>'
    body_html +=    '       </div>';
    body_html +=    '   </div>';
    body_html +=    '</div>';

    action_modal_title.innerHTML = __("Duplicate Planner");
    action_modal_body.innerHTML = body_html;
    action_modal_primary.innerHTML = __("Duplicate");
    action_modal_secondary.innerHTML = __("Cancel");
    $("#modal_action").modal("show");
}


function delete_planner(e) {
    planner_name = getQueryVariable("planner-name").replace(/%20/g, " ");  // remove %20s
    planner = frappe.get_doc("Weekly Planner", planner_name);
    
    // Open and build the modal
    var action_modal_title = document.getElementById("modal_action_title");
    var action_modal_body = document.getElementById("modal_action_body");
    var action_modal_primary = document.getElementById("modal_action_primary");
    var action_modal_secondary = document.getElementById("modal_action_secondary");

    action_modal_title.innerHTML = __("Delete Planner");
    action_modal_body.innerHTML = __("Are you sure you want to delete this planner? This cannot be undone.");
    action_modal_primary.innerHTML = __("Cancel");
    action_modal_secondary.innerHTML = __("Delete");
    $("#modal_action").modal("show");
}


function print_planner(e) {
    // This planner-name can be accessed by e.
    // onclick="print_planner(['{{ planner.name }}', 'A4'])"
    // console.log(e[0]) and console.log(e[1]) etc...
    planner_name = getQueryVariable("planner-name").replace(/%20/g, " ");  // remove %20s
    window.open("/api/method/weekly_planner.www.print-planner.planner_reports.build_planner_report?planner_name=" + planner_name + "&paper_size=" + e, "_blank");
}


function submit_planner(e) {
    planner_name = getQueryVariable("planner-name").replace(/%20/g, " ");  // remove %20s
    planner = frappe.get_doc("Weekly Planner", planner_name);

    var action_modal_title = document.getElementById("modal_action_title");
    var action_modal_body = document.getElementById("modal_action_body");
    var action_modal_primary = document.getElementById("modal_action_primary");
    var action_modal_secondary = document.getElementById("modal_action_secondary");

    action_modal_title.innerHTML = __("Submit Planner");
    action_modal_body.innerHTML = __("Are you sure you want to submit this planner?");
    action_modal_primary.innerHTML = __("Submit");
    action_modal_secondary.innerHTML = __("Cancel");
    $("#modal_action").modal("show");
}


function approve_planner(e) {
    planner_name = getQueryVariable("planner-name").replace(/%20/g, " ");  // remove %20s
    planner = frappe.get_doc("Weekly Planner", planner_name);

    var action_modal_title = document.getElementById("modal_action_title");
    var action_modal_body = document.getElementById("modal_action_body");
    var action_modal_primary = document.getElementById("modal_action_primary");
    var action_modal_secondary = document.getElementById("modal_action_secondary");

    action_modal_title.innerHTML = __("Approve Planner");
    action_modal_body.innerHTML = __("Are you sure you want to approve this planner?");
    action_modal_primary.innerHTML = __("Submit");
    action_modal_secondary.innerHTML = __("Cancel");
    $("#modal_action").modal("show");
}


function show_students(mode = "Add") {
    var planner_name = getQueryVariable("planner-name").replace(/%20/g, " ");  // remove %20s
    var campus = (mode == "Add") ? document.getElementById("selected_campus").value : "";
    var group = (mode == "Add") ? document.getElementById("selected_group").value : "";
    
    // Retrieve students from Frappe
    frappe.call({
        method: "weekly_planner.www.planner-detail.planner_actions.get_students_for_selection",
        args: {
            "selected_campus": campus,
            "selected_group": group,
            "planner_name": planner_name,
            "mode": mode,
        },

        callback: function(students) {
            if (students.message) {
                // Make sure the right table name is used
                var table_name = (mode == "Add") ? "students_table" : "del_students_table";

                var lesson_body = document.getElementById(table_name);
                table_name = "#" + table_name;

                // Build the lesson_body with columns student, campus and group using the dataset returned from get_students_for_selection method
                var lesson_body_html = '<thead><tr><th>ID</th><th>First Name</th><th>Last Name</th><th>DOB</th><th>Student Group</th></tr></thead><tbody>';
                
                students.message.forEach((student) => {
                    lesson_body_html += '<tr><td>' + student.name + '</td><td>' + student.first_name + '</td><td>' + 
                        student.last_name + '</td><td>' + student.date_of_birth + '</td><td>' + student.parent +'</td></tr>';
                });
                lesson_body_html += '</tbody>';

                // Add the table to the page
                lesson_body.innerHTML = lesson_body_html;

                // todo: Adjust modal in case the table is too big
                // myModal.handleUpdate()

                const table = new DataTable(table_name, {
                    destroy: true,
                    order: [[2, 'asc'], [1, 'asc']],
                    columnDefs: [
                        {
                            target: 0,
                            visible: false,
                            searchable: false
                        }
                    ]
                });                

                // todo: fix the selection of rows
                table.on('click', 'tbody tr', function (e) {
                    e.currentTarget.classList.toggle('selected');
                });
                
                if (mode == "Add") {
                    document.querySelector('#clear_button').addEventListener('click', function () {
                        table.rows('.selected').nodes().each((row) => row.classList.toggle('selected'));
                    });

                    // Add selected students to the planner
                    document.querySelector('#add_button').addEventListener('click', function () {
                        // Output to console.log details of each student in selected_students

                        const insert_list = [];
                        table.rows(".selected").every(function ( rowIdx, tableLoop, rowLoop ) {
                            // Build an array containing both student and planner_name
                            item = this.data()[0];
                            insert_list.push(item);
                        });
                        
                        // Output to console log each element in the insert_list array
                        // console.log(insert_list);
                        save_students(planner_name, insert_list);
                    });

                } else {    // Delete selected students from the planner
                    var modal_del_students = new bootstrap.Modal(document.getElementById('modal_del_students'), {
                        keyboard: true
                    })

                    modal_del_students.show();

                    document.querySelector('#clear_del_button').addEventListener('click', function () {
                        table.rows('.selected').nodes().each((row) => row.classList.toggle('selected'));
                    });

                    document.querySelector('#del_button').addEventListener('click', function () {
                        const del_list = [];
                        table.rows(".selected").every(function ( rowIdx, tableLoop, rowLoop ) {
                            // Build an array containing both student and planner_name
                            item = this.data()[0];
                            del_list.push(item);
                        });
                        
                        modal_del_students.hide();
                        delete_students(planner_name, del_list);
                    });

                    document.querySelector('#btn_del_students_cancel').addEventListener('click', function () {
                        modal_del_students.hide();
                    });
                }
            }
        }
    });
}


function save_students(planner_name, insert_list) {
    frappe.call({
        method: "weekly_planner.www.planner-detail.planner_actions.save_students",
        args: {
            "planner_name": planner_name,
            "insert_list": insert_list
        },

        callback: function(r) {
            if (!r.exc) {
                // Go back to the main page
                location.reload();
            } else {
                frappe.show_alert(
                    {
                        message: __("Error loading students!"),
                        indicator: "red",
                    },
                    3
                );
            }
        }
    });
}


function delete_students(planner_name, del_list) {
    var action_modal = new bootstrap.Modal(document.getElementById('modal_action'), {
        keyboard: true
    })

    if (del_list.length == 0) {
        // Check that there are students to delete
        action_modal.show();
        document.getElementById("modal_action_title").innerHTML = __("No Students selected");
        document.getElementById("modal_action_body").innerHTML = __("Please select Students to delete.");
        document.getElementById("modal_action_primary").innerHTML = __("OK");
        document.getElementById("modal_action_secondary").visible = false;

        location.reload();
        return;
    }

    action_modal.show();
    document.getElementById("modal_action_title").innerHTML = __("Are you sure you wish to delete the selected Students?");
    document.getElementById("modal_action_body").innerHTML = __("Selected Students may have lesson entries. Deleting them will also delete the lesson entries.");
    document.getElementById("modal_action_primary").innerHTML = __("Cancel");
    document.getElementById("modal_action_secondary").innerHTML = __("Delete");

    // Confirm that the user wants to delete the selected students before proceeding
    document.querySelector('#modal_action_primary').addEventListener('click', function () {
        location.reload();
        return;
    });

    document.querySelector('#modal_action_secondary').addEventListener('click', function () {
        frappe.call({
            method: "weekly_planner.www.planner-detail.planner_actions.delete_students",
            args: {
                "planner_name": planner_name,
                "del_list": del_list
            },

            callback: function(r) {
                if (!r.exc) {
                    // Go back to the main page
                    location.reload();
                } else {
                    frappe.show_alert(
                        {
                            message: __("Error deleting students!"),
                            indicator: "red",
                        },
                        3
                    );
                }
            }
        });
    });
}


function show_topics(show_action) {
    // Retrieve topics from Frappe
    planner_name = getQueryVariable("planner-name").replace(/%20/g, " ");  // remove %20s

    frappe.call({
        method: "weekly_planner.www.planner-detail.planner_actions.get_topics_for_selection",
        args: {
            "planner_name": planner_name,
            "show_action": show_action
        },

        callback: function(topics) {
            if (topics.message) {
                var topics_table = document.getElementById("topics_table");
                if (show_action == "add") {
                    document.getElementById("modal_topics_title").innerHTML = __("Add Topics");
                    document.getElementById("add_topics_button").innerHTML = __("Add Selected");
                } else {
                    document.getElementById("modal_topics_title").innerHTML = __("Delete Topics");
                    document.getElementById("add_topics_button").innerHTML = __("Delete Selected");
                }

                // Show the topics table
                topics_table.innerHTML = "";

                // Build the topics_table with columns topic, campus and group using the dataset returned from get_topics method
                var topics_table_html = '<thead><tr><th>Topic</th><th>Course</th><th>Key</th></tr></thead><tbody>';
                
                topics.message.forEach((topic) => {
                    course = topic.parent ? topic.parent : "";
                    topics_table_html += '<tr><td>' + topic.subject + '</td>';
                    topics_table_html += '<td>' + course + '</td>'
                    topics_table_html += '<td>' + topic.record_key + '</td></tr>';
                });
                topics_table_html += '</tbody>';
                // console.log(topics_table_html);

                // Add the table to the page
                topics_table.innerHTML = topics_table_html;
                const table = new DataTable('#topics_table', {
                    destroy: true,
                    rowGroup: {
                        dataSrc: 1
                    },
                    columnDefs: [{
                        target: 2,
                        visible: false,
                        searchable: false
                    }],
                    order: [[1, 'asc']]
                });

                $('#modal_add_topics').modal('show');

                table.on('click', 'tbody tr', function (e) {
                    e.currentTarget.classList.toggle('selected');
                });
                
                document.querySelector('#clear_topics_button').addEventListener('click', function () {
                    table.rows('.selected').nodes().each((row) => row.classList.toggle('selected'));
                })

                document.querySelector('#add_topics_button').addEventListener('click', function () {
                    // Output to console.log details of each student in selected_students

                    const insert_list = [];
                    table.rows(".selected").every(function ( rowIdx, tableLoop, rowLoop ) {
                        // Build an array containing both student and planner_name
                        if (show_action == 'add') {
                            item = this.data()[0].replace(/&amp;/g, "&");
                        } else {
                            item = this.data()[2]           // topic name for deleting; this is a hidden column
                        }
                        insert_list.push(item);
                    });
                    
                    // Output to console log each element in the insert_list array
                    save_topics(planner_name, insert_list, show_action);
                });

                document.querySelector('#cancel_topics_button').addEventListener('click', function () {
                    // Destroy the table
                    topics_table.DataTable().clear()
                    topics_table.DataTable().destroy();
                    topics_table.empty();
                    topics_table.innerHTML = "";
                });
            }
        }
    });
}


function save_topics(planner_name, insert_list, show_action) {
    // Confirm that the user wants to delete the selected topic before proceeding
    if (show_action == "delete") {
        if (!confirm(__("Are you sure you want to delete the selected topics?"))) {
            // User clicked "Cancel"
            return;
        }
    }

    frappe.call({
        method: "weekly_planner.www.planner-detail.planner_actions.save_topics",
        args: {
            "planner_name": planner_name,
            "insert_list": insert_list,
            "show_action": show_action
        },

        callback: function(r) {
            if (!r.exc) {
                // Go back to the main page
                location.reload();
            } else {
                frappe.show_alert(
                    {
                        message: __("Error loading students!"),
                        indicator: "red",
                    },
                    3
                );
            }
        }
    });
}


function show_add_students_modal(planner_name) {
    frappe.call({
        method: "weekly_planner.www.planner-detail.planner_actions.build_add_students_modal",
        args: {"planner_name": planner_name,},

        callback: function(r) {
            if (r.exc) {
                frappe.msgprint(__("Error building Add Students modal!"));
                return;
            }

            var modal_body = document.getElementById("modal_add_students_body");
            modal_body.innerHTML = r.message;
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
    var planner_name = getQueryVariable("planner-name").replace(/%20/g, " ");  // remove %20s
    var lesson_name = cell.substring(lesson_pos, lesson_len);
    var student = cell.substring(student_pos, student_len);
    var topic = row[1]    
    var lesson_date = cell.substring(status_len + 1, status_len + 9); // Length of date based on this format: 07/19/23
    
    var org_lesson_value = lesson_name
    
    console.log("lesson name: " + lesson_name + "\nplanner_name: " + planner_name + "\nstudent: " + student + " \ntopic: " + topic + " \nlesson_date: " + lesson_date + " \nstatus_abbr: " + status_abbr + "\norg_lesson_val: " + org_lesson_value);

    // Retrieve Lesson Status options from Frappe
    frappe.call({
        method: "weekly_planner.www.planner-detail.planner_actions.build_lesson_entry_modal",

        args: {
            "student": student,
            "topic": topic,
            "lesson_name": lesson_name,
            "status_abbr": status_abbr,
            "lesson_date": lesson_date,
            "org_lesson_value": org_lesson_value,
        },

        callback: function(r) {
            if (r.exc) {
                frappe.msgprint(__("Missing Status Options data!"));
                return;
            }

            var lesson_modal_body = document.getElementById("lesson_modal_body");
            lesson_modal_body.innerHTML = r.message;
            
            if (lesson_name) {
                const history_table = new DataTable('#history_table', {
                    destroy: true,
                    searching: false,
                    lengthChange: false
                });
            }

            // Attach some attributes to the save_lesson_button for later use
            save_button = document.getElementById("save_lesson_button");
            save_button.setAttribute("lesson_name", lesson_name);
            save_button.setAttribute("topic", topic);
            save_button.setAttribute("student", student);
            save_button.setAttribute("org_lesson_value", org_lesson_value);

            document.getElementById("delete_lesson_button").setAttribute("lesson_name", lesson_name);

            $('#modal_add_lesson').modal('show');
        }
    });
}