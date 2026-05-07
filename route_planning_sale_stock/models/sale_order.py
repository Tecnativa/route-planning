# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    route_area_id = fields.Many2one(
        "route.area",
        compute="_compute_route_area_id",
        store=True,
        readonly=False,
        tracking=True,
    )

    @api.depends("partner_shipping_id", "company_id")
    def _compute_route_area_id(self):
        for order in self:
            company = order.company_id or self.env.company
            partner = order.partner_shipping_id.with_company(company)
            order.route_area_id = partner.route_area_id
