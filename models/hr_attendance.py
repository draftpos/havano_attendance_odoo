from odoo import models, fields, api
from datetime import datetime, time
import pytz

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    check_in_status = fields.Selection([
        ('early', 'Early'),
        ('normal', 'Normal'),
        ('late', 'Late')
    ], string="Check-in Status", compute="_compute_check_in_out_status", store=True)
    
    check_out_status = fields.Selection([
        ('early', 'Early'),
        ('normal', 'Normal'),
        ('late', 'Late'),
        ('pending', 'Pending')
    ], string="Check-out Status", compute="_compute_check_in_out_status", store=True)

    @api.depends('check_in', 'check_out', 'employee_id.company_id.attendance_start_time', 'employee_id.company_id.attendance_end_time', 'employee_id.company_id.attendance_late_time', 'employee_id.company_id.attendance_late_check_out')
    def _compute_check_in_out_status(self):
        for att in self:
            company = att.employee_id.company_id or self.env.company
            user_tz = pytz.timezone(self.env.user.tz or 'UTC')
            
            c_start = company.attendance_start_time
            c_late = company.attendance_late_time
            c_end = company.attendance_end_time
            c_late_out = company.attendance_late_check_out
            
            # Check-in Status
            if att.check_in:
                check_in_local = att.check_in.replace(tzinfo=pytz.utc).astimezone(user_tz)
                check_in_hour = check_in_local.hour + check_in_local.minute / 60.0
                if check_in_hour < c_start:
                    att.check_in_status = 'early'
                elif check_in_hour >= c_late:
                    att.check_in_status = 'late'
                else:
                    att.check_in_status = 'normal'
            else:
                att.check_in_status = False
                
            # Check-out Status
            if att.check_out:
                check_out_local = att.check_out.replace(tzinfo=pytz.utc).astimezone(user_tz)
                check_out_hour = check_out_local.hour + check_out_local.minute / 60.0
                if check_out_hour < c_end:
                    att.check_out_status = 'early'
                elif check_out_hour >= c_late_out:
                    att.check_out_status = 'late'
                else:
                    att.check_out_status = 'normal'
            elif att.check_in:
                att.check_out_status = 'pending'
            else:
                att.check_out_status = False

    @api.model
    def get_dashboard_stats(self, date_str):

        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        employees = self.env['hr.employee'].search([('company_id', '=', self.env.company.id)])
        total_employees = len(employees)
        
        user_tz_str = self.env.user.tz or 'UTC'
        try:
            user_tz = pytz.timezone(user_tz_str)
        except pytz.UnknownTimeZoneError:
            user_tz = pytz.UTC

        start_dt = user_tz.localize(datetime.combine(date_obj, time.min)).astimezone(pytz.utc).replace(tzinfo=None)
        end_dt = user_tz.localize(datetime.combine(date_obj, time.max)).astimezone(pytz.utc).replace(tzinfo=None)
        
        domain = [
            ('check_in', '>=', start_dt),
            ('check_in', '<=', end_dt),
            ('employee_id.company_id', '=', self.env.company.id)
        ]
        attendances = self.search(domain)
        
        company = self.env.company
        c_start = company.attendance_start_time
        c_end = company.attendance_end_time
        c_late = company.attendance_late_time
        c_late_out = company.attendance_late_check_out
        c_req_hours = company.attendance_required_hours
        
        active_today = 0
        for emp_id in attendances.mapped('employee_id'):
            emp_attendances = attendances.filtered(lambda a: a.employee_id == emp_id)
            total_worked = sum(emp_attendances.mapped('worked_hours'))
            if any(not a.check_out for a in emp_attendances) or total_worked >= c_req_hours:
                active_today += 1
                
        absent_today = total_employees - active_today
        if absent_today < 0:
            absent_today = 0
            
        early_check_in = 0
        late_check_in = 0
        early_check_out = 0
        late_check_out = 0
        
        for att in attendances:
            if att.check_in:
                check_in_local = att.check_in.replace(tzinfo=pytz.utc).astimezone(user_tz)
                check_in_hour = check_in_local.hour + check_in_local.minute / 60.0
                
                if check_in_hour < c_start:
                    early_check_in += 1
                if check_in_hour >= c_late:
                    late_check_in += 1
                    
            if att.check_out:
                check_out_local = att.check_out.replace(tzinfo=pytz.utc).astimezone(user_tz)
                check_out_hour = check_out_local.hour + check_out_local.minute / 60.0
                
                if check_out_hour >= c_late_out:
                    late_check_out += 1
                if check_out_hour < c_end:
                    early_check_out += 1

        # --- RECENT ACTIVITY ---
        recent_activity_limit = 5
        recent_attendances = self.search([
            ('employee_id.company_id', '=', self.env.company.id)
        ], limit=recent_activity_limit, order='check_in desc')
        
        recent_list = []
        for att in recent_attendances:
            recent_list.append({
                'employee_name': att.employee_id.name,
                'check_in': att.check_in.replace(tzinfo=pytz.utc).astimezone(user_tz).strftime('%Y-%m-%d %H:%M:%S') if att.check_in else '',
                'check_out': att.check_out.replace(tzinfo=pytz.utc).astimezone(user_tz).strftime('%Y-%m-%d %H:%M:%S') if att.check_out else '',
            })
            
        # --- PIE CHART (Active vs Absent) ---
        pie_data = {
            'labels': ['Active Today', 'Absent Today'],
            'datasets': [{
                'data': [active_today, absent_today],
                'backgroundColor': ['#1cc88a', '#e74a3b'],
            }]
        }

        # --- BAR CHART (Check-ins per day for the last 7 days) ---
        bar_labels = []
        bar_data_points = []
        import datetime as dt
        for i in range(6, -1, -1):
            day_obj = date_obj - dt.timedelta(days=i)
            day_str = day_obj.strftime("%b %d")
            bar_labels.append(day_str)
            
            day_start = user_tz.localize(datetime.combine(day_obj, time.min)).astimezone(pytz.utc).replace(tzinfo=None)
            day_end = user_tz.localize(datetime.combine(day_obj, time.max)).astimezone(pytz.utc).replace(tzinfo=None)
            
            day_count = self.search_count([
                ('check_in', '>=', day_start),
                ('check_in', '<=', day_end),
                ('employee_id.company_id', '=', self.env.company.id)
            ])
            bar_data_points.append(day_count)
            
        bar_data = {
            'labels': bar_labels,
            'datasets': [{
                'label': 'Check-ins',
                'data': bar_data_points,
                'backgroundColor': '#4e73df',
            }]
        }

        # --- LATE CHECK-INS TODAY ---
        late_list = []
        for att in attendances:
            if att.check_in:
                check_in_local = att.check_in.replace(tzinfo=pytz.utc).astimezone(user_tz)
                check_in_hour = check_in_local.hour + check_in_local.minute / 60.0
                if check_in_hour >= c_late:
                    delay_mins = int((check_in_hour - c_late) * 60)
                    late_list.append({
                        'employee_name': att.employee_id.name,
                        'check_in': check_in_local.strftime('%H:%M'),
                        'delay_mins': delay_mins
                    })

        return {
            'total_employees': total_employees,
            'active_today': active_today,
            'absent_today': absent_today,
            'early_check_in': early_check_in,
            'late_check_in': late_check_in,
            'early_check_out': early_check_out,
            'late_check_out': late_check_out,
            'pie_chart': pie_data,
            'bar_chart': bar_data,
            'recent_activity': recent_list,
            'late_check_ins': late_list,
        }
