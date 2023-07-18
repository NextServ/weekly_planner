frappe.ready(function() {
    new DataTable('#main_table');
})

// Write a function to receive data from index.html and use it to open another page
function open_planner_detail(e = event) {
    // alert("Planner name:" + e.currentTarget.getAttribute('planner-name'));
    planner_name = e.currentTarget.getAttribute('planner-name');

    // open a new page and pass the planner name to the new page
    window.open("planner-detail/index.html?planner-name=" + planner_name, "_self");
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