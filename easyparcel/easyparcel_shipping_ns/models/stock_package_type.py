# -*- coding: utf-8 -*-
from odoo import fields, models, api


class StockPackageType(models.Model):
    _inherit = 'stock.package.type'

    package_carrier_type = fields.Selection(selection_add=[("easyparcel_ns", "Easyparcel")],
                                            ondelete={'easyparcel_ns': 'set default'})
