# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_route_area(self):
        # Return the route area to be used from RMA
        if self.rma_receiver_ids:
            return self.sudo().rma_receiver_ids[0].reception_route_area_id
        elif self.rma_id:
            return self.sudo().rma_id.route_area_id
        return super()._get_route_area()

    def _set_location_dest_from_rma(self):
        """A method that is called when defining a route area in an RMA and
        allows you to specify the appropriate destination location in the moves
        (if the route area has been changed or if it previously had one and no
        longer does).
        """
        for item in self:
            if not item.rma_id:
                continue
            custom_location = item.sudo().rma_id._get_location_final()
            if item.location_dest_id == custom_location:
                continue
            item.location_dest_id = custom_location
            if item.picking_id and item.picking_id.location_dest_id != custom_location:
                item.picking_id.location_dest_id = custom_location
