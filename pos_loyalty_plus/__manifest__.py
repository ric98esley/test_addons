{
    "name": "Pos loyalty Plus",
    "summary": """
        Add loyalty points views and extra logic
    """,
    "author": "Ricardo Perez",
    "website": "https://github.com/ric98esley/test_addons",
    "category": "Point of Sale",
    "version": "16.0.0.0.1",
    "depends": ["point_of_sale", "pos_loyalty"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/pos_config_views.xml",
        "views/pos_session_views.xml",
        "wizard/loyalty_report_wizard_view.xml",
        "report/loyalty_report.xml",
        "report/loyalty_history_period_report.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "license": "LGPL-3",
    "auto_install": True,
}
