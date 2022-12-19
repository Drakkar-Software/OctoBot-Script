import os


def get_report_resource_path(resource_name):
    base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    if resource_name:
        return os.path.join(base_path, resource_name)
    return base_path
