from odoo import _, api, fields, models


class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order']

    @api.one
    @api.depends('order_line.price_unit', 'order_line.discount', 'order_line.product_uom_qty')
    def descuentos(self):
        for line in self.order_line:
            perc2 = line.price_unit * line.discount / 100
            print("###############################################perc2 ", perc2)
            descuentos = sum(l.amount_discount for l in self.order_line)
            print ("###########################################descuentos", descuentos)
            self.discounts = descuentos


    @api.one
    @api.depends('order_line.price_unit',  'order_line.product_uom_qty')
    def precio_discount(self):
        for l in self.order_line:
            total3 = sum(l.price_unit for l in self.order_line) * l.product_uom_qty
            self.precio_sin_descuento = total3

    discounts = fields.Float(string='Descuentos', digits=(14,2), compute="descuentos")
    precio_sin_descuento = fields.Float(string='Precio sin Descuento', digits=(14,2), compute="precio_discount")



    amount_to_text = fields.Char('Amount to text',compute='_compute_amount_to_text')
    # accounts = fields.One2many(
    #     'res.partner.bank',
    #     'partner_id',
    #     'Cuentas',
    #     compute='_computed_account')

    @api.multi
    def _compute_amount_to_text(self):
        """Method to transform a float amount to text words
        E.g. 100 - ONE HUNDRED
        :returns: Amount transformed to words mexican format for invoices
        :rtype: str
        """
        self.ensure_one()
        currency = self.currency_id.name.upper()
        # M.N. = Moneda Nacional (National Currency)
        # M.E. = Moneda Extranjera (Foreign Currency)
        currency_type = 'M.N' if currency == 'MXN' else 'M.E.'
        # Split integer and decimal part
        amount_i, amount_d = divmod(self.amount_total, 1)
        amount_d = round(amount_d, 2)
        amount_d = int(round(amount_d * 100, 2))
        words = self.currency_id.with_context(
            lang=self.partner_id.lang or'es_ES'
        ).amount_to_text(amount_i).upper()
        sale_words = '%(words)s %(amount_d)02d/100 %(curr_t)s' % dict(
            words=words, amount_d=amount_d, curr_t=currency_type)
        self.amount_to_text = sale_words




class sale_order_line(models.Model):
    _name = 'sale.order.line'
    _inherit = ['sale.order.line']



    
    barcode = fields.Char(related='product_id.barcode', string='Código de barras')
    price_discount = fields.Float(string='Precio con Descuento', digits=(14,2), compute="discount_price")
    amount_discount = fields.Float(compute='_compute_amount_discount')
    import_discount = fields.Float(string='Importe con Descuento', digits=(14,2),  compute="discount_import")

    @api.one
    @api.depends('price_unit', 'discount', 'product_uom_qty')
    def _compute_amount_discount(self):
        for record in self:
            record.amount_discount = (record.price_unit * record.discount / 100) * record.product_uom_qty

    @api.one
    @api.depends('price_unit', 'discount')
    def discount_price(self):
        # porcentaje = (self.discount / 100)
        # procentaje2 = (procentaje * 10) 
        perc = self.price_unit * self.discount / 100
        
        precio_con_descuento = (self.price_unit - perc)
        self.price_discount = precio_con_descuento 

    @api.one
    @api.depends('price_unit', 'discount', 'product_uom_qty')
    def discount_import(self):
        perc1 = self.price_unit * self.discount / 100
        precio_con_descuento = ((self.price_unit - perc1) * self.product_uom_qty)
        self.import_discount=precio_con_descuento 




    # @api.one
    # @api.depends('invoice_line_ids.price_discount', 'invoice_line_ids.import_discount')
    # def _compute_amount(self):
    #     self.price_discount = sum(line.price_subtotal for line in self.invoice_line_ids)
    #     self.amount_tax = sum(line.amount_total for line in self.tax_line_ids)
    #     self.amount_total = self.amount_untaxed + self.amount_tax
    #     self.amount_discount = sum((line.quantity * line.price_unit * line.discount)/100 for line in self.invoice_line_ids)


    # @api.one
    # @api.depends('invoice_line_ids')
    # def _get_average_cost_amount(self):
    #     for record in self:
    #         record.cost_amount = sum(l.cost_amount for l in record.invoice_line_ids)