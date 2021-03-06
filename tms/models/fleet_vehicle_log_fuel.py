# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# import time

from openerp import api, fields, models
from openerp.exceptions import UserError
# from openerp import netsvc
# import openerp.addons.decimal_precision as dp
# from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
# from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _


class FleetVehicleLogFuel(models.Model):
    _name = 'fleet.vehicle.log.fuel'
    _inherit = ['fleet.vehicle.log.fuel', 'mail.thread', 'ir.needaction_mixin']

    name = fields.Char(string='Name', size=64)
    product_id = fields.Many2one('product.product', string="Fuel",
                                 domain=[('purchase_ok', '=', True)])
    # currency_id = fields.Many2one(
    #     'res.currency', 'Currency', required=True,
    #     states={'cancel': [('readonly', True)],
    #             'confirmed': [('readonly', True)],
    #             'closed': [('readonly', True)]},
    #     default=(lambda self: self.env.user.company_id.currency_id.id))
    state = fields.Selection(
        [('draft', 'Draft'),
         ('approved', 'Approved'),
         ('confirmed', 'Confirmed'),
         ('closed', 'Closed'),
         ('cancel', 'Cancelled')],
        string='State', readonly=True, default='draft')
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', domain=[('tms_category', '=', 'driver')])
    # travel_id = fields.Many2one(
    #     'tms.travel', 'Travel', required=False,
    #     states={'cancel': [('readonly', True)],
    #             'confirmed': [('readonly', True)],
    #             'closed': [('readonly', True)]})
    tax_amount = fields.Float(string='Taxes')
    subtotal = fields.Float(string="Subtotal", compute='_subtotal')
    amount = fields.Float(string="Total", compute="_amount")
    # cancelled_by = fields.Many2one('res.users',
    # 'Cancelled by', readonly=True)
    # date_cancelled = fields.Datetime('Date Cancelled', readonly=True)
    # approved_by = fields.Many2one('res.users', 'Approved by', readonly=True)
    # date_approved = fields.Datetime('Date Approved', readonly=True)
    # confirmed_by = fields.Many2one('res.users', 'Confirmed by',
    # readonly=True)
    # date_confirmed = fields.Datetime('Date Confirmed', readonly=True)
    # closed_by = fields.Many2one('res.users', 'Closed by', readonly=True)
    # date_closed = fields.Datetime('Date Closed', readonly=True)
    # drafted_by = fields.Many2one('res.users', 'Drafted by', readonly=True)
    # date_drafted = fields.Datetime('Date Drafted', readonly=True)
    # invoice_id = fields.Many2one(
    #     'account.invoice', 'Invoice Record', readonly=True,
    #     domain=[('state', '!=', 'cancel')],)
    # invoiced = fields.Boolean(
    #     compute=_invoiced, method=True, string='Invoiced', multi='invoiced',
    #     store={
    #         'tms.fuelvoucher':
    #             (lambda self, cr, uid, ids, c={}: ids, None, 10),
    #         'account.invoice': (_get_supplier_invoice, ['state'], 20)})
    # invoice_paid = fields.Boolean(
    #     compute=_invoiced, method=True, string='Paid', multi='invoiced',
    #     store={
    #         'tms.fuelvoucher':
    #             (lambda self, cr, uid, ids, c={}: ids, None, 10),
    #         'account.invoice': (_get_supplier_invoice, ['state'], 20)})
    # invoice_name = fields.Char(
    #     compute=_invoiced, method=True, string='Invoice', size=64,
    #     multi='invoiced',
    #     store={
    #         'tms.fuelvoucher':
    #             (lambda self, cr, uid, ids, c={}: ids, None, 10),
    #         'account.invoice': (_get_supplier_invoice, ['state'], 20)})
    # no_travel = fields.Boolean(
    #     'No Travel', help="Check this if you want to create Fuel Voucher \
    #     with no Travel.",
    #     states={'cancel': [('readonly', True)],
    #             'approved': [('readonly', True)],
    #             'confirmed': [('readonly', True)],
    #             'closed': [('readonly', True)]})
    # expense_id = fields.Many2one(
    #     'tms.expense', 'Expense Record', required=False, readonly=True)

    @api.multi
    @api.depends('liter', 'price_per_liter')
    def _subtotal(self):
        for rec in self:
            rec.subtotal = rec.liter * rec.price_per_liter

    @api.multi
    @api.depends('subtotal', 'tax_amount')
    def _amount(self):
        for rec in self:
            rec.amount = rec.subtotal + rec.tax_amount

    # @api.multi
    # def action_cancel(self):
    #     for voucher in self:
    #         move_id = voucher.move_id.id
    #         if voucher.invoiced:
    #             raise Warning(
    #                 _('Could not cancel Fuel Voucher!'),
    #                 _('This Fuel Voucher is already invoiced')
    #                 )
    #             self.write({'state': 'cancel', 'invoice_id': False,
    #                         'move_id': False, 'cancelled_by': self,
    #                         'date_cancelled':
    #                         time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
    #             if move_id:
    #                 move_obj.unlink([move_id])
    #     return True

    @api.multi
    def action_approve(self):
        for rec in self:
            if rec.liter == 0:
                raise UserError(
                    _('Liters must be more than 0.'))
            elif rec.price_per_liter == 0:
                raise UserError(
                    _('You neet to assign price per liter'))
            message = _('<b>Fuel Voucher Approved.</b></br><ul>'
                        '<li><b>Supplier: </b>%s</li>'
                        '<li><b>Liters: </b>%s</li>'
                        '<li><b>Price per liter: </b>%s</li>'
                        '<li><b>Driver: </b>%s</li>'
                        '<li><b>Unit: </b>%s</li>'
                        '<li><b>Odometer: </b>%s</li>'
                        '</ul>') % (rec.vendor_id.name, rec.liter,
                                    rec.price_per_liter, rec.employee_id.name,
                                    rec.vehicle_id.name, rec.odometer)
            rec.message_post(body=message)
            rec.state = 'approved'

    # @api.multi
    # def action_confirm(self):
    #     for rec in self:
    #         move_obj = self.env['account.move']
    #         account_jrnl_obj = self.env['account.journal']
    #         journal_id = account_jrnl_obj.search(
    #                 [('type', '=', 'general'),
    #                  ('tms_fuelvoucher_journal', '=', 1)], context=None)
    #         if not journal_id:
    #             raise Warning(
    #                     'Error !',
    #                     'You have not defined Fuel Voucher Journal...')
    #         journal_id = journal_id and journal_id[0]
    #         move_lines = []
    #       precision = self.env['decimal.precision'].precision_get('Account')
    #         notes = _("Fuel Voucher: %s\nTravel: %s\nDriver: (ID %s) %s\n\
    #                          Vehicle: %s") % (
    #                  (rec.name, rec.travel_id and
    #                      rec.travel_id.name or 'N/A'),
    #                  (rec.travel_id and
    #                      rec.travel_id.employee_id.id or 0),
    #                  (rec.travel_id.employee_id and
    #                      rec.travel_id.employee_id.name or 'N/A'),
    #                  (rec.travel_id and
    #                      rec.travel_id.unit_id and
    #                      rec.travel_id.unit_id.name or
    #                      rec.unit_id.name))
    #         print "notes: ", notes

    #         move_line = (0, 0, {
    #                  'name': _('Fuel Voucher: %s') % (rec.name),
    #                  'account_id':
    #                      (rec.product_id.property_account_expense.id if
    #                       rec.product_id.property_account_expense.id
    #                       else
    #                       rec.product_id.categ_id.
    #                       property_account_expense_categ.id),
    #                  'debit': 0.0,
    #                  'credit': round(rec.price_subtotal, precision),
    #                  'journal_id': journal_id,
    #                  'period_id': period_id[0],
    #                  'vehicle_id': rec.unit_id.id,
    #                  'employee_id': (rec.employee_id and
    #                                  rec.employee_id.id or False),
    #                  'sale_shop_id': rec.shop_id.id,
    #                  'product_id': rec.product_id.id,
    #                  'product_uom_id': rec.product_id.uom_id.id,
    #                  'quantity': rec.product_uom_qty
    #              })

    #         move ={
    #              'ref': _('Fuel Voucher: %s') % (voucher.name),
    #              'journal_id': journal_id,
    #              'narration': notes,
    #              'line_id': [x for x in move_lines],
    #              'date': voucher.date,
    #              'period_id': period_id[0],
    #         }
    #         move_id = move_obj.create(move)
    #         if move_id:
    #             move_obj.button_validate([move_id])
    #         self.write({'move_id': move_id,
    #                     'state': 'confirmed',
    #                     'confirmed_by': self,
    #                     'date_confirmed':
    #                     time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
    #     return true

    # @api.model
    # def oe_chatter(self,vals):
    #    rec = Super(TmsFuelvoucher, self).create(vals)

    # def _invoiced(self, field_name, args):
    #     res = {}
    #     for record in self.browse(self):
    #         res[record.id] = {
    #             'invoiced': bool(record.invoice_id and
    #                              record.invoice_id.state != 'cancel'),
    #             'invoice_paid': bool(record.invoice_id and
    #                                  record.invoice_id.state == 'paid'),
    #             'invoice_name':
    #             ((record.invoice_id and
    #               record.invoice_id.state != 'cancel') and
    #                 (record.invoice_id.supplier_invoice_number or
    #                  record.invoice_id.name) or
    #                 False),
    #         }
    #     return res

    # def _get_supplier_invoice(self):
    #     result = {}
    #     for invoice in self.env['account.invoice']:
    #         for fuelvoucher in invoice.fuelvoucher_ids:
    #             result[fuelvoucher.id] = True
    #     return result.keys()

    # _sql_constraints = [
    #     ('name_uniq', 'unique(partner_id,name)',
    #      'Fuel Voucher number must be unique !'),
    # ]
    # _order = "name desc, date desc"

    # def _check_driver(self):
    #     for record in self.browse(self):
    #         if (not record.no_travel and
    #             record.driver_helper and not
    #             record.travel_id.employee2_id.id ==
    #                 record.employee_id.id):
    #             return False
    #         elif (not record.no_travel and not
    #               record.travel_id.employee_id.id == record.employee_id.id):
    #             return False
    #         return True

    # _constraints = [
    #     (_check_driver,
    #      'You can not create Fuel Voucher with Driver not in Travel Record.',
    #      ['employee_id']),
    # ]

    # def on_change_product_id(self, product_id):
    #     if not product_id:
    #         return {}
    #     prod_obj = self.pool.get('product.product')
    #     return {'value': {'product_uom': prod_obj.browse(
    #         [product_id], context=None)[0].uom_id.id}}

    # def on_change_no_travel(self, no_travel):
    #     return no_travel and {'value': {
    #         'travel_id': False,
    #         'unit_id': False, 'employee_id': False}} or {}

    # def on_change_travel_id(self, travel_id):
    #     if not travel_id:
    #         return {'value': {
    #             'employee_id': False,
    #             'employee1_id': False,
    #             'employee2_id': False,
    #             'unit_id': False,
    #             'operation_id': False,
    #             'shop_id': False,
    #         }}
    #     travel = self.pool.get('tms.travel').browse(
    #         [travel_id], context=None)[0]
    #     return {'value': {'employee_id': travel.employee_id.id,
    #                       'employee1_id': travel.employee_id.id,
    #                       'employee2_id': travel.employee2_id.id,
    #                       'unit_id': travel.unit_id.id,
    #                       'operation_id': travel.operation_id.id,
    #                       'shop_id': travel.shop_id.id,
    #                       }
    #             }

    # def on_change_amount(
    #         self, product_uom_qty, price_total, tax_amount, product_id):
    #     res = {'value': {
    #         'price_unit': 0.0,
    #         'price_subtotal': 0.0,
    #         'special_tax_amount': 0.0}}
    #     if not (product_uom_qty and price_total and product_id):
    #         return res
    #     tax_factor = 0.00
    #     prod_obj = self.pool.get('product.product')
    #     for line in prod_obj.browse(
    #             [product_id], context=None)[0].supplier_taxes_id:
    #         tax_factor = ((tax_factor + line.amount)
    #                       if line.amount != 0.0 else tax_factor)
    #     if (tax_amount) and tax_factor == 0.00:
    #         raise Warning(
    #             _('No taxes defined in product !'),
    #             _('You have to add taxes for this product. Para Mexico: \
    #                 Tiene que agregar el IVA que corresponda y el IEPS con \
    #                 factor 0.0.'))
    #     subtotal = ((tax_amount / tax_factor)
    #                 if tax_factor != 0.0 else price_total)
    #     special_tax = ((price_total - subtotal - tax_amount)
    #                    if tax_factor else 0.0)
    #     return {'value': {
    #         'price_unit': (subtotal / product_uom_qty),
    #         'price_subtotal': subtotal,
    #         'special_tax_amount': special_tax}}

    # def create(self, vals):
    #     # Esta va junta
    #     # 'travel_id' in vals and vals['travel_id'] and 'no_travel' in
    #     # vals and vals['no_travel'] and vals.pop('travel_id')
    #     shop_id = 'shop_id' in vals and vals['shop_id'] or False
    #     # print "vals: ", vals
    #     if 'travel_id' in vals and vals['travel_id']:
    #         travel = self.pool.get('tms.travel').browse(vals['travel_id'])
    #         shop_id = travel.shop_id.id
    #         vals.update({
    #             'shop_id': travel.shop_id.id,
    #             'unit_id': travel.unit_id.id})
    #     # print "shop_id: ", shop_id
    #     supplier_seq_id = self.pool.get(
    #         'tms.sale.shop.fuel.supplier.seq').search(
    #             [('shop_id', '=', shop_id),
    #              ('partner_id', '=', vals['partner_id'])])
    #     if supplier_seq_id:
    #         seq_id = self.pool.get(
    #             'tms.sale.shop.fuel.supplier.seq').browse(
    #                 supplier_seq_id)[0].fuel_sequence.id
    #     else:
    #         raise Warning(
    #             _('Fuel Voucher Sequence Error !'),
    #             _('You have not defined Fuel Voucher Sequence for this \
    #                 shop and Supplier ') + str(vals['partner_id']))
    #     if seq_id:
    #         seq_number = self.pool.get('ir.sequence').get_id(seq_id)
    #         vals['name'] = seq_number
    #     else:
    #         raise Warning(
    #             _('Fuel Voucher Sequence Error !'),
    #             _('You have not defined Fuel Voucher Sequence for shop \
    #                 ' + shop_id.name))
    #     return super(TmsFuelvoucher, self).create(self)

    # def write(self, vals):
    #     if 'no_travel' in vals:
    #         raise Warning(
    #             _('Warning !'),
    #             _('You can not change field < No Travel > once Fuel Voucher \
    #                 has been saved for the first time'))

    #     for rec in self.browse(self):
    #         'unit_id' in vals and not rec.no_travel and vals.pop('unit_id')
    #         if 'travel_id' in vals:
    #            travel = self.pool.get('tms.travel').browse(vals['travel_id'])
    #             vals.update({'shop_id': travel.shop_id.id,
    #                          'unit_id': travel.unit_id.id})
    #     return super(TmsFuelvoucher, self).write(self)

    # def action_cancel_draft(self, *args):
    #     if not len(self):
    #         return False
    #     for voucher in self.browse(self):
    #         if voucher.travel_id.state in ('cancel', 'closed'):
    #             raise Warning(
    #                 _('Warning !!! '),
    #                 _('Could not set to draft this Fuel Voucher, Travel is \
    #                     Closed or Cancelled !!!'))
    #         elif voucher.picking_id.id and voucher.picking_id_cancel.id:
    #             raise Warning(
    #                 _('Warning !!! '),
    #                 _('Could not set to draft this Fuel Voucher because it \
    #                     was from Fuel Self Consumption.'))
    #         else:
    #             self.write({'state': 'draft',
    #                         'drafted_by': self,
    #                         'date_drafted':
    #                         time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
    #     return True

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'draft'
    #     for fuelvoucher in self.browse(self):
    #         if fuelvoucher.invoiced:
    #             raise Warning(
    #                 _('Could not cancel Fuel Voucher !'),
    #                 _('This Fuel Voucher is already Invoiced'))
    #         elif (fuelvoucher.travel_id and
    #               fuelvoucher.travel_id.state in ('closed')):
    #             raise Warning(
    #                 _('Could not cancel Fuel Voucher !'),
    #               _('This Fuel Voucher is already linked to Travel Expenses \
    #                     record'))
    #         elif fuelvoucher.picking_id and fuelvoucher.picking_id.id:
    #             picking_id = self.create_picking(
    #                 fuelvoucher, 'return', fuelvoucher.picking_id.id)
    #             self.write({'picking_id_cancel': picking_id})
    #         self.write({'state': 'cancel', 'invoice_id': False,
    #                     'move_id': False, 'cancelled_by': self,
    #                     'date_cancelled':
    #                     time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

    # def create_picking(self, fuelvoucher, picking_type, source_picking_id):
    #     picking_obj = self.pool.get('stock.picking')
    #     move = (0, 0, {
    #         'date': (fuelvoucher.date
    #             if picking_type == 'out'
    #             else time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
    #         'date_expected': (fuelvoucher.date
    #             if picking_type == 'out'
    #             else time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
    #         'product_id': fuelvoucher.product_id.id,
    #         'product_qty': fuelvoucher.product_uom_qty,
    #         'product_uos_qty': fuelvoucher.product_uom_qty,
    #         'product_uom': fuelvoucher.product_id.uom_id.id,
    #         'price_unit': fuelvoucher.product_id.standard_price,
    #         'name': fuelvoucher.product_id.name + ' - ' + fuelvoucher.name,
    #         'auto_validate': False,
    #         'price_currency_id': self.pool.get('res.users').browse(
    #             self).company_id.currency_id.id,
    #         'location_id':
    #             (fuelvoucher.partner_id.tms_warehouse_id.lot_stock_id.id
    #                 if picking_type == 'out'
    #               else fuelvoucher.product_id.property_stock_production.id),
    #         'location_dest_id':
    #             (fuelvoucher.product_id.property_stock_production.id
    #              if picking_type == 'out'
    #            else fuelvoucher.partner_id.tms_warehouse_id.lot_stock_id.id),
    #         'company_id':
    #             self.pool.get('res.users').browse(self).company_id.id,
    #         'vehicle_id': fuelvoucher.unit_id.id,
    #         'employee_id': fuelvoucher.employee_id.id,
    #         'fuelvoucher_id': fuelvoucher.id,
    #     })
    #     last_pick_name = picking_obj.read(
    #         [source_picking_id],
    #         ['name'])[0]['name'] if picking_type != 'out' else ''
    #     new_pick_name = self.pool.get('ir.sequence').get('stock.picking')
    #     name = (new_pick_name
    #             if picking_type == 'out'
    #             else _('%s-%s-Ret') % (new_pick_name, last_pick_name))
    #     picking = {
    #         'name': name,
    #         'date': (fuelvoucher.date
    #                  if picking_type == 'out'
    #                  else time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
    #         'min_date': (fuelvoucher.date
    #                      if picking_type == 'out'
    #                      else time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
    #         'origin': fuelvoucher.name,
    #         'move_lines': [move],
    #         'move_type': 'direct',
    #         'type': 'internal',
    #         'invoice_state': 'none',
    #     }
    #     picking_id = picking_obj.create(picking)
    #     if picking_id:
    #         wf_service = netsvc.LocalService("workflow")
    #         wf_service.trg_validate(
    #             'stock.picking', picking_id, 'button_confirm')
    #         stock_move_obj = self.pool.get('stock.move')
    #         for picking in picking_obj.browse([picking_id]):
    #             for move in picking.move_lines:
    #                 stock_move_obj.force_assign([move.id])
    #                 stock_move_obj.action_done([move.id])
    #     else:
    #         raise Warning(
    #             _('Error !'),
    #             _('Could not create Picking for Fuel Voucher %s\
    #                 ') % (fuelvoucher.name,))
    #     return picking_id

    # def action_approve(self):
    #     for fuelvoucher in self.browse(self):
    #         if fuelvoucher.state in ('draft'):
    #             self.write({'state': 'approved', 'approved_by': self,
    #                         'date_approved':
    #                         time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
    #     return True

    # def action_confirm(self):
    #     for voucher in self:
    #         if voucher.product_uom_qty <= 0.0:
    #             raise Warning(
    #                 _('Could not confirm Fuel Voucher !'),
    #                 _('Product quantity must be greater than zero.'))
    #         elif (voucher.partner_id.tms_category == 'fuel':
    #             if (voucher.product_id.qty_available <
    #                     voucher.product_uom_qty):
    #                 raise Warning(
    #                     _('Warning !'),
    #                     _('There is no enough Product Inventory to Confirm \
    #                         Fuel Voucher %s') % (voucher.name,))
    #             picking_id = self.create_picking(voucher, 'out', 'False')
    #             self.write(
    #                 {'picking_id': picking_id,
    #                  'price_total':
    #                  (voucher.product_id.standard_price *
    #                   voucher.product_uom_qty),
    #                  'state': 'confirmed', 'confirmed_by': self,
    #                  'date_confirmed':
    #                  time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
    #         else:
    #             period_obj = self.pool.get('account.period')
    #             account_jrnl_obj = self.pool.get('account.journal')
    #             period_id = period_obj.search(
    #                 [('date_start', '<=', voucher.date),
    #                  ('date_stop', '>=', voucher.date),
    #                  ('state', '=', 'draft')], context=None)
    #             if not period_id:
    #                 raise Warning(
    #                     _('Warning !'),
    #                   _('There is no valid account period for this date %s. \
    #                         Period does not exists or is already closed\
    #                         ') % (voucher.date,))
    #             journal_id = account_jrnl_obj.search(
    #                 [('type', '=', 'general'),
    #                  ('tms_fuelvoucher_journal', '=', 1)], context=None)
    #             if not journal_id:
    #                 raise Warning(
    #                     'Error !',
    #                     'You have not defined Fuel Voucher Journal...')
    #             journal_id = journal_id and journal_id[0]
    #             move_lines = []
    #             precision = self.pool.get('decimal.precision').precision_get(
    #                 'Account')
    #            notes = _("Fuel Voucher: %s\nTravel: %s\nDriver: (ID %s) %s\n\
    #                         Vehicle: %s") % (
    #                 (voucher.name, voucher.travel_id and
    #                     voucher.travel_id.name or 'N/A'),
    #                 (voucher.travel_id and
    #                     voucher.travel_id.employee_id.id or 0),
    #                 (voucher.travel_id.employee_id and
    #                     voucher.travel_id.employee_id.name or 'N/A'),
    #                 (voucher.travel_id and
    #                     voucher.travel_id.unit_id and
    #                     voucher.travel_id.unit_id.name or
    #                     voucher.unit_id.name))
    #             # #print "notes: ", notes
    #             if not (voucher.product_id.property_account_expense.id
    #                     if voucher.product_id.property_account_expense.id
    #                     else voucher.product_id.categ_id.
    #                     property_account_expense_categ.id
    #                     if voucher.product_id.categ_id.
    #                     property_account_expense_categ.id
    #                     else False):
    #                 raise Warning(
    #                     _('Missing configuration !!!'),
    #                     _('You have not defined expense Account for \
    #                         Product %s...') % (voucher.product_id.name))
    #             move_line = (0, 0, {
    #                 'name': _('Fuel Voucher: %s') % (voucher.name),
    #                 'account_id':
    #                     (voucher.product_id.property_account_expense.id if
    #                      voucher.product_id.property_account_expense.id
    #                      else
    #                      voucher.product_id.categ_id.
    #                      property_account_expense_categ.id),
    #                 'debit': 0.0,
    #                 'credit': round(voucher.price_subtotal, precision),
    #                 'journal_id': journal_id,
    #                 'period_id': period_id[0],
    #                 'vehicle_id': voucher.unit_id.id,
    #                 'employee_id': (voucher.employee_id and
    #                                 voucher.employee_id.id or False),
    #                 'sale_shop_id': voucher.shop_id.id,
    #                 'product_id': voucher.product_id.id,
    #                 'product_uom_id': voucher.product_id.uom_id.id,
    #                 'quantity': voucher.product_uom_qty
    #             })
    #             move_lines.append(move_line)
    #             if not (voucher.product_id.tms_property_account_expense.id
    #                     if
    #                     voucher.product_id.tms_property_account_expense.id
    #                     else
    #                     voucher.product_id.categ_id.
    #                     tms_property_account_expense_categ.id
    #                     if
    #                     voucher.product_id.categ_id.
    #                     tms_property_account_expense_categ.id
    #                     else False):
    #                 raise Warning(
    #                     _('Missing configuration !!!'),
    #                     _('You have not defined breakdown Account for \
    #                         Product %s...') % (voucher.product_id.name))
    #             move_line = (0, 0, {
    #                 'name': _('Fuel Voucher: %s') % (voucher.name),
    #                 'account_id':
    #                 (voucher.product_id.tms_property_account_expense.id if
    #                     voucher.product_id.tms_property_account_expense.id
    #                     else
    #                     voucher.product_id.categ_id.
    #                     tms_property_account_expense_categ.id),
    #                 'debit': round(voucher.price_subtotal, precision),
    #                 'credit': 0.0,
    #                 'journal_id': journal_id,
    #                 'period_id': period_id[0],
    #                 'vehicle_id': voucher.unit_id.id,
    #                 'employee_id': (voucher.employee_id and
    #                                 voucher.employee_id.id or False),
    #                 'sale_shop_id': voucher.shop_id.id,
    #                 'product_id': voucher.product_id.id,
    #                 'product_uom_id': voucher.product_id.uom_id.id,
    #                 'quantity': voucher.product_uom_qty
    #             })
    #             move_lines.append(move_line)
    #             move = {
    #                 'ref': _('Fuel Voucher: %s') % (voucher.name),
    #                 'journal_id': journal_id,
    #                 'narration': notes,
    #                 'line_id': [x for x in move_lines],
    #                 'date': voucher.date,
    #                 'period_id': period_id[0],
    #             }
    #             move_id = move_obj.create(move)
    #             if move_id:
    #                 move_obj.button_validate([move_id])
    #             self.write({'move_id': move_id,
    #                         'state': 'confirmed',
    #                         'confirmed_by': self,
    #                         'date_confirmed':
    #                         time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
    #     return True

    # def copy(self, default=None):
    #     default = default or {}
    #     default.update({
    #         'cancelled_by': False,
    #         'date_cancelled': False,
    #         'approved_by': False,
    #         'date_approved': False,
    #         'confirmed_by': False,
    #         'date_confirmed': False,
    #         'closed_by': False,
    #         'date_closed': False,
    #         'drafted_by': False,
    #         'date_drafted': False,
    #         'invoice_id': False,
    #         'notes': False,
    #         'move_id': False,
    #         'expense_id': False,
    #         'expense2_id': False,
    #     })
    #     return super(TmsFuelvoucher, self).copy(self)
