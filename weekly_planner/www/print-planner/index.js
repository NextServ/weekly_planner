import { readFileSync } from 'fs';
import { create } from 'html-pdf';

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
            if (r.exc) {
                frappe.msgprint("Error building planner report");
                return;
            }
            
            var items_table = document.getElementById("items_table");
            items_table.innerHTML = r.message;

            // Generate PDF from index.html
            const html = readFileSync('index.html', 'utf8');
            create(html, { format: 'Letter' }).toFile('demo.pdf', function(err, res) {
                if (err) return console.log(err);
                console.log(res);
            });
        }
    });
});
