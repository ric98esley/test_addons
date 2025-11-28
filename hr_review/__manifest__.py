{
    "name": "hr_review",
    "summary": """
        Allow to review employees
    """,
    "author": "Ricardo Perez",
    "website": "https://github.com/ric98esley/test_addons",
    "category": "Human Resources",
    "version": "16.0.0.0.1",
    "depends": ["base", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/templates.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "application": True,
    "installable": True,
    "license": "LGPL-3",
}
