# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order.line"

    def _get_route_area_location(self):
        self.ensure_one()
        return self.order_id.route_area_id.location_id

    def _get_location_final(self):
        location = super()._get_location_final()
        ra_location = self._get_route_area_location()
        return ra_location or location
