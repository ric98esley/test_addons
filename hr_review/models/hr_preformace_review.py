from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrPerformanceReview(models.Model):
    _name = "hr.performance.review"
    _description = "Employee Performance Review"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "review_date desc"
    _rec_name = "employee_id"

    # Basic Information
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        ondelete="cascade",
        index=True,
        help="Employee being evaluated",
    )
    review_date = fields.Date(
        required=True,
        default=fields.Date.context_today,
        help="Date when the review was conducted",
    )
    reviewer_id = fields.Many2one(
        "hr.employee",
        string="Reviewer",
        required=True,
        ondelete="restrict",
        help="Employee conducting the review",
    )

    # Evaluation
    score = fields.Float(digits=(5, 2), help="Performance score (0-100)")
    comments = fields.Text(help="Qualitative observations about performance")
    strengths = fields.Text(help="Employee strengths and positive aspects")
    weaknesses = fields.Text(
        string="Areas for Improvement", help="Areas where the employee can improve"
    )
    goals_next_period = fields.Text(
        help="Objectives and goals for the next evaluation cycle",
    )

    # Workflow
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("completed", "Completed"),
        ],
        string="Status",
        default="pending",
        required=True,
        tracking=True,
        help="Review status",
    )

    # Computed fields
    employee_department_id = fields.Many2one(
        "hr.department",
        string="Department",
        related="employee_id.department_id",
        store=True,
        readonly=True,
    )
    employee_job_id = fields.Many2one(
        "hr.job",
        string="Job Position",
        related="employee_id.job_id",
        store=True,
        readonly=True,
    )

    _sql_constraints = [
        (
            "score_range",
            "CHECK(score >= 0 AND score <= 100)",
            "Score must be between 0 and 100!",
        ),
    ]

    @api.constrains("score")
    def _check_score(self):
        """Validate score is within valid range"""
        for review in self:
            if review.score and (review.score < 0 or review.score > 100):
                raise ValidationError(_("Score must be between 0 and 100!"))

    @api.constrains("employee_id", "reviewer_id")
    def _check_reviewer_different(self):
        """Optionally validate that reviewer is different from employee"""
        # This is commented out to allow self-reviews if needed
        # for review in self:
        #     if review.employee_id == review.reviewer_id:
        #         raise ValidationError('Employee cannot review themselves!')

    def action_complete(self):
        """Mark review as completed"""
        self.write({"state": "completed"})
        return True

    def action_reset_to_pending(self):
        """Reset review to pending state"""
        self.write({"state": "pending"})
        return True

    def name_get(self):
        """Custom display name"""
        result = []
        for review in self:
            name = f"{review.employee_id.name} - {review.review_date}"
            result.append((review.id, name))
        return result
