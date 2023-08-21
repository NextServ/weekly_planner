frappe.ready(function() {
    const urlParams = new URLSearchParams(window.location.search);
    const plannerName = urlParams.get('planner-name');
    
    // Build items table
    frappe.call({
        method: "weekly_planner.www.print-planner.planner_reports.build_planner_report",
        args: {
            "planner_name": plannerName
        },

        callback: function(r) {
            if (r.message) {
                var items_table = document.getElementById("items_table");
                items_table.innerHTML = r.message;
            }
        }
    });
});
