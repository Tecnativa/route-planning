# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class RouteArea(models.Model):
    _inherit = "route.area"

    def _create_or_update_rule(self):
        res = super()._create_or_update_rule()
        StockRule = self.env["stock.rule"].sudo()
        warehouse = self.warehouse_id
        customer_loc, _supplier_loc = warehouse._get_partner_locations()
        routing_out1 = warehouse.Routing(
            warehouse.rma_loc_id, self.location_id, warehouse.rma_out_type_id, "pull"
        )
        routing_out2 = warehouse.Routing(
            self.location_id, customer_loc, warehouse.rma_out_type_id, "push"
        )
        routing_in1 = warehouse.Routing(
            customer_loc, self.location_id, warehouse.rma_in_type_id, "pull"
        )
        routing_in2 = warehouse.Routing(
            self.location_id, warehouse.rma_loc_id, warehouse.rma_in_type_id, "push"
        )
        rule_vals = [
            warehouse._prepare_stock_rule_values(
                warehouse.rma_out_route_id, routing_out1, "make_to_stock", True
            ),
            warehouse._prepare_stock_rule_values(
                warehouse.rma_out_route_id, routing_out2, "make_to_order", False
            ),
            warehouse._prepare_stock_rule_values(
                warehouse.rma_in_route_id, routing_in1, "make_to_stock", True
            ),
            warehouse._prepare_stock_rule_values(
                warehouse.rma_in_route_id, routing_in2, "make_to_stock", False
            ),
        ]
        for rule_val in rule_vals:
            existing_rule = StockRule.with_context(active_test=False).search(
                [
                    ("picking_type_id", "=", rule_val["picking_type_id"]),
                    ("location_src_id", "=", rule_val["location_src_id"]),
                    ("location_dest_id", "=", rule_val["location_dest_id"]),
                    ("route_id", "=", rule_val["route_id"]),
                    ("action", "=", rule_val["action"]),
                ]
            )
            if not existing_rule:
                StockRule.create(rule_val)
            else:
                existing_rule.write(rule_val)
        return res
