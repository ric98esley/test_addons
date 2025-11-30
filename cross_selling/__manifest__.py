{
    "name": "Cross Selling",
    "summary": """
        Cross Selling, Allow to add cross selling products to the sale order""",
    "author": "Ricardo Perez",
    "website": "https://github.com/ric98esley/test_addons",
    "category": "Sales",
    "version": "16.0.0.0.1",
    "depends": ["base", "sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/cross_selling_view.xml",
        "views/sale_order_view.xml",
        "wizard/cross_selling_wizard_view.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
