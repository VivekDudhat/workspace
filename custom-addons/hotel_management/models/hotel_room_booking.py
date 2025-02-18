from odoo import fields, api, models
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
import re


class HotelBooking(models.Model):
    _name = "hotel.room.booking"
    _description = "Hotel Room Booking"
    _rec_name = "customer_name"
    _inherit = ['mail.thread','mail.activity.mixin']
    

    customer_name = fields.Char(string="Customer Name", )
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')])
    contact = fields.Char(string='Contact Number', )
    date_of_birth = fields.Date(string='Date Of Birth')
    age = fields.Integer(string="Age", compute='_compute_age', store=True)
    email_id = fields.Char(string="Email", )
    document_proof = fields.Binary(string='Photo ID')
    check_in = fields.Datetime(string="Check-In",)  # default=fields.Datetime.now
    check_out = fields.Datetime(string="Check-Out", default=lambda self: self._default_check_out())
    room_id = fields.Many2one('hotel.rooms', string="Room", required=True,tracking = True)
    room_type =fields.Many2one (string='Room Type', related='room_id.rooms_ids')
    room_price = fields.Float(string = "Price",related='room_id.price')
    room_image = fields.Image(string="Room Image", related='room_id.rooms_ids.room_image', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('booked', 'Booked'),
        ('checked_in', 'Checked-In'),
        ('checked_out', 'Checked-Out'),
        ('canceled', 'Canceled'),
    ], string="State", default='draft', readonly=True,tracking = True)

    @api.constrains('room_id')
   
    def _default_check_out(self):
        # Default check-out time is 12:00 PM 
        check_in = self.check_in or fields.Datetime.now()
        return check_in.replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=1)

    @api.constrains('email_id')
    def _check_email_format(self):
        for record in self:
            if record.email_id:
                email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
                if not re.match(email_regex, record.email_id):
                    raise ValidationError("The email address is not in a valid format.")

    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                today = date.today()
                dob = record.date_of_birth
                record.age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            else:
                record.age = 0

    @api.constrains('contact')
    def _check_contact_format(self):
        for record in self:
            if record.contact:
                phone_regex = r'^\+?\d{1,4}\s?\d{10}$'
                if not re.match(phone_regex, record.contact):
                    raise ValidationError("The contact number is not in a valid format. It should be in the format +<country_code> <phone_number> (e.g., +91 8780085668).")

    @api.constrains('room_id', 'check_in', 'check_out', 'state')
    def _check_room_availability(self):
        for record in self:
            if record.state != 'canceled':
                overlapping_bookings = self.search([
                    ('room_id', '=', record.room_id.id),
                    ('check_in', '<', record.check_out),
                    ('check_out', '>', record.check_in),
                    ('id', '!=', record.id),
                    ('state', '!=','checked_out'),
                    ('state', '!=', 'canceled'),
                ])
                if overlapping_bookings:
                    raise ValidationError("This room is already booked for the selected date range.")

    @api.onchange('check_in', 'check_out')
    def _onchange_dates(self):
        if self.check_in and self.check_out:
            domain = [
                ('check_in', '<', self.check_out),
                ('check_out', '>', self.check_in),
                ('state', '!=', 'canceled'),
            ]
            if self.id: 
                domain.append(('id', '!=', self.id))
            overlapping_bookings = self.search(domain)
            booked_room_ids = overlapping_bookings.mapped('room_id').ids
            return {
                'domain': {
                    'room_id': [('id', 'not in', booked_room_ids)]
                }
            }

    def action_book(self):
        for record in self:
            if not record.room_id:
                raise ValidationError("Please select a room before confirming the booking.")
            if record.state == 'draft':
                record.state = 'booked'
                record.room_id.is_booked = True

    def action_check_in(self):
        for record in self:
            if record.state == 'booked':
                record.state = 'checked_in'

    def action_check_out(self):
        for record in self:
            if record.state == 'checked_in':
                record.state = 'checked_out'
                record.room_id.is_booked = False

    def action_cancel(self):
        for record in self:
            if record.state in ['draft', 'booked']:
                record.state = 'canceled'
                record.room_id.is_booked = False

    @api.model
    def create(self, vals):
        if 'room_id' not in vals or not vals['room_id']:
            raise ValidationError("Please select a room before creating the booking.")
        booking = super(HotelBooking, self).create(vals)
        if booking.state == 'booked':
            booking.room_id.is_booked = True
        return booking

    def write(self, vals):
        if 'room_id' in vals and not vals['room_id']:
            raise ValidationError("Please select a room before updating the booking.")
        if 'room_id' in vals:
            for record in self:
                record.room_id.is_booked = False
                new_room = self.env['hotel.rooms'].browse(vals['room_id'])
                new_room.is_booked = True
        return super(HotelBooking, self).write(vals)

    def unlink(self):
        for record in self:
            if record.state != 'checked_out':
                record.room_id.is_booked = False
        return super(HotelBooking, self).unlink()