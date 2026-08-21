{
    'name': 'Havano Attendance Dashboard',
    'version': '1.0',
    'category': 'Human Resources/Attendance',
    'summary': 'Custom statistical dashboard for Attendance',
    'description': """
        This module provides a custom dashboard for the HR Attendance app.
        It displays statistics such as Total Employees, Active Today, Absent Today,
        Early Check-in, Late Check-in, Early Check-out, and Late Check-out.
    """,
    'author': 'Havano',
    'depends': ['hr_attendance'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/attendance_dashboard_views.xml',
        'views/hr_attendance_report_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'havano_attendance_odoo/static/src/xml/attendance_dashboard.xml',
            'havano_attendance_odoo/static/src/js/attendance_dashboard.js',
            'havano_attendance_odoo/static/src/css/attendance_dashboard.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
