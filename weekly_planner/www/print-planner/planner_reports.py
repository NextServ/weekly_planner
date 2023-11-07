import frappe
from frappe import _
from datetime import date, timedelta, datetime
from weekly_planner.utils import diff_months
from frappe.utils.pdf import get_pdf

options = {
    "margin-left": '2mm',
    "margin-right": '2mm',
    "margin-top": '2mm',
    "margin-bottom": '2mm'
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
    
    all_topics = frappe.get_all("Planner Topic", filters={"parent": planner_name, "is_hidden": 0}, fields=["*"])

    lessons = frappe.db.sql('''SELECT p.name, p.date, p.student, p.topic, l.abbreviation from `tabPlanner Lesson` p
                            INNER JOIN `tabLesson Status` l ON p.lesson_status = l.name
                            WHERE parent = %(p_name)s''', {"p_name": planner_name}, as_dict=True)

    studs_per_batch = 35
    topics_per_batch = 7
    topics_done = True
    cur_page = 0
    cur_student_batch = 0
    total_students = len(all_students)
    total_topics = len(all_topics)
    # We can't always assure that the total_students will always be equal to studs_per_batch. This results to 0 value. Not sure of the purpose.
    total_stud_batches = int((total_students / studs_per_batch) + (1 if (total_students % studs_per_batch) and (total_students <= studs_per_batch) else 0))
    # total_stud_batches = int((total_students / studs_per_batch) + (1 if (total_students % studs_per_batch)else 0))
    total_topic_batches = int((total_topics / topics_per_batch) + (1 if (total_topics % topics_per_batch) or (total_topics == topics_per_batch) else 0))
    total_pages = total_stud_batches * total_topic_batches
    # breakpoint()
                            
    html_text =  '<head>'
    # html_text += '    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">'
    html_text += '  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">'
    html_text += '  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>'

    html_text += '</head>'
       
    html_text += '<!-- Header -->'
    html_text += '<header class="container">'
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
    # html_text += '          transform-origin: top center;'
    # html_text += '          transform: rotate(-90deg) translateX(50%) translateY(12%); /* Rotate the text by 90 degrees */'

    html_text += '          -webkit-transform: rotate(-90deg) translate(-55px, -60px);'
    # html_text += '          -moz-transform: rotate(-90deg) translate(-60px, -60px);'
    # html_text += '          -ms-transform: rotate(-90deg) translate(-60px, -60px);'
    # html_text += '          -o-transform: rotate(-90deg) translate(-60px, -60px);'
    
    html_text += '          white-space: nowrap; /* Keep the text on one line */'
    html_text += '          text-align: top;'
    html_text += '          height: 190px;'
    html_text += '      }'
                   
    html_text += '      table#items_table > thead > tr {'
    html_text += '          height: auto;'
    html_text += '      }'
                   
    html_text += '      table#items_table th:not(:first-child) {'
    # html_text += '          max-width: 50px;'
    # html_text += '          max-width: ' + _(str(1750 / total_students)) + 'px;'
    html_text += '          max-width: ' + _(str(1000 / total_students)) + 'px;'
    # html_text += '          max-width: 2%;'
    html_text += '      }'
                   
    html_text += '      table#items_table {'
    html_text += '          width: auto;'
    html_text += '      }'
                   
    html_text += '      main {'
    html_text += '          margin-left: 0px !important;'
    html_text += '          margin-right: 0px !important;'
    html_text += '      }'

    html_text += '      h7 {'
    html_text += '          font-family: Arial, Helvetica, sans-serif;'
    html_text += '          font-size: 5pt;'
    html_text += '      }'
    html_text += '  </style>'

    html_text += '</header>'
    html_text += '<!-- ./ Header -->'

    html_text += '<!-- Main -->'
    html_text += '<main class="container-xl"><h7>'

    print('* build_planner_report')

    while True:
        cur_page += 1
        if cur_page > total_pages:
            break

        if topics_done:
            cur_topic_batch = 1
            cur_student_batch += 1
            students = all_students[(cur_student_batch - 1) * studs_per_batch:cur_student_batch * studs_per_batch]
            print('student batch: ' + str(cur_student_batch) + ' / ' + str(total_stud_batches) + ' | students: ' + str(total_students))
        
        html_text += '<p class=new-page />' if cur_page > 1 else ''
        print('  topic_batch: ' + str(cur_topic_batch) + ' / ' + str(total_topic_batches) + ' | topics: ' + str(total_topics) + ' | topics_done: ' + str(topics_done))

        html_text += '    <!-- Planner Header -->'
        html_text += '    <br />'
        html_text += '    <!-- Grid -->'
        html_text += '    <div class="container">'
        html_text += '      ' + _("Instructor:") + '&nbsp <b>' + planner.instructor + '</b>&nbsp &nbsp &nbsp' + _("Student Group: ") + '<b>' + planner.student_group + '</b>'
        html_text += '      &nbsp &nbsp &nbsp'
        html_text += '      ' + _("Dates:") + '&nbsp <b>' + start_date + '</b> to <b>' +  end_date + '</b> &nbsp &nbsp &nbsp' + _("Status:") + '&nbsp <b>'

        if planner.is_approved:
            html_text += _("Approved")
        elif planner.status == 0:
            html_text += _("Draft")
        elif planner.status == 1:
            html_text +=_("Submitted")
        else:
            html_text += _("Cancelled")

        html_text += '    </b></div>'
        html_text += '    <br />'
        html_text += '    <!-- ./ Planner Header -->'


        # planner_details = [["" for row in range(num_students)] for col in range(num_topics)]
        student_headers = {}
        topic_headers = []

        # Build the table html
        html_text += '    <!-- Tables -->'
        html_text += '    <table class="table table-bordered" id="items_table">'
        html_text += '      <thead><h7>'
        html_text += '        <tr>'
        html_text += '          <th style="width: 10px;"><span><h7>Topic</h7></span></th>'

        # Load up the columns
        for student in students:
            if student.student not in student_headers:
                # Calculate age in years and months
                years = None
                months = None
                if student.date_of_birth:
                    years = int(diff_months(datetime.today(), student.date_of_birth) / 12)
                    months = years % 12

                html_text += "<th class='rotated-text'><h7>" + student.last_name + " " + student.first_name
                if show_age:
                    html_text += "<p class='fw-light'><i>" + str(years) + " Years " + str(months) + " Months</i><p>"
                
                html_text += "</h7></th>"

            student_headers[student.student] = student.student
        
        html_text += "</tr></h7></thead><tbody><h7>"

        # Load up the rows
        topics = all_topics[(cur_topic_batch - 1) * topics_per_batch:cur_topic_batch * topics_per_batch]

        cur_topic_batch += 1
        topics_done = cur_topic_batch > total_topic_batches
                            
        for topic in topics:
            html_text += "<tr><td><h7>" + topic.topic[:50] + ('...' if len(topic.topic) > 50 else '') + "</h7></td>"

            if not topic.topic in topic_headers:
                topic_headers.append(topic.topic)

                # loop through keys
                for col_header in student_headers.keys():
                    item = [entry for entry in lessons if entry["topic"] == topic.topic and entry["student"] == col_header]
                    html_text += "<td class='text-center'><h7>"

                    if item != []:
                        lesson_item = item[0].abbreviation + " " + item[0].date.strftime('%m-%d')
                        html_text += "<span class='text-center'>" + lesson_item + "</span>"
                    
                    html_text += "</h7></td>"

        html_text += '      </tr>'
        html_text += '    </h7></tbody></table>'
        html_text += '    <!-- ./ Tables -->'
        
    html_text += '</h7></main>'
    html_text += '<!-- ./ Main -->    '

    file_name = 'planner_report'
    options["page-size"] = "A4"
    options["orientation"] = "Landscape"
    # options["minimum-font-size"] = "3"

    frappe.local.response.filename = "{file_name}.pdf".format(file_name=file_name)
    frappe.local.response.filecontent = get_pdf(html_text, options)
    frappe.local.response.type = "pdf"

    return file_name