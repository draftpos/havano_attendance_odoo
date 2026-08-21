/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadBundle } from "@web/core/assets";
import { Component, useState, onWillStart, onMounted, onPatched } from "@odoo/owl";

export class AttendanceDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        
        const tzOffset = (new Date()).getTimezoneOffset() * 60000;
        const localISOTime = (new Date(Date.now() - tzOffset)).toISOString().slice(0, 10);
        
        this.state = useState({
            date: localISOTime,
            stats: null,
        });

        this.pieChart = null;
        this.barChart = null;

        onWillStart(async () => {
            await loadBundle("web.chartjs_lib");
            await this.fetchDashboardStats();
        });

        onMounted(() => {
            this.renderCharts();
        });

        onPatched(() => {
            this.renderCharts();
        });
    }

    async fetchDashboardStats() {
        const stats = await this.orm.call("hr.attendance", "get_dashboard_stats", [this.state.date]);
        this.state.stats = stats;
    }

    async onDateChange(ev) {
        this.state.date = ev.target.value;
        await this.fetchDashboardStats();
    }

    renderCharts() {
        if (!this.state.stats) return;

        const pieCanvas = document.getElementById("attendancePieChart");
        if (pieCanvas) {
            if (this.pieChart) {
                this.pieChart.destroy();
            }
            this.pieChart = new Chart(pieCanvas, {
                type: 'pie',
                data: this.state.stats.pie_chart,
                options: {
                    maintainAspectRatio: false,
                    responsive: true,
                }
            });
        }

        const barCanvas = document.getElementById("attendanceBarChart");
        if (barCanvas) {
            if (this.barChart) {
                this.barChart.destroy();
            }
            this.barChart = new Chart(barCanvas, {
                type: 'bar',
                data: this.state.stats.bar_chart,
                options: {
                    maintainAspectRatio: false,
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }
}

AttendanceDashboard.template = "havano_attendance_odoo.AttendanceDashboard";

registry.category("actions").add("havano_attendance_odoo.dashboard", AttendanceDashboard);
