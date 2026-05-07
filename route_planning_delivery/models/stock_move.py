# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_route_area(self):
        if (
            self.group_id.sale_id
            and self.group_id.sale_id.carrier_id
            and self.group_id.sale_id.carrier_id.delivery_type != "route_planning"
        ):
            return self.env["route.area"]
        return super()._get_route_area()

    def _get_picking_carrier(self, carrier_id):
        """Get the carrier to be assigned to the picking."""
        return carrier_id

    def _get_new_picking_values(self):
        vals = super()._get_new_picking_values()
        # Override carrier assignment to picking
        # to easily customize it in inherited modules
        vals["carrier_id"] = self._get_picking_carrier(vals.get("carrier_id"))
        return vals
