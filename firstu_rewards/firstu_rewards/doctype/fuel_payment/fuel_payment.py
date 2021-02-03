# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tridz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class FuelPayment(Document):
	def validate(self):
		self.customer_doc = frappe.get_doc('Customer', self.customer)
		fuel_doc = frappe.get_doc('Fuel Price')
		
		# validate fuel type and membership type and assign fuel price according to membership type. Fuel price are updated on change of fuel prices.

		fuel_type = self.customer_doc.fuel_type
		membership_type = self.customer_doc.membership_type

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
		
		# calculate liters filled and cashback amount and create cashback ledger document against customer.

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
			'fuel_payment': self.name,
			'fuel_paid_amount': self.amount,
			'note': 'Cashbhack received for fuel refill'
		})
		

	def on_submit(self):

		# calculates cashback balance and trophies collected by customer.
		# Trophies are added upon fuel payment frequency which is predefined in trophy settings.
		# Refuel left field indicates the refuel left to earn next trophies.

		trophy_doc = frappe.get_doc('Trophy Settings')

		self.customer_doc.cashback_balance = int(self.customer_doc.cashback_balance) + int(self.cashback)
		self.customer_doc.lifetime = int(self.customer_doc.lifetime) + int(self.cashback)

		if int(self.customer_doc.refuel_left) == 0:
			self.customer_doc.total_trophies_collected = int(self.customer_doc.total_trophies_collected) + int(trophy_doc.trophies)
			self.customer_doc.refuel_left =  int(trophy_doc.frequency)
			trophy_doc = frappe.get_doc({
				'doctype': 'Trophy Ledger',
				'trophy_count': trophy_doc.trophies,
				'creditdebit': "Credit",
				'note': 'Trophy Earned from refuel',
				'customer': self.customer,
				'docstatus': 1
			})
			trophy_doc.insert()
		else:
			self.customer_doc.refuel_left = int(self.customer_doc.refuel_left) - 1

		
		self.customer_doc.save()
		self.cashback_doc.submit()
