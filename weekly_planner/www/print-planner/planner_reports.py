import frappe
from frappe import _
from datetime import date, timedelta, datetime
from weekly_planner.utils import diff_months
from frappe.utils.pdf import get_pdf

options = {
    "margin-left": '1.5mm',
    "margin-right": '1.5mm',
    "margin-top": '1.5mm',
    "margin-bottom": '1.5mm'
}

@frappe.whitelist()
def build_planner_report(planner_name):
    # Remove %20 from planner_name
    if planner_name:    
        planner_name = planner_name.replace("%20", " ")

    planner = frappe.get_doc("Weekly Planner", planner_name)
    start_date = planner.start_date.strftime("%m/%d/%Y")
    end_date = (planner.start_date + timedelta(days=7)).strftime("%m/%d/%Y")
        
    # Check if show age is enabled
    show_age = frappe.db.get_single_value("Weekly Planner Settings", "show_student_age_in_print")

    # First load all students from Planner Detail
    all_students = frappe.db.sql('''SELECT p.student, s.first_name, s.last_name, s.date_of_birth
                             FROM `tabPlanner Student` p INNER JOIN `tabStudent` s
                             ON p.student = s.name
                             WHERE p.parent = %(p_name)s''', {"p_name": planner_name}, as_dict=True)
    
    # lessons = frappe.get_all("Planner Lesson", filters={"parent": planner_name}, fields=["*"])
    topics = frappe.get_all("Planner Topic", filters={"parent": planner_name}, fields=["*"])
    lessons = frappe.db.sql('''SELECT p.name, p.date, p.student, p.topic, l.abbreviation from `tabPlanner Lesson` p
                            INNER JOIN `tabLesson Status` l ON p.lesson_status = l.name
                            WHERE parent = %(p_name)s''', {"p_name": planner_name}, as_dict=True)

    cols_per_batch = 12
    total_batches = int((len(all_students) / cols_per_batch) + 1 if (len(all_students) % cols_per_batch) or (len(all_students) == cols_per_batch) else 0)
    
                            
    html_text =  '<head>'
    html_text += '    <script src="https://code.jquery.com/jquery-3.7.0.js"></script>'
    html_text += '    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">'
    html_text += '    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>'
    html_text += '    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.min.js" integrity="sha384-cVKIPhGWiC2Al4u+LWgxfKTRIcfu0JTxR+EQDz/bgldoEyl4H0zUF0QKbrJ0EcQF" crossorigin="anonymous"></script>'
    html_text += '</head>'
   
    html_text += '<!-- Header -->'
    html_text += '<header class="container-fluid">'
    html_text += '  <div>'
    html_text += '    <div>'
    html_text += '        <h3>' + _(frappe.db.get_single_value("Weekly Planner Settings", "title") + ' Detail') + '</h3>'
    html_text += '    </div>'
    html_text += '  </div>'
    
    html_text += '  <!-- display table header titles vertically -->'
    html_text += '  <style>'
    html_text += '      .new-page {'
    html_text += '          page-break-before: always;'
    html_text += '      }'
                   
    html_text += '      .rotated-text {'
    html_text += '          transform-origin: bottom center;'
    html_text += '          transform: rotate(-90deg) translateX(50%) translateY(12%); /* Rotate the text by 90 degrees */'
    html_text += '          white-space: nowrap; /* Keep the text on one line */'
    html_text += '          text-align: center;'
    html_text += '          /* left: 50%; */'
    html_text += '          height: 200px;'
    html_text += '      }'
                   
    html_text += '      table#items_table > thead > tr {'
    html_text += '          height: auto;'
    html_text += '      }'
                   
    html_text += '      table#items_table th:not(:first-child) {'
    html_text += '          max-width: 80px;'
    html_text += '      }'
                   
    html_text += '      table#items_table {'
    html_text += '          width: auto;'
    html_text += '      }'
                   
    html_text += '      main {'
    html_text += '          margin-left: 0px !important;'
    html_text += '          margin-right: 0px !important;'
    html_text += '      }'
    html_text += '  </style>'

    html_text += '</header>'
    html_text += '<!-- ./ Header -->'

    html_text += '<!-- Main -->'
    html_text += '<main class="container-fluid">'

    for batch in range(total_batches):       
        students = all_students[batch * cols_per_batch:batch + cols_per_batch]
        html_text += '<p class=new-page />' if batch else ''
                            
        html_text += '    <!-- Planner Header -->'
        html_text += '    <br />'
        html_text += '    <section id="header">'
        html_text += '        <!-- Grid -->'
        html_text += '        <form>'
        html_text += '            <div class="row">'
        html_text += '                <div class="col">'
        html_text += '                    ' + _("Instructor")
        html_text += '                    <input type="text" class="form-control" placeholder="First name" value="' + planner.instructor + '" readonly>'
        html_text += '                </div>'
        html_text += '                <div class="col">'
        html_text += '                    ' + _("Student Group")
        html_text += '                    <input type="text" class="form-control" placeholder="Last name" value="' + planner.student_group +'" readonly>'
        html_text += '                </div>'
        html_text += '            </div>'
        html_text += '            <br />'
        html_text += '            <div class="row">'
        html_text += '                <div class="col">'
        html_text += '                    '+ _("Date")
        html_text += '                    <input type="text" class="form-control" placeholder="Date" value="' + start_date + ' to ' +  end_date + '" readonly>'
        html_text += '                </div>'
        html_text += '                <div class="col">'
        html_text += '                    <br />'

        if planner.is_approved:
            html_text += '                <h5>' + _("[Approved]") + '</h5>'
        elif planner.status == 0:
            html_text += '                <h5>' + _("[Draft]") + '</h5>'
        elif planner.status == 1:
            html_text += '                <h5>' + _("[Submitted]") + '</h5>'
        else:
            html_text += '                <h5>' + _("[Cancelled]") + '</h5>'

        html_text += '                </div>'
        html_text += '            </div>'
        html_text += '        </form>'
        html_text += '    </section>'
        html_text += '    <br />'
        html_text += '    <!-- ./ Planner Header -->'


        # planner_details = [["" for row in range(num_students)] for col in range(num_topics)]
        student_headers = {}
        topic_headers = []

        # Build the table html
        html_text += '    <!-- Tables -->'
        html_text += '    <table class="table table-bordered" id="items_table">'
        html_text += '      <thead>'
        html_text += '        <tr>'
        html_text += '          <th><span width="15px">Topic</span></th>'

        # Load up the columns
        for student in students:
            if student.student not in student_headers:
                # Calculate age in years and months
                years = None
                months = None
                if student.date_of_birth:
                    years = int(diff_months(datetime.today(), student.date_of_birth) / 12)
                    months = years % 12

                html_text += "<th class='rotated-text'>" + student.last_name + " " + student.first_name
                if show_age:
                    html_text += "<h6><i class='fw-light'>" + str(years) + " Years " + str(months) + " Months</i></h6>"
                
                html_text += "</th>"

            student_headers[student.student] = student.student
        
        html_text += "</tr></thead><tbody>"

        # Load up the rows
        for topic in topics:
            html_text += "<tr><td>" + topic.topic + "</td>"

            if not topic.topic in topic_headers:
                topic_headers.append(topic.topic)

                # loop through keys
                for col_header in student_headers.keys():
                    item = [entry for entry in lessons if entry["topic"] == topic.topic and entry["student"] == col_header]
                    html_text += "<td class='text-center'>"

                    if item != []:
                        lesson_item = item[0].abbreviation + " " + item[0].date.strftime('%m-%d-%y')
                        html_text += "<span class='text-center'>[" + lesson_item + "]</span>"
                    else:
                        html_text += "<span><p hidden>student: " + col_header + " | name: none | </span>"
                    
                    html_text += "</td>"

        html_text += '      </tr>'
        html_text += '    </tbody></table>'
        html_text += '    <!-- ./ Tables -->'
        
    html_text += '</main>'
    html_text += '<!-- ./ Main -->    '

    file_name = 'planner_report'
    options["page-size"] = "A4"
    options["orientation"] = "Landscape"

    frappe.local.response.filename = "{file_name}.pdf".format(file_name=file_name)
    frappe.local.response.filecontent = get_pdf(html_text, options)
    frappe.local.response.type = "pdf"

    return file_name