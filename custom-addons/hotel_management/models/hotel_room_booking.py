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
    contact = fields.Char(string='Contact Number', )
    date_of_birth = fields.Date(string='Date Of Birth')
    age = fields.Integer(string="Age", compute='_compute_age', store=True)
    email_id = fields.Char(string="Email", )
    document_proof = fields.Binary(string='Document Proof')
    check_in = fields.Datetime(string="Check-In",)  # default=fields.Datetime.now
    check_out = fields.Datetime(string="Check-Out", default=lambda self: self._default_check_out())
    room_id = fields.Many2one('hotel.rooms', string="Room", required=True,tracking = True)
    room_type =fields.Many2one (string='Room Type', related='room_id.rooms_ids')
    room_price = fields.Float(string = "Price",related='room_id.price')
    room_image = fields.Image(string="Room Image", related='room_id.rooms_ids.room_image', store=True)
    customer_photo = fields.Image(string="Customer Photo", max_width=128, max_height=128)
    total_price = fields.Float(string = "Total Amount", compute = '_total_amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('booked', 'Booked'),
        ('checked_in', 'Checked-In'),
        ('checked_out', 'Checked-Out'),
        ('canceled', 'Canceled'),
    ], string="State", default='draft', readonly=True,tracking = True)
    amenity_id = fields.Many2many(
        'hotel.amenities',
        'booking_amenities_rel',
        'amenity_id',
        'booking_id',
        string="Amenities"
    )
    amenity_charge = fields.Float(string = "Amenity Charge",related='amenity_id.charge')
    total_charge = fields.Float(string = 'Total charge', compute = '_total_charge')
    adult_count = fields.Integer(string="No of Adult")
    children_count = fields.Integer(string = "No of Children")
    vehicle_id = fields.Many2one('hotel.rental',string='vehicle',)
    vehicle_name = fields.Selection(string = "Vehicle name",related='vehicle_id.vehicle_type', store = 'True')
    vechicle_charge = fields.Float(string = "Vehicle")
    resturant_id = fields.Many2one('hotel.resturant',string='resturant',)
    food = fields.Char(string = 'food name',related='resturant_id.food_name')
    food_bill = fields.Float(string = 'Bill',related='resturant_id.total_bill')
    cleaning_id = fields.Many2one('hotel.room.cleaning',string='cleaning',)

    @api.constrains('self')
    def _check_(self):
        for record in self:
            if record.adult_count < 1:
                raise ValidationError("There must be one adult")
            if record.children_count < 0 :
                raise ValidationError("Children cannot be in negative")
            
    
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

    @api.depends('check_in','check_out','room_price')
    def _total_amount(self):
        for record in self:
            if record.check_in and record.check_out:
                num_days = (record.check_out - record.check_in).days
                num_days = num_days = num_days if num_days > 0 else 1 
                record.total_price = num_days * record.room_price
            else:
                record.total_price = 0.0

    @api.depends('amenity_charge')
    def _total_charge(self):
        for record in self:
            record.total_charge = sum(record.amenity_id.mapped('charge'))
    
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
                book_template = self.env.ref('hotel_management.email_template_room_booking')
                if book_template:
                    book_template.send_mail(record.id,force_send = True)

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
        adult_count = vals.get('adult_count', 1)
        children_count = vals.get('children_count', 0)

        if adult_count <= 2 and children_count <= 1 :
            normal_room = self.env['hotel.rooms'].search([('rooms_ids', '=', 'normal')], limit=1)
            if not normal_room:
                raise ValidationError("No normal rooms available.")
            vals['room_id'] = normal_room.id
        elif adult_count <= 2 and children_count <= 2:
            deluxe_room = self.env['hotel.rooms'].search([('rooms_ids', '=', 'deluxe')], limit=1)
            if not deluxe_room:
                raise ValidationError("No deluxe room avaliable")
            vals['room_id'] = deluxe_room.id
        else:
            raise ValidationError("No rooms avaliable right now")

        booking = super(HotelBooking, self).create(vals)
        if booking.state == 'booked':
            booking.room_id.is_booked = True
        return booking

    def write(self, vals):
        if 'room_id' in vals and not vals['room_id']:
            raise ValidationError("Please select a room before updating the booking.")
        
        # Automaticallyroom type on number of adult and child count
        adult_count = vals.get('adult_count', self.adult_count)
        children_count = vals.get('child_count', self.children_count)
        
        if adult_count <= 2 and children_count <= 1:
            # Assign normal room
            normal_room = self.env['hotel.rooms'].search([('rooms_ids', '=', 'normal')], limit=1)
            if not normal_room:
                raise ValidationError("No normal rooms available.")
            vals['room_id'] = normal_room.id
        elif adult_count <= 2 and children_count <= 2:
            # Assign deluxe room
            deluxe_room = self.env['hotel.rooms'].search([('rooms_ids', '=', 'deluxe')], limit=1)
            if not deluxe_room:
                raise ValidationError("No deluxe rooms available.")
            vals['room_id'] = deluxe_room.id
        else:
            raise ValidationError("No suitable room available for the given number of adults and children.")
        
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

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hotel.room.booking'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'hotel.room.booking',
            'docs': docs,
           
        }
    def action_print_booking_report(self):
        return self.env.ref('hotel_management.hotel_booking_report_action').report_action(self)