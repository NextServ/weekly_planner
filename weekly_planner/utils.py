# Description: Utility functions for weekly_planner
def get_root_url():
    return frappe.utils.get_url()

# wriite code to take first letter of every word in string and make it uppercase
def get_initials(name):
    initials = ""
    for word in name.split():
        initials += word[0].upper()
    return initials