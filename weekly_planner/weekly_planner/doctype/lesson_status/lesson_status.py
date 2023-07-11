# Copyright (c) 2023, Servio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LessonStatus(Document):
	def before_save(self):
		# frappe.msgprint("Before Save")
		# Store in var abbrev first letter of each word in status
		abbrev = ""
		for word in self.status.split():
			abbrev += word[0]
		
		self.abbreviation = abbrev.upper()
