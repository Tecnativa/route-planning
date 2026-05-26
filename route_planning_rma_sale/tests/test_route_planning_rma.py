# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from .common import TestRoutePlanningRmaCommon


class TestRoutePlanningRma(TestRoutePlanningRmaCommon):
    def test_rma_with_route_area(self):
        self.order.action_confirm()
        self.assertEqual(self.order.state, "sale")
        picking = self.order.picking_ids
        self.assertEqual(picking.route_area_id, self.area_north)
        self.assertEqual(picking.location_dest_id, self.area_north.location_id)
        self.assertFalse(picking.has_route_planning)
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        next_picking = picking._get_next_transfers()
        self.assertTrue(next_picking)
        self.assertEqual(next_picking.route_area_id, self.area_north)
        self.assertEqual(next_picking.location_id, self.area_north.location_id)
        self.assertTrue(next_picking.has_route_planning)
        next_picking.button_validate()
        self.assertEqual(next_picking.state, "done")
        # Create rma
        wizard = self._rma_sale_wizard(self.order)
        rma = self.env["rma"].browse(wizard.create_and_open_rma()["res_id"])
        self.assertTrue(rma)
        self.assertEqual(rma.state, "confirmed")
        rma.reception_route_area_id = self.area_north
        rma.reception_move_id.quantity = rma.product_uom_qty
        reception_picking = rma.reception_move_id.picking_id
        reception_picking.button_validate()
        # Create return
        rma.route_area_id = self.area_south
        res = rma.action_return()
        wizard_form = Form(self.env[res["res_model"]].with_context(**res["context"]))
        wizard = wizard_form.save()
        wizard.action_deliver()
        self.assertTrue(rma.delivery_move_ids.picking_id)
        rma_picking = rma.delivery_move_ids.picking_id
        self.assertEqual(rma_picking.route_area_id, self.area_south)
        self.assertEqual(rma_picking.location_dest_id, self.area_south.location_id)
        # Change route area
        rma.route_area_id = self.area_north
        self.assertEqual(rma_picking.route_area_id, self.area_north)
        self.assertEqual(rma_picking.location_dest_id, self.area_north.location_id)
        rma_picking.button_validate()
        self.assertEqual(rma_picking.state, "done")
        next_rma_picking = rma_picking._get_next_transfers()
        self.assertTrue(next_rma_picking)
        self.assertEqual(next_rma_picking.route_area_id, self.area_north)
        self.assertEqual(next_rma_picking.location_id, self.area_north.location_id)
        next_rma_picking.button_validate()
        self.assertEqual(next_rma_picking.state, "done")

    def test_rma_without_route_area(self):
        self.partner_1.route_area_id = False
        self.order.route_area_id = False
        self.order.action_confirm()
        self.assertEqual(self.order.state, "sale")
        picking = self.order.picking_ids
        self.assertFalse(picking.route_area_id)
        self.assertNotEqual(picking.location_dest_id, self.area_north.location_id)
        self.assertFalse(picking.has_route_planning)
        picking.button_validate()
        self.assertEqual(picking.state, "done")
        next_picking = picking._get_next_transfers()
        self.assertFalse(next_picking)
        # Create rma
        wizard = self._rma_sale_wizard(self.order)
        rma = self.env["rma"].browse(wizard.create_and_open_rma()["res_id"])
        self.assertTrue(rma)
        self.assertEqual(rma.state, "confirmed")
        rma.reception_move_id.quantity = rma.product_uom_qty
        rma.reception_move_id.picking_id.button_validate()
        # Create return
        res = rma.action_return()
        wizard_form = Form(self.env[res["res_model"]].with_context(**res["context"]))
        wizard = wizard_form.save()
        wizard.action_deliver()
        self.assertTrue(rma.delivery_move_ids.picking_id)
        rma_picking = rma.delivery_move_ids.picking_id
        self.assertFalse(rma_picking.route_area_id)
        self.assertNotEqual(rma_picking.location_dest_id, self.area_north.location_id)
        rma_picking.button_validate()
        self.assertEqual(rma_picking.state, "done")
        next_rma_picking = rma_picking._get_next_transfers()
        self.assertFalse(next_rma_picking)
