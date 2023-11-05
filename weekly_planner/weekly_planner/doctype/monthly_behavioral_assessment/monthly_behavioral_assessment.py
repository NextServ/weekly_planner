# Copyright (c) 2023, Servio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MonthlyBehavioralAssessment(Document):
    def autoname(self):
        # Get the student name
        last_name, first_name = frappe.db.get_value('Student', self.student, ['last_name', 'first_name'])

        self.name = last_name + ', ' + first_name + ' - ' + self.month + ' - ' + self.academic_year
