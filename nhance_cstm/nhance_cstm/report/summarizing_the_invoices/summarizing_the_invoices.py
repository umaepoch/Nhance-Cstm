# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _, msgprint
from frappe.utils import flt, getdate, comma_and
from erpnext.stock.stock_balance import get_balance_qty_from_sle
import datetime
from datetime import date, timedelta
from collections import defaultdict
import operator
import frappe
import json
import time
import math
import ast

def execute(filters=None):
	global data
	columns = []
	data = []
	columns = get_columns()

	data.append(["", "", ""])
	invoice_list_for_day = get_day_wise_invoices()
	data.append(["Day", "", ""])
	if invoice_list_for_day is not None:
		invoice_type = "Day"
		get_invoice_amount(invoice_list_for_day,invoice_type)
	
	data.append(["", "", ""])
	data.append(["Month To Date", "", ""])

	invoice_list_for_month = get_month_wise_invoices()
	if invoice_list_for_month is not None:
		invoice_type = "Month"
		get_invoice_amount(invoice_list_for_month,invoice_type)
	
	data.append(["", "", ""])
	data.append(["Year To Date", "", ""])

	invoice_list_for_fin_year = get_year_wise_invoices()
	if invoice_list_for_fin_year is not None:
		invoice_type = "Year"
		get_invoice_amount(invoice_list_for_fin_year,invoice_type)
	
	return columns, data

def get_columns():
	"""return columns"""
	columns = [
	_(" ")+"::100",
	_("B-C")+"::100",
	_("B-B")+"::150",
	_("Total")+"::150"
	 ]
	return columns

def get_invoice_amount(invoice_list,invoice_type):
	customer_type = ""
	total_invoice_amount_of_company = 0
	total_invoice_amount_of_individual = 0
	current_date = getdate(datetime.datetime.now())
	c_date = frappe.utils.formatdate(current_date, "dd-MM-yyyy")
	now = datetime.datetime.now()
	current_year = now.year
	monthinteger = now.month
	current_month = datetime.date(1900, monthinteger, 1).strftime('%B')
	fiscal_year = frappe.defaults.get_user_default("fiscal_year")
	fiscal_year_start = fiscal_year[:4]
	for invoice_data in invoice_list:
		customer_namee =invoice_data['customer_name']
		customer_type = get_customer_type(customer_namee)
		print "Suresh Checking *************** customer_type from for",customer_type

		amount = invoice_data['net_total']
		status = invoice_data['status']
		if customer_type == "Company":
			total_invoice_amount_of_company = total_invoice_amount_of_company + amount
		elif customer_type == "Individual":
			total_invoice_amount_of_individual = total_invoice_amount_of_individual + amount
			print "total_invoice_amount_of_individual--------", total_invoice_amount_of_individual
	
	total = total_invoice_amount_of_company + total_invoice_amount_of_individual
	if invoice_type == "Day":
		data.append([str(c_date), total_invoice_amount_of_individual, total_invoice_amount_of_company, total])
	elif invoice_type == "Month":
		data.append([ (str(current_month) + ", " + str(current_year)), total_invoice_amount_of_individual, 				       total_invoice_amount_of_company, total])
	elif invoice_type == "Year":
		data.append([ ("FY" + fiscal_year_start + "-"+ str(current_year)), total_invoice_amount_of_individual, 					total_invoice_amount_of_company, total])

def get_day_wise_invoices():
	current_date = getdate(datetime.datetime.now())
	invoice_details = frappe.db.sql("""select customer_name, name, net_total, status from `tabSales Invoice` where posting_date = %s and 
					docstatus=1""", (current_date), as_dict=1)
	if len(invoice_details)!=0:
		return invoice_details
	else:
		return None

def get_month_wise_invoices():
	d = date.today()
	from_date = get_first_day(d)
	to_date = getdate(datetime.datetime.now())
	invoice_details = frappe.db.sql("""select customer_name, name, net_total, status from `tabSales Invoice` where posting_date >= %s and 
					posting_date <= %s and docstatus=1""", (from_date, to_date), as_dict=1)
	if len(invoice_details)!=0:
		return invoice_details
	else:
		return None

def get_year_wise_invoices():
	now = datetime.datetime.now()
	current_year = now.year
	fiscal_year = frappe.defaults.get_user_default("fiscal_year")
	fiscal_year_start = fiscal_year[:4]
	from_date = str(fiscal_year_start) + "-04-01"
	to_date = getdate(datetime.datetime.now())
	invoice_details = frappe.db.sql("""select customer_name, name, net_total, status from `tabSales Invoice` where posting_date >= %s and 
					posting_date <= %s and docstatus=1""", (from_date, to_date), as_dict=1)

	if len(invoice_details)!=0:
		return invoice_details
	else:
		return None

def get_first_day(dt, d_years=0, d_months=0):
	# d_years, d_months are "deltas" to apply to dt
	y, m = dt.year + d_years, dt.month + d_months
	a, m = divmod(m-1, 12)
	return date(y+a, m+1, 1)

def  get_customer_type( customer_name ):
	customer_type = frappe.db.get_value("Customer",customer_name,'customer_type')
	return customer_type


	


