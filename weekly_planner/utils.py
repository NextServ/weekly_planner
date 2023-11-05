from datetime import date, datetime


# Description: Utility functions for weekly_planner
def get_root_url():
    return frappe.utils.get_url()


# write code to take first letter of every word in string and make it uppercase
def get_initials(name):
    initials = ""
    for word in name.split():
        initials += word[0].upper()
    return initials


# Return difference between two dates in months
def diff_months(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month