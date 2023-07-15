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