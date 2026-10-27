# Copyright 2025-2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_route_area(self):
        # Return the route area to be used from RMA
        if self.rma_receiver_ids:
            return self.sudo().rma_receiver_ids[0].reception_route_area_id
        elif (
            not self.rma_id
            and self.move_orig_ids
            and any(move.rma_receiver_ids for move in self.move_orig_ids)
        ):
            # Although route_planning_stock could handle this part, it is not possible
            # because the condition for route_planning_sale_stock would be met, and
            # the route_area_id for the sale would be retrieved incorrectly.
            move = self.move_orig_ids.sudo().filtered(lambda x: x.rma_receiver_ids)[0]
            return move.picking_id.route_area_id
        elif self.rma_id:
            return self.sudo().rma_id.route_area_id
        return super()._get_route_area()

    def _get_stock_move_vals_from_record_route_area(self):
        vals = super()._get_stock_move_vals_from_record_route_area()
        if not self.rma_id and not self.rma_receiver_ids:
            return vals
        rule = self.rule_id
        if self.rma_id:
            location_final = self.rma_id._get_location_final()
        else:
            location_final = fields.first(self.rma_receiver_ids).location_id
        if self.location_final_id:
            rules = rule.route_id.rule_ids.filtered(
                lambda r: r.action != "push"
                and r.location_src_id == rule.location_src_id
                and r.location_dest_id == location_final
                and r.procure_method == rule.procure_method
            )
        else:
            rules = rule.route_id.rule_ids.filtered(
                lambda r: r.location_src_id == location_final
                and r.location_dest_id == rule.location_dest_id
                and r.procure_method == rule.procure_method
            )
        new_rule = rules[:1]
        if new_rule:
            vals["rule_id"] = new_rule.id
            vals["location_id"] = new_rule.location_src_id.id
            if new_rule.location_dest_from_rule or not self._get_route_area():
                # Although the _compute_location_dest_id() method in stock.move uses
                # this data, it does not have the appropriate "depends" field, and
                # we do not want to add it; therefore, we must change it manually
                vals["location_dest_id"] = new_rule.location_dest_id.id
            if self.location_final_id:
                vals["location_final_id"] = location_final.id
        return vals

    def _set_locations_from_record_route_area(self):
        # We define the appropriate destination location associated with the rma
        res = super()._set_locations_from_record_route_area()
        for item in self.filtered(lambda x: x.rma_id or x.rma_receiver_ids):
            vals = item._get_stock_move_vals_from_record_route_area()
            if vals:
                item.write(vals)
        return res
