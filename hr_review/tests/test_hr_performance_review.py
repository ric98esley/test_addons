from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHrPerformanceReview(TransactionCase):
    def setUp(self):
        super(TestHrPerformanceReview, self).setUp()

        # Create test employees
        self.employee_model = self.env["hr.employee"]
        self.review_model = self.env["hr.performance.review"]

        self.employee_1 = self.employee_model.create(
            {
                "name": "Test Employee 1",
            }
        )

        self.employee_2 = self.employee_model.create(
            {
                "name": "Test Employee 2",
            }
        )

        self.reviewer = self.employee_model.create(
            {
                "name": "Test Reviewer",
            }
        )

    def test_create_review(self):
        """Test creation of performance review with valid data"""
        review = self.review_model.create(
            {
                "employee_id": self.employee_1.id,
                "reviewer_id": self.reviewer.id,
                "score": 85.5,
                "comments": "Excellent performance",
                "strengths": "Great communication skills",
                "weaknesses": "Time management could improve",
                "goals_next_period": "Complete advanced training",
            }
        )

        self.assertTrue(review)
        self.assertEqual(review.employee_id, self.employee_1)
        self.assertEqual(review.reviewer_id, self.reviewer)
        self.assertEqual(review.score, 85.5)
        self.assertEqual(review.state, "pending")

    def test_review_employee_relation(self):
        """Test correct linking with employee"""
        review = self.review_model.create(
            {
                "employee_id": self.employee_1.id,
                "reviewer_id": self.reviewer.id,
                "score": 75.0,
            }
        )

        self.assertEqual(review.employee_id.id, self.employee_1.id)
        self.assertEqual(review.employee_id.name, "Test Employee 1")

    def test_review_state_workflow(self):
        """Test state changes from pending to completed"""
        review = self.review_model.create(
            {
                "employee_id": self.employee_1.id,
                "reviewer_id": self.reviewer.id,
                "score": 90.0,
            }
        )

        # Initial state should be pending
        self.assertEqual(review.state, "pending")

        # Complete the review
        review.action_complete()
        self.assertEqual(review.state, "completed")

        # Reset to pending
        review.action_reset_to_pending()
        self.assertEqual(review.state, "pending")

    def test_review_score_constraint(self):
        """Test score validation (must be 0-100)"""
        # Test score > 100
        with self.assertRaises(ValidationError):
            self.review_model.create(
                {
                    "employee_id": self.employee_1.id,
                    "reviewer_id": self.reviewer.id,
                    "score": 150.0,
                }
            )

        # Test negative score
        with self.assertRaises(ValidationError):
            self.review_model.create(
                {
                    "employee_id": self.employee_1.id,
                    "reviewer_id": self.reviewer.id,
                    "score": -10.0,
                }
            )

        # Test valid score
        review = self.review_model.create(
            {
                "employee_id": self.employee_1.id,
                "reviewer_id": self.reviewer.id,
                "score": 50.0,
            }
        )
        self.assertTrue(review)

    def test_review_search_groupby(self):
        """Test search and grouping by state"""
        # Create multiple reviews with different states
        review1 = self.review_model.create(
            {
                "employee_id": self.employee_1.id,
                "reviewer_id": self.reviewer.id,
                "score": 80.0,
                "state": "pending",
            }
        )

        review2 = self.review_model.create(
            {
                "employee_id": self.employee_2.id,
                "reviewer_id": self.reviewer.id,
                "score": 90.0,
                "state": "pending",
            }
        )
        review2.action_complete()

        # Search for pending reviews
        pending_reviews = self.review_model.search([("state", "=", "pending")])
        self.assertEqual(len(pending_reviews), 1)
        self.assertIn(review1, pending_reviews)

        # Search for completed reviews
        completed_reviews = self.review_model.search([("state", "=", "completed")])
        self.assertEqual(len(completed_reviews), 1)
        self.assertIn(review2, completed_reviews)

    def test_review_name_get(self):
        """Test custom name_get method"""
        review = self.review_model.create(
            {
                "employee_id": self.employee_1.id,
                "reviewer_id": self.reviewer.id,
                "score": 80.0,
            }
        )

        name = review.name_get()[0][1]
        self.assertIn(self.employee_1.name, name)
        self.assertIn(str(review.review_date), name)

    def test_review_related_fields(self):
        """Test related fields (department, job position)"""
        # Create department and job
        department = self.env["hr.department"].create(
            {
                "name": "Test Department",
            }
        )

        job = self.env["hr.job"].create(
            {
                "name": "Test Job",
            }
        )

        # Update employee
        self.employee_1.write(
            {
                "department_id": department.id,
                "job_id": job.id,
            }
        )

        # Create review
        review = self.review_model.create(
            {
                "employee_id": self.employee_1.id,
                "reviewer_id": self.reviewer.id,
                "score": 80.0,
            }
        )

        self.assertEqual(review.employee_department_id, department)
        self.assertEqual(review.employee_job_id, job)
