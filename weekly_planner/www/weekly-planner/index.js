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
