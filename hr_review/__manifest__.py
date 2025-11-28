{
    "name": "HR Performance Review",
    "summary": """
                HR Performance Review Module
        =============================

        Manage employee performance evaluations with comprehensive tracking:

        Features:
        ---------
        * Create and track performance reviews for employees
        * Record scores, strengths, weaknesses, and comments
        * Set goals for next evaluation period
        * Track review status (pending/completed)
        * Kanban view for visual workflow management
        * Generate PDF reports with performance history
        * Search and filter by employee, department, score, and status

        This module integrates with the HR module to provide a complete
        performance management solution.
    """,
    "author": "Ricardo Perez",
    "website": "https://github.com/ric98esley/test_addons",
    "category": "Human Resources",
    "version": "16.0.1.0.0",
    "depends": ["base", "hr", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
        "report/performance_review_report.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}
