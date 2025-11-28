{
    "name": "stock_alerts",
    "summary": """
        Generate alerts when stock levels are low""",
    "author": "Ricardo Perez",
    "website": "https://github.com/ric98esley/test_addons",
    "category": "Uncategorized",
    "version": "16.0.0.0.1",
    "depends": ["base", "stock", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/product_template_views.xml",
        "views/stock_alert_history_views.xml",
        "views/stock_alert_dashboard.xml",
        "views/menu_items.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
    "installable": True,
    "application": True,
    "license": "AGPL-3",
}
