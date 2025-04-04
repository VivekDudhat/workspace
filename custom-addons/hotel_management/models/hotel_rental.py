from odoo import fields,api,models
from datetime import date,datetime,timedelta



class HotelRental(models.Model):
    _name = "hotel.rental"
    _description = "Rental Service"
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = "customer_id"
    

    customer_id = fields.Many2one('hotel.room.booking',string='Customer Name',)
    customer_email = fields.Char(string='Email',related='customer_id.email_id')
    customer_number = fields.Char(string = "Contact Number",related='customer_id.contact')
    date_of_arrival= fields.Datetime(string = "Date of arrival",)
    pick_up_location = fields.Selection([('airport', 'Airport'),('bus stop','Bus Stop'),('railway station','Railway Station')])
    no_of_people = fields.Integer(string = "Number of people",)
    vehicle_type = fields.Selection([('car', 'Car'),('mini van','Mini Van'),('tempo traveller','Tempo Traveller')])
    state = fields.Selection([('draft','Draft'),('book', 'Book'),('cancel','Cancel')],default='draft')
    distance = fields.Float(string = 'Total Distance',  default=0.0)
    total_cost = fields.Float(string='Total Amount', compute="_compute_total_cost", store=True)
    booking_time = fields.Datetime()

    @api.onchange('no_of_people')
    def _onchange_field(self):
        if self.no_of_people <= 3:
            self.vehicle_type = 'car'
        elif self.no_of_people <= 6:
            self.vehicle_type = 'mini van'
        else:
            self.vehicle_type = 'tempo traveller'

    @api.onchange('pick_up_location')
    def _onchange_distance(self):
        if self.pick_up_location == 'airport':
            self.distance = 25
        elif self.pick_up_location == 'railway station':
            self.distance = 17
        elif self.pick_up_location == 'bus stop':
            self.distance = 11

    @api.depends('no_of_people')
    def _compute_total_cost(self):
        for record in self:
            if record.vehicle_type == 'car':
                rate_per_km = 20
            elif record.vehicle_type == 'mini van':
                rate_per_km = 25
            else:
                rate_per_km = 30
            record.total_cost = record.distance * rate_per_km

    def action_book(self):
        for records in self :
            records.state = 'book'
            records.booking_time = fields.Datetime.now()
            template_id = self.env.ref('hotel_management.email_template_confirm')
            if template_id:
                template_id.send_mail(records.id,force_send = True)

    def action_cancel(self):
        for records in self:
            if records.state == 'book':
                cuurent_time = fields.Datetime.now()
                booking_time = records.booking_time
                time_difference = cuurent_time - booking_time
                if time_difference <= timedelta(minutes=10):
                    records.state = 'cancel'
                    refund_template = self.env.ref('hotel_management.email_template_cancel_booking_refund')
                    refund_template.send_mail(records.id,force_send=True)
                else:
                    records.state = 'cancel'
                    cancel_template = self.env.ref('hotel_management.email_template_cancel_booking')
                    cancel_template.send_mail(records.id,force_send=True)
            else:
                records.state = 'cancel'
            


   
    
    
    