import os


def get_report_resource_path(resource_name):
    if resource_name:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", resource_name)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")