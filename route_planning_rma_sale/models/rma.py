# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Rma(models.Model):
    _inherit = "rma"

    reception_carrier_delivery_type = fields.Selection(
        related="reception_carrier_id.delivery_type",
        string="Reception carrier delivery type",
    )
    reception_route_area_id = fields.Many2one(
        comodel_name="route.area", string="Reception route area"
    )
    carrier_id = fields.Many2one(
        inverse="_inverse_carrier_id",
    )
    carrier_delivery_type = fields.Selection(
        related="carrier_id.delivery_type", string="Carrier delivery type"
    )
    route_area_id = fields.Many2one(
        comodel_name="route.area",
        string="Delivery route area",
        compute="_compute_route_area_id",
        inverse="_inverse_route_area_id",
        store=True,
        readonly=False,
    )

    @api.depends("partner_shipping_id", "company_id")
    def _compute_route_area_id(self):
        for rma in self:
            company = rma.company_id or self.env.company
            partner = rma.partner_shipping_id.with_company(company)
            rma.route_area_id = partner.route_area_id

    def _inverse_carrier_id(self):
        self._set_delivery_location_dest()

    def _inverse_route_area_id(self):
        self._set_delivery_location_dest()

    def _set_delivery_location_dest(self):
        for item in self.filtered("delivery_move_ids"):
            moves = item.delivery_move_ids.filtered(
                lambda x: x.state not in ("done", "cancel")
            )
            if moves:
                moves._set_location_dest_from_rma()

    @api.onchange("reception_route_area_id", "order_id")
    def onchange_reception_route_area_id(self):
        if self.reception_route_area_id:
            self.location_id = self.reception_route_area_id.location_id
        else:
            self.location_id = self.order_id.warehouse_id.rma_loc_id

    def _get_route_area(self):
        """Return the route area to be used in deliveries."""
        self.ensure_one()
        return self.route_area_id

    def _get_location_final(self):
        location = super()._get_location_final()
        route_area = self._get_route_area()
        return route_area.location_id or location
