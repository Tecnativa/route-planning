# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.route_planning.tests.common import RouteCommon


class TestRoutePlanningDelivery(RouteCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Product = cls.env["product.product"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.area_north.warehouse_id = cls.warehouse
        cls.area_south.warehouse_id = cls.warehouse
        cls.product_a = Product.create({"name": "Product A", "is_storable": True})
        carrier_product = Product.create(
            {"name": "Test shipping product", "type": "service"}
        )
        # Create quants for products to ensure stock availability
        cls.env["stock.quant"].create(
            {
                "product_id": cls.product_a.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 10.0,
            }
        )
        cls.carrier = cls.env["delivery.carrier"].create(
            {"name": "Test carrier", "product_id": carrier_product.id}
        )
        cls.carrier_route = cls.env["delivery.carrier"].create(
            {
                "name": "Test carrier route",
                "product_id": carrier_product.id,
                "delivery_type": "route_planning",
                "integration_level": "rate",
            }
        )
        order_form = Form(cls.env["sale.order"])
        order_form.partner_id = cls.partner_1
        with order_form.order_line.new() as line_form:
            line_form.product_id = cls.product_a
        cls.order = order_form.save()

    def _add_shipping_to_order(self, sale_order, carrier, route_area=None):
        action = sale_order.action_open_delivery_wizard()
        wizard_form = Form(
            self.env[action["res_model"]].with_context(**action["context"])
        )
        wizard_form.carrier_id = carrier
        if route_area:
            wizard_form.route_area_id = route_area
        wizard = wizard_form.save()
        wizard.button_confirm()

    def test_delivery_carrier_constrains(self):
        # test onchange delivery_type to route_planning
        self.assertEqual(self.carrier.delivery_type, "fixed")
        self.carrier.integration_level = "rate_and_ship"
        with Form(self.carrier) as carrier_form:
            carrier_form.delivery_type = "route_planning"
        self.assertEqual(self.carrier.integration_level, "rate")
        # test constrains delivery_type to route_planning and invalid integration_level
        with self.assertRaisesRegex(
            ValidationError, r"please change the integration level to ' Get rate'"
        ):
            self.carrier_route.integration_level = "rate_and_ship"

    def test_sale_order_with_carrier_send_shipper(self):
        """
        Test that sending to shipper with route planning carrier
        raises the appropriate ValidationError.
        """
        self._add_shipping_to_order(
            self.order, self.carrier_route, route_area=self.area_north
        )
        self.assertEqual(self.order.carrier_id, self.carrier_route)
        self.assertEqual(self.order.route_area_id, self.area_north)
        self.order.action_confirm()
        picking = self.order.picking_ids
        self.assertEqual(picking.route_area_id, self.area_north)
        self.assertEqual(picking.carrier_id, self.carrier_route)
        self.assertEqual(picking.location_dest_id, self.area_north.location_id)
        self.assertFalse(picking.has_route_planning)
        picking.button_validate()
        with self.assertRaisesRegex(ValidationError, r"cannot create shipments"):
            picking.send_to_shipper()

    def test_sale_order_with_carrier_and_route_area(self):
        self._add_shipping_to_order(
            self.order, self.carrier_route, route_area=self.area_north
        )
        self.assertEqual(self.order.carrier_id, self.carrier_route)
        self.assertEqual(self.order.route_area_id, self.area_north)
        self.order.action_confirm()
        picking = self.order.picking_ids
        self.assertEqual(picking.route_area_id, self.area_north)
        self.assertEqual(picking.carrier_id, self.carrier_route)
        self.assertEqual(picking.location_dest_id, self.area_north.location_id)
        self.assertFalse(picking.has_route_planning)
        picking.button_validate()
        next_picking = picking._get_next_transfers()
        self.assertEqual(next_picking.route_area_id, self.area_north)
        self.assertEqual(next_picking.carrier_id, self.carrier_route)
        self.assertEqual(next_picking.location_id, self.area_north.location_id)
        self.assertTrue(next_picking.has_route_planning)
        next_picking.button_validate()

    def test_sale_order_with_carrier_change_route_area(self):
        self._add_shipping_to_order(
            self.order, self.carrier_route, route_area=self.area_north
        )
        self.assertEqual(self.order.carrier_id, self.carrier_route)
        self.assertEqual(self.order.route_area_id, self.area_north)
        # change route area before confirming
        self.order.route_area_id = self.area_south
        self.order.action_confirm()
        picking = self.order.picking_ids
        self.assertEqual(picking.route_area_id, self.area_south)
        self.assertEqual(picking.carrier_id, self.carrier_route)
        self.assertEqual(picking.location_dest_id, self.area_south.location_id)
        self.assertFalse(picking.has_route_planning)
        picking.button_validate()
        next_picking = picking._get_next_transfers()
        self.assertEqual(next_picking.route_area_id, self.area_south)
        self.assertEqual(next_picking.carrier_id, self.carrier_route)
        self.assertEqual(next_picking.location_id, self.area_south.location_id)
        self.assertTrue(next_picking.has_route_planning)
        next_picking.button_validate()

    def test_sale_order_with_carrier_and_without_route_area(self):
        self._add_shipping_to_order(self.order, self.carrier)
        self.assertEqual(self.order.carrier_id, self.carrier)
        self.assertFalse(self.order.route_area_id)
        self.order.action_confirm()
        picking = self.order.picking_ids
        self.assertFalse(picking.route_area_id)
        self.assertNotEqual(picking.location_dest_id, self.area_north.location_id)
        self.assertFalse(picking.has_route_planning)
        picking.button_validate()
        next_picking = picking._get_next_transfers()
        self.assertFalse(next_picking)

    def test_sale_order_without_carrier_and_route_area(self):
        # asign the carrier and route area first
        # and remove the carrier later
        self._add_shipping_to_order(
            self.order, self.carrier_route, route_area=self.area_north
        )
        self.assertEqual(self.order.carrier_id, self.carrier_route)
        self.assertEqual(self.order.route_area_id, self.area_north)
        # remove delivery line
        delivery_line = self.order.order_line.filtered("is_delivery")
        delivery_line.unlink()
        self.assertFalse(self.order.carrier_id)
        self.assertFalse(self.order.route_area_id)
        self.order.action_confirm()
        picking = self.order.picking_ids
        self.assertFalse(picking.route_area_id)
        self.assertNotEqual(picking.location_dest_id, self.area_north.location_id)
        self.assertFalse(picking.has_route_planning)
        picking.button_validate()
        next_picking = picking._get_next_transfers()
        self.assertFalse(next_picking)
