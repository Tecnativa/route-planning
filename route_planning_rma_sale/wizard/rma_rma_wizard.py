# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RmaRmaWizard(models.TransientModel):
    _inherit = "rma.rma.wizard"

    delivery_type = fields.Selection(related="reception_carrier_id.delivery_type")
    reception_route_area_id = fields.Many2one(
        comodel_name="route.area",
        string="Reception route area",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        rma_id = self.env.context.get("active_id")
        rma = self.env["rma"].browse(rma_id)
        if rma:
            res.update(
                reception_route_area_id=rma.reception_route_area_id.id,
            )
        return res

    @api.onchange("reception_carrier_id")
    def _onchange_reception_carrier_id(self):
        if self.reception_carrier_id.delivery_type != "route_planning":
            self.reception_route_area_id = False

    def _stock_return_picking_vals(self, picking):
        vals = super()._stock_return_picking_vals(picking)
        if self.reception_route_area_id:
            vals["reception_route_area_id"] = self.reception_route_area_id.id
        return vals
