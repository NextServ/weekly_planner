frappe.ready(function() {
    new DataTable('#main_table');

    // Check for Approve Planner button click
    $("#modal_action_primary").on("click", function(e) {
        planner_name = e.currentTarget.getAttribute("planner-name");
        // console.log(planner_name)

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

        } else if (document.getElementById("modal_action_title").innerHTML == __("Settings")) {
            console.log("Show Student Age in View: " + document.getElementById("show_student_age_in_view").value);
            frappe.call({
                method: "weekly_planner.www.planner-detail.planner_actions.save_settings",

                args: {
                    "title": document.getElementById("title").value,
                    "welcome_text": document.getElementById("welcome_text").value,
                    "default_color": document.getElementById("default_color").value,
                    "show_student_age_in_view": document.getElementById("show_student_age_in_view").checked,
                    "show_student_age_in_print": document.getElementById("show_student_age_in_print").checked,
                },

                callback: function(r) {
                    if (r.exc) {
                        // Throw error message
                        return;
                    }
                    window.open("/weekly-planner", "_self");
                }
            });
        }
    });

    $("#modal_action_print").on("click", function(e) {
        // The passed attribute is now available to be passed as a URL parameter Step-3
        planner_name = e.currentTarget.getAttribute("planner-name");
        planner_instructor = e.currentTarget.getAttribute("planner-instructor");
        student_group = e.currentTarget.getAttribute("student-group");
        let is_remember = $('#remember_selected_paper_size').is(":checked")
        let paper_size = $('#selected_paper_size').find(":selected").text()

        // First validate that the end date is not before the start date
        selected_report = document.getElementById("selected_report").value;
        student_id = document.getElementById("selected_student").value;
        start_date = document.getElementById("report_start_date").value;
        end_date = document.getElementById("report_end_date").value;
        limit_to_planner = document.getElementById("check_limit_to_planner").checked;
        if (((start_date > end_date) || (!start_date) || (!end_date)) && (selected_report == "Student")) {
            alert(__("Invalid date values! Please re-enter."));
            return;
        }

        if (selected_report == "Planner") {
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

            window.open("/api/method/weekly_planner.www.print-planner.planner_reports.build_planner_report?planner_name=" + planner_name + "&paper_size=" + paper_size, "_blank");
            
        } else {
            // pass the contexts here
            // Can be accessed by
            // context.instructor = frappe.form_dict.get("planner-instructor") in the folder's py file.
            url_text =  "print-student/index.html?planner-name=" + planner_name
            url_text += "&student=" + student_id
            url_text += "&start-date=" + start_date
            url_text += "&end-date=" + end_date
            url_text += "&limit-to-planner=" + limit_to_planner
            url_text += "&planner-instructor=" + planner_instructor
            url_text += "&student-group=" + student_group
            window.open(url_text, "_blank");
        }

    });

    $("#modal_action_select").on("click", function(e) {
        document.getElementById("selected_student").value = document.getElementById("modal_action_select").getAttribute("selected-student");
    })

    $("#btn_show_all").on("click", function(e) {
        hos_show_all();
    })
});


function hos_show_all() {
    // Store HoS show_all value per HoS in tabSingles
    frappe.call({
        method: "weekly_planner.www.planner-detail.planner_actions.hos_show_all",
        callback: function(r) {
            if (r.exc) {
                // Throw error message
                return;
            }
            
            location.reload();
        }
    });
}


function calc_end_date(label_start_date, label_end_date) {
    // Get the start date
    const lessonDateInput = document.getElementById(label_start_date);
    const sevenDaysLater = new Date(lessonDateInput.value);
    sevenDaysLater.setDate(sevenDaysLater.getDate() + 7);
    document.getElementById(label_end_date).value = sevenDaysLater.toISOString().slice(0, 10);
    // console.log(sevenDaysLater);
}


function save_planner(e) {
    // Get input values
    instructor = document.getElementById("instructor").value;
    lesson_date = document.getElementById("lesson_start_date").value;
    student_group = document.getElementById("selected_group").value;
    description = document.getElementById("description").value; 

    console.log("instructor: " + instructor + "\ndate: " + lesson_date + "\nstudent_group: " + student_group + "\ndescription: " + description)

    // Create a new planner
    frappe.call({
        method: "weekly_planner.www.planner-detail.planner_actions.create_planner",
        args: {
            "instructor": instructor,
            "start_date": lesson_date,
            "selected_group": student_group,
            "description": description
        },
        callback: function(r) {
            // Reload the page
            location.reload();
        }
    })
}


function open_settings() {
    frappe.call({
        method: "weekly_planner.www.planner-detail.planner_actions.get_settings",
        callback: function(r) {
            if (r.exc) {
                // Throw error message
                return;
            }

            // Open action modal
            var modal_box = document.getElementById("modal_action_box");
            var action_modal_title = document.getElementById("modal_action_title");
            var action_modal_body = document.getElementById("modal_action_body");
            var action_modal_primary = document.getElementById("modal_action_primary");
            var action_modal_secondary = document.getElementById("modal_action_secondary");

            modal_box.classList.add("modal-md");
            action_modal_title.innerHTML = __("Settings");
            action_modal_body.innerHTML = r.message;
            action_modal_primary.innerHTML = __("Submit");
            action_modal_secondary.innerHTML = __("Cancel");

            $("#modal_action").modal("show");
        }
    });
}


// Write a function to receive data from index.html and use it to open another page
// function open_planner_detail(e = event) {
    // open a new page and pass the planner name to the new page
//    window.open("planner-detail/index.html?planner-name=" + e.currentTarget.getAttribute('planner-name'), "_self");
//}

//Resolving Problem Where The planner Name has ampersand in it
function open_planner_detail(e = event) {
    // Get the planner name from the clicked element
    let plannerName = e.currentTarget.getAttribute('planner-name');
    
    // Replace '&' with '%26' in the planner name
    plannerName = plannerName.replace(/&/g, '%26');
    
    // Open the new page with the encoded planner name
    window.open("planner-detail/index.html?planner-name=" + plannerName, "_self");
}


function approve_planner(e = event) {
    planner_name = e.currentTarget.getAttribute("planner-name");
    
    var action_modal_title = document.getElementById("modal_action_title");
    var action_modal_body = document.getElementById("modal_action_body");
    var action_modal_primary = document.getElementById("modal_action_primary");
    var action_modal_secondary = document.getElementById("modal_action_secondary");

    action_modal_title.innerHTML = __("Approve Planner");
    action_modal_body.innerHTML = __("Are you sure you want to approve this planner?");
    action_modal_primary.innerHTML = __("Submit");
    action_modal_primary.setAttribute("planner-name", planner_name);
    action_modal_secondary.innerHTML = __("Cancel");

    $("#modal_action").modal("show");
}


function print_planner_modal(e = event) {
    // Get the attribute when the print button in weekly-planner is clicked in the list, this is set uniquely for each item in the "data-table". Step-1
    planner_name = e.currentTarget.getAttribute("planner-name");
    planner_start = e.currentTarget.getAttribute("planner-start");
    planner_instructor = e.currentTarget.getAttribute("planner-instructor");
    student_group = e.currentTarget.getAttribute("student-group")
    // Set the fetched data from "data-table" to the current modal that we are gonna use when print button is clicked. Step-2
    document.getElementById("modal_action_print").setAttribute("planner-name", planner_name);
    document.getElementById("modal_action_print").setAttribute("planner-start", planner_start);
    document.getElementById("modal_action_print").setAttribute("planner-instructor", planner_instructor);
    document.getElementById("modal_action_print").setAttribute("student-group", student_group);

    // Reset modal fields
    document.getElementById("selected_report").value = "Planner";
    document.getElementById("selected_student").value = "";
    document.getElementById("report_start_date").value = "";
    document.getElementById("report_end_date").value = "";
    document.getElementById("check_limit_to_planner").checked = false;
    enable_report_options(true);

    $("#modal_print_planner").modal("show");

    // Fetch the stored remembered size
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
}


function enable_report_options(newly_selected = false) {
    // Enable/disable the report options based on the report selection
    options_disabled = document.getElementById("selected_report").value != "Student" || newly_selected;
    document.getElementById("selected_student").disabled = options_disabled;
    document.getElementById("selected_student").required = !options_disabled;
    document.getElementById("button_select").disabled = options_disabled;
    document.getElementById("report_start_date").disabled = options_disabled;
    document.getElementById("report_start_date").required = !options_disabled;
    document.getElementById("report_end_date").disabled = options_disabled;
    document.getElementById("report_end_date").required = !options_disabled;
    document.getElementById("check_limit_to_planner").disabled = options_disabled;

    if (document.getElementById("check_limit_to_planner").checked) {
        // Populate start and end dates
        start_date = document.getElementById("modal_action_print").getAttribute("planner-start");

        // add 7 days to start_date into end_date
        const sevenDaysLater = new Date(start_date);
        sevenDaysLater.setDate(sevenDaysLater.getDate() + 7);
        end_date = sevenDaysLater.toISOString().slice(0, 10);

        document.getElementById("report_start_date").value = start_date;
        document.getElementById("report_end_date").value = end_date;
    }

    // Select Print Report Size
    $("#selected_paper_size").prop('disabled', !options_disabled)
    $("#remember_selected_paper_size").prop('disabled', !options_disabled)
}


function select_student(selected_action){
    student_name = document.getElementById("selected_student").value;

    if (selected_action == "select") {
        frappe.call({
            method: "weekly_planner.www.planner-detail.planner_actions.get_student_for_printing",
            callback: function(r) {
                if (r.exc) {
                    // Throw error message
                    return;
                }

                student_table = document.getElementById("student_table");
                student_table.innerHTML = r.message;
                const table = new DataTable('#student_table', {
                    destroy: true
                });

                if (student_name) {
                    table.search(student_name).draw();
                }

                table.on('click', 'tbody tr', (e) => {
                    let classList = e.currentTarget.classList;
                 
                    if (classList.contains('selected')) {
                        classList.remove('selected');
                    } else {
                        table.rows('.selected').nodes().each((row) => row.classList.remove('selected'));
                        classList.add('selected');
                        document.getElementById("modal_action_select").setAttribute("selected-student", table.row('.selected').data()[2]);
                    }
                });

                // Open action modal
                $("#modal_print_planner").modal("hide");

                $("#modal_select_student").modal("show");
            }
        })
    } else {    // Cancel button clicked
        $("#modal_select_student").modal("hide");
        $("#modal_print_planner").modal("show");
    }
}
