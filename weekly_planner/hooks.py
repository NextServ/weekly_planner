from . import __version__ as app_version

app_name = "weekly_planner"
app_title = "Weekly Planner"
app_publisher = "Servio"
app_description = "Weekly Planner for Monstessori Guides"
app_email = "ton@serviotech.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/weekly_planner/css/weekly_planner.css"
# app_include_js = "/assets/weekly_planner/js/weekly_planner.js"

# include js, css files in header of web template
# web_include_css = "/assets/weekly_planner/css/weekly_planner.css"
# web_include_js = "/assets/weekly_planner/js/weekly_planner.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "weekly_planner/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "weekly_planner.utils.jinja_methods",
#	"filters": "weekly_planner.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "weekly_planner.install.before_install"
# after_install = "weekly_planner.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "weekly_planner.uninstall.before_uninstall"
# after_uninstall = "weekly_planner.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "weekly_planner.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"weekly_planner.tasks.all"
#	],
#	"daily": [
#		"weekly_planner.tasks.daily"
#	],
#	"hourly": [
#		"weekly_planner.tasks.hourly"
#	],
#	"weekly": [
#		"weekly_planner.tasks.weekly"
#	],
#	"monthly": [
#		"weekly_planner.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "weekly_planner.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "weekly_planner.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "weekly_planner.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["weekly_planner.utils.before_request"]
# after_request = ["weekly_planner.utils.after_request"]

# Job Events
# ----------
# before_job = ["weekly_planner.utils.before_job"]
# after_job = ["weekly_planner.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"weekly_planner.auth.validate"
# ]
