# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Technical field to display the route area in the sale order form
    delivery_type = fields.Selection(related="carrier_id.delivery_type")

    def write(self, vals):
        # Ensure that the route area is cleared
        # when changing to a non-route planning carrier
        if "carrier_id" in vals:
            carrier = self.env["delivery.carrier"].browse(vals["carrier_id"])
            if carrier.delivery_type != "route_planning":
                vals["route_area_id"] = False
        return super().write(vals)
