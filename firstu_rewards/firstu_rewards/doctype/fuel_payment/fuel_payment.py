# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tridz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class FuelPayment(Document):
	def validate(self):
		customer_doc = frappe.get_doc('Customer', self.customer)
		fuel_doc = frappe.get_doc('Fuel Price')
		
		fuel_type = customer_doc.fuel_type
		membership_type = customer_doc.membership_type

		if fuel_type == "Petrol":
			fuel_today = fuel_doc.petrol
			if membership_type == "Status":
				fuel = fuel_doc.petrol_status
			elif membership_type == "Privilege":
				fuel = fuel_doc.petrol_privilege
			

		elif fuel_type == "Diesel":
			fuel_today = fuel_doc.diesel
			if membership_type == "Status":
				fuel = fuel_doc.diesel_status
			elif membership_type == "Privilege":
				fuel = fuel_doc.diesel_privilege

		litre_filled = round(int(self.amount) / int(fuel_today), 2)
		self.litres = litre_filled
		self.market_value = fuel_today
		self.customer_value = fuel
		cashback = int(fuel_today) * int(litre_filled) - int(fuel) * int(litre_filled)
		self.cashback = cashback
		self.cashback_doc = frappe.get_doc({
			'doctype': 'Cashback Ledger',
			'customer': self.customer,
			'amount': cashback,
			'fuel_payment': self.name
		})
		
		trophy_doc = frappe.get_doc('Trophy Settings')

		if int(customer_doc.refuel_left) == 0:
			customer_doc.total_trophies_collected = int(customer_doc.total_trophies_collected) + int(trophy_doc.trophies)
			customer_doc.refuel_left =  int(trophy_doc.frequency)
		else:
			customer_doc.refuel_left = int(customer_doc.refuel_left) - 1

		
		customer_doc.save()

	def on_submit(self):
		self.cashback_doc.submit()
