frappe.ready(function() {
    new DataTable('#main_table');

    // Check for Approve Planner button click
    $("#modal_action_primary").on("click", function(e) {
        planner_name = e.currentTarget.getAttribute("planner-name");
        console.log(planner_name)

        if (document.getElementById("modal_action_title").innerHTML == "Approve Planner") {
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
        }
    });
})


function calc_end_date(e) {
    // Get the start date
    const lessonDateInput = document.getElementById("lesson_date");
    const sevenDaysLater = new Date(lessonDateInput.value);
    sevenDaysLater.setDate(sevenDaysLater.getDate() + 7);
    document.getElementById("end_date").value = sevenDaysLater.toISOString().slice(0, 10);
    console.log(sevenDaysLater);
}


function save_planner(e) {
    // Get input values
    instructor = document.getElementById("instructor").value;
    lesson_date = document.getElementById("lesson_date").value;
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


// Write a function to receive data from index.html and use it to open another page
function open_planner_detail(e = event) {
    // open a new page and pass the planner name to the new page
    window.open("planner-detail/index.html?planner-name=" + e.currentTarget.getAttribute('planner-name'), "_self");
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