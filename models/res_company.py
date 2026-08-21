from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    attendance_start_time = fields.Float(string="Expected Check-in Time", default=8.0)
    attendance_earliest_check_in = fields.Float(string="Earliest Check-in", default=6.0)
    attendance_end_time = fields.Float(string="Expected Check-out Time", default=17.0)
    attendance_earliest_check_out = fields.Float(string="Earliest Check-out", default=16.0)
    attendance_late_time = fields.Float(string="Late Check-in Threshold", default=8.25)
    attendance_late_check_out = fields.Float(string="Late Check-out Threshold", default=17.5)
    attendance_required_hours = fields.Float(string="Required Working Hours", default=8.0)
