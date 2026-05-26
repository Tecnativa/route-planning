# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from odoo.addons.route_planning.tests.common import RouteCommon


class TestRoutePlanningRmaCommon(RouteCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.area_north.warehouse_id = cls.warehouse
        cls.area_south.warehouse_id = cls.warehouse
        cls.product_a = cls.env["product.product"].create(
            {"name": "Product A", "is_storable": True}
        )
        # Create quants for products to ensure stock availability
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product_a.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 10.0,
            }
        )
        # Create sale order
        order_form = Form(cls.env["sale.order"])
        order_form.partner_id = cls.partner_1
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.product_a
        cls.order = order_form.save()

    @classmethod
    def _rma_sale_wizard(cls, order):
        wizard_id = order.action_create_rma()["res_id"]
        wizard = cls.env["sale.order.rma.wizard"].browse(wizard_id)
        wizard.operation_id = cls.env.ref("rma.rma_operation_replace")
        return wizard
