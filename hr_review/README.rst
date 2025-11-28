==========================
HR Performance Review
==========================

Employee Performance Review and Evaluation Management for Odoo 16

.. contents::
   :local:

Overview
========

This module extends Odoo's HR functionality to provide comprehensive performance review and evaluation management for employees. It enables HR managers and supervisors to create, track, and analyze employee performance reviews with detailed metrics and goal setting.

Features
========

Core Functionality
------------------

* **Performance Review Management**: Create and manage employee performance reviews with detailed evaluation criteria
* **Scoring System**: Numerical scoring system (0-100) with validation
* **Comprehensive Evaluation**: Track strengths, weaknesses, comments, and goals
* **Workflow States**: Two-state workflow (Pending/Completed) for review lifecycle
* **Employee Relations**: Full integration with Odoo's HR employee module

Views and Navigation
--------------------

* **Form View**: Detailed review form with organized sections
* **Tree View**: List view with key information and color-coded states
* **Kanban View**: Visual board grouped by status with score-based color coding
* **Search and Filters**: Advanced search with filters by score ranges, status, and date
* **Menu Structure**: Dedicated "Performance Reviews" menu under HR with filtered submenus

Reporting
---------

* **PDF Report**: Comprehensive performance review report per employee
* **Historical Data**: View complete review history for each employee
* **Statistics**: Automatic calculation of average, highest, and latest scores
* **Detailed Breakdown**: Latest review details with strengths, weaknesses, and goals

Installation
============

1. Copy the ``hr_review`` folder to your Odoo addons directory
2. Update the apps list in Odoo
3. Search for "HR Performance Review" and click Install
4. The module depends on ``base``, ``hr``, and ``mail`` modules

Configuration
=============

No special configuration is required. Once installed:

1. Go to **HR ► Performance Reviews**
2. Start creating performance reviews for your employees

Usage
=====

Creating a Performance Review
------------------------------

1. Navigate to **HR ► Performance Reviews ► All Reviews**
2. Click **Create**
3. Select the employee being evaluated
4. Enter review date (defaults to today)
5. Select the reviewer
6. Enter the performance score (0-100)
7. Fill in evaluation details:
   
   * Strengths
   * Areas for improvement
   * Additional comments
   * Goals for next period

8. Save the review (status: Pending)
9. Click "Mark as Completed" when ready

Managing Reviews
----------------

* Use the **Kanban view** to visualize reviews by status
* Filter pending reviews using the **Pending Reviews** menu
* View completed reviews using the **Completed Reviews** menu
* Search and group by employee, department, reviewer, or score range

Generating Reports
------------------

1. Go to **HR ► Employees**
2. Select an employee
3. Click **Print ► Performance Review Report**
4. The PDF will include:
   
   * Employee information
   * Total number of reviews
   * Score statistics (average, highest, latest)
   * Complete review history
   * Detailed breakdown of each review

Technical Details
=================

Model Structure
---------------

``hr.performance.review``
~~~~~~~~~~~~~~~~~~~~~~~~~

Fields:

* ``employee_id``: Many2one to hr.employee (required)
* ``review_date``: Date (required, default: today)
* ``reviewer_id``: Many2one to hr.employee (required)
* ``score``: Float (0-100 range with validation)
* ``comments``: Text
* ``strengths``: Text
* ``weaknesses``: Text
* ``goals_next_period``: Text
* ``state``: Selection (pending/completed)
* ``employee_department_id``: Related field (stored)
* ``employee_job_id``: Related field (stored)

Security
--------

Access Rights:

* **HR User** (hr.group_hr_user): Read, Write, Create
* **HR Manager** (hr.group_hr_manager): Full access including Delete

Database Structure
------------------

* Inherits from mail.thread for chatter functionality
* SQL constraint for score range validation
* Python constraint for additional score validation
* Ordered by review_date descending

Known Issues / Roadmap
======================

* Future: Email notifications for review deadlines
* Future: Review templates for different job positions
* Future: 360-degree review functionality
* Future: Performance improvement plans integration

Credits
=======

Authors
-------

* Ricardo Perez

Contributors
------------

* Ricardo Perez

Maintainer
----------

This module is maintained by Ricardo Perez.

For support, please contact through the GitHub repository.
