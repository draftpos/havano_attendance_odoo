from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    attendance_start_time = fields.Float(related='company_id.attendance_start_time', readonly=False)
    attendance_earliest_check_in = fields.Float(related='company_id.attendance_earliest_check_in', readonly=False)
    attendance_end_time = fields.Float(related='company_id.attendance_end_time', readonly=False)
    attendance_earliest_check_out = fields.Float(related='company_id.attendance_earliest_check_out', readonly=False)
    attendance_late_time = fields.Float(related='company_id.attendance_late_time', readonly=False)
    attendance_late_check_out = fields.Float(related='company_id.attendance_late_check_out', readonly=False)
    attendance_required_hours = fields.Float(related='company_id.attendance_required_hours', readonly=False)
