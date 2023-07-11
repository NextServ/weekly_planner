# Copyright (c) 2023, Servio and contributors
# For license information, please see license.txt

# import frappe
from frappe.website.website_generator import WebsiteGenerator

class WeeklyPlanner(WebsiteGenerator):
	def before_saves(self):
		name = self.name.replace(" ", "") 	# Remove spaces from name
		route = "/planner/" + name
		self.route = route
