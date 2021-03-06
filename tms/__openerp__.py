# -*- coding: utf-8 -*-
# © <2012> <Israel Cruz Argil, Argil Consulting>
# © <2016> <Jarsa Sistemas, S.A. de C.V.>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Freight Management",
    "version": "9.0.0.1.0",
    "category": "Transport",
    "author": "Argil Consulting, Jarsa Sistemas",
    "website": "http://www.argil.mx, https://www.jarsa.com.mx",
    "depends": ["hr", "account_voucher", "purchase", "sale", "fleet"],
    "summary": "Management System for Carriers, Trucking and other companies",
    "license": "AGPL-3",
    "data": [
        'security/ir.model.access.csv',
        'views/tms_view.xml',
        'views/tms_base_view.xml',
        # 'views/account_journal_view.xml',
        # 'views/fleet_vehicle_odometer_view.xml',
        # 'views/fleet_vehicle_view.xml',
        'views/hr_employee_view.xml',
        'views/fleet_vehicle_view.xml',
        'views/fleet_vehicle_log_fuel_view.xml',
        # 'views/product_category_view.xml',
        'views/product_product_view.xml',
        # 'views/tms_advance_view.xml',
        'views/tms_config_settings_view.xml',
        # 'views/tms_expense_line_view.xml',
        # 'views/tms_expense_view.xml',
        'views/tms_factor_view.xml',
        'views/tms_place_view.xml',
        'views/tms_route_view.xml',
        'views/tms_transportable_view.xml',
        # 'views/tms_travel_view.xml',
        # 'views/tms_unit_kit_view.xml',
        'views/tms_waybill_view.xml',
        'data/product_product_data.xml',
    ],
    "demo": [
        'demo/tms_place.xml',
        'demo/tms_route.xml',
        'demo/tms_transportable.xml',
    ],
    "application": True,
    "installable": True
}
