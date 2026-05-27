# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderRmaWizard(models.TransientModel):
    _inherit = "sale.order.rma.wizard"

    reception_route_area_id = fields.Many2one(
        comodel_name="route.area",
        string="Reception route area",
    )
    reception_carrier_delivery_type = fields.Selection(
        related="reception_carrier_id.delivery_type"
    )
    location_id = fields.Many2one(compute="_compute_location_id", store=True)

    @api.depends("reception_carrier_id", "reception_route_area_id")
    def _compute_location_id(self):
        for item in self:
            if item.reception_route_area_id:
                item.location_id = item.reception_route_area_id.location_id
            else:
                item.location_id = item.order_id.warehouse_id.rma_loc_id

    @api.onchange("reception_carrier_id")
    def _onchange_reception_carrier_id(self):
        if self.reception_carrier_id.delivery_type != "route_planning":
            self.reception_route_area_id = False


class SaleOrderLineRmaWizard(models.TransientModel):
    _inherit = "sale.order.line.rma.wizard"

    def _prepare_rma_values(self):
        values = super()._prepare_rma_values()
        if self.wizard_id.reception_route_area_id:
            values["reception_route_area_id"] = (
                self.wizard_id.reception_route_area_id.id
            )
        return values
