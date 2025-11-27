{
    "name": "account_discount",
    "summary": """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    "author": "Ricardo Perez",
    "website": "https://github.com/ric98esley/test_addons",
    "category": "Account",
    "version": "16.0.0.0.1",
    # any module necessary for this one to work correctly
    "depends": ["base", "account"],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_type.xml",
        "views/res_partner_id.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
