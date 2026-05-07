# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_route_area_location(self):
        location = super()._get_route_area_location()
        if (
            self.order_id.carrier_id
            and self.order_id.carrier_id.delivery_type != "route_planning"
        ):
            return self.env["stock.location"]
        return location
