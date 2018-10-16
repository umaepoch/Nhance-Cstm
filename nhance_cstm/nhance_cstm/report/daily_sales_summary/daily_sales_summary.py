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
import calendar

def execute(filters=None):
	global data
	columns = []
	data = []
	columns = get_columns()
	invoices_day_month_year_list=[]

	invoice_list_for_day = get_day_wise_invoices()
	if invoice_list_for_day is not None:
		invoices_day_month_year_list.append({"day":invoice_list_for_day})
	else:
		invoices_day_month_year_list.append({"day":None})

	invoice_list_for_month = get_month_wise_invoices()
	if invoice_list_for_month is not None:
		invoices_day_month_year_list.append({"month":invoice_list_for_month})
	else:
		invoices_day_month_year_list.append({"month":None})

	invoice_list_for_fin_year = get_year_wise_invoices()
	if invoice_list_for_fin_year is not None:
		invoices_day_month_year_list.append({"year":invoice_list_for_fin_year})
	else:
		invoices_day_month_year_list.append({"year":None})

	data_appending(invoices_day_month_year_list)
	
	return columns, data

def get_columns():
	"""return columns"""
	columns = [
	_("-")+"::100",
	_("-")+"::100",
	_("Day")+"::100",
	_("Month to Date")+"::100",
	_("Year to Date")+"::150"
	 ]
	return columns

def data_appending(invoices_day_month_year_list):
	customer_type = ""
	payment_term = ""

	total_company_cash_day = 0
	total_company_credit_card_day = 0
	total_company_neft_rtgs_day = 0
	total_company_bank_draft_day = 0
	total_company_cheque_day = 0
	total_company_credit_day = 0
	total_individual_cash_day = 0
	total_individual_credit_card_day = 0
	total_individual_neft_rtgs_day = 0
	total_individual_bank_draft_day = 0
	total_individual_cheque_day = 0
	total_individual_credit_day = 0

	total_company_cash_month = 0
	total_company_credit_card_month = 0
	total_company_neft_rtgs_month = 0
	total_company_bank_draft_month = 0
	total_company_cheque_month = 0
	total_company_credit_month = 0
	total_individual_cash_month = 0
	total_individual_credit_card_month = 0
	total_individual_neft_rtgs_month = 0
	total_individual_bank_draft_month = 0
	total_individual_cheque_month = 0
	total_individual_credit_month = 0

	total_company_cash_year = 0
	total_company_credit_card_year = 0
	total_company_neft_rtgs_year = 0
	total_company_bank_draft_year = 0
	total_company_cheque_year = 0
	total_company_credit_year= 0
	total_individual_cash_year = 0
	total_individual_credit_card_year = 0
	total_individual_neft_rtgs_year = 0
	total_individual_bank_draft_year = 0
	total_individual_cheque_year = 0
	total_individual_credit_year = 0

	current_date = getdate(datetime.datetime.now())
	c_date = frappe.utils.formatdate(current_date, "dd-MM-yyyy")
	now = datetime.datetime.now()
	current_year = now.year
	monthinteger = now.month
	current_month = datetime.date(1900, monthinteger, 1).strftime('%B')
	
	invoice_list_for_day_key      = invoices_day_month_year_list[0]
	invoice_list_for_day          = invoice_list_for_day_key["day"]         
	invoice_list_for_month_key    = invoices_day_month_year_list[1]
	invoice_list_for_month        = invoice_list_for_month_key["month"]         
	invoice_list_for_year_key = invoices_day_month_year_list[2]
	invoice_list_for_year     = invoice_list_for_year_key["year"]
	#day data
	if invoice_list_for_day is not None:
		invoice_type="Day"
		invoice_amount_day = get_invoice_amount(invoice_list_for_day)
		company_details = invoice_amount_day["company"]
		individual_details = invoice_amount_day["individual"]

		total_company_cash_day = company_details["cash"]
		total_company_credit_card_day = company_details["credit_card"]
		total_company_neft_rtgs_day = company_details["neft_rtgs"]
		total_company_bank_draft_day = company_details["bank_draft"]
		total_company_cheque_day = company_details["cheque"]
		total_company_credit_day = company_details["credit"]

		total_individual_cash_day = individual_details["cash"]
		total_individual_credit_card_day = individual_details["credit_card"]
		total_individual_neft_rtgs_day = individual_details["neft_rtgs"]
		total_individual_bank_draft_day = individual_details["bank_draft"]
		total_individual_cheque_day = individual_details["cheque"]
		total_individual_credit_day = individual_details["credit"]		
	#Month_data
	if invoice_list_for_month is not None:
		invoice_type="Month"
		invoice_amount_month = get_invoice_amount(invoice_list_for_month)
		company_details = invoice_amount_month["company"]
		individual_details = invoice_amount_month["individual"]

		total_company_cash_month = company_details["cash"]
		total_company_credit_card_month = company_details["credit_card"]
		total_company_neft_rtgs_month = company_details["neft_rtgs"]
		total_company_bank_draft_month = company_details["bank_draft"]
		total_company_cheque_month = company_details["cheque"]
		total_company_credit_month = company_details["credit"]

		total_individual_cash_month = individual_details["cash"]
		total_individual_credit_card_month = individual_details["credit_card"]
		total_individual_neft_rtgs_month = individual_details["neft_rtgs"]
		total_individual_bank_draft_month = individual_details["bank_draft"]
		total_individual_cheque_month = individual_details["cheque"]
		total_individual_credit_month = individual_details["credit"]		
	#Year data
	if invoice_list_for_year is not None:
		invoice_type="Year"
		invoice_amount_year = get_invoice_amount(invoice_list_for_year)
		company_details = invoice_amount_year["company"]
		individual_details = invoice_amount_year["individual"]

		total_company_cash_year = company_details["cash"]
		total_company_credit_card_year = company_details["credit_card"]
		total_company_neft_rtgs_year = company_details["neft_rtgs"]
		total_company_bank_draft_year = company_details["bank_draft"]
		total_company_cheque_year = company_details["cheque"]
		total_company_credit_year = company_details["credit"]

		total_individual_cash_year = individual_details["cash"]
		total_individual_credit_card_year = individual_details["credit_card"]
		total_individual_neft_rtgs_year = individual_details["neft_rtgs"]
		total_individual_bank_draft_year = individual_details["bank_draft"]
		total_individual_cheque_year = individual_details["cheque"]
		total_individual_credit_year = individual_details["credit"]		
	#start of B2B	
	data.append(["","",str(c_date),(str(current_month) + ", " + str(current_year)),("FY" + str(current_year) + "-"+ str(current_year + 1))]) 
	data.append(["", "", "", ""])
	data.append(["B2B", "Cash", str(total_company_cash_day),str(total_company_cash_month),str(total_company_cash_year)])
	data.append(["", "Credit Card",str(total_company_credit_card_day),str(total_company_credit_card_month),str(total_company_credit_card_year)])
	data.append(["", "NEFT/RTGS",str(total_company_neft_rtgs_day),str(total_company_neft_rtgs_month),str(total_company_neft_rtgs_year)])
	data.append(["", "Bank Draft",str(total_company_bank_draft_day),str(total_company_bank_draft_month),str(total_company_bank_draft_year)])
	data.append(["", "Cheque",str(total_company_cheque_day),str(total_company_cheque_month),str(total_company_cheque_year)])
	data.append(["", "Credit", str(total_company_credit_day),str(total_company_credit_month),str(total_company_credit_year)])			
	
	#start of B2C
	data.append(["", "", "", ""]) 
	data.append(["B2C", "Cash", str(total_individual_cash_day),str(total_individual_cash_month),str(total_individual_cash_year)])
	data.append(["", "Credit Card",str(total_individual_credit_card_day),str(total_individual_credit_card_month),str(total_individual_credit_card_year)])
	data.append(["", "NEFT/RTGS",str(total_individual_neft_rtgs_day),str(total_individual_neft_rtgs_month),str(total_individual_neft_rtgs_year)])
	data.append(["", "Bank Draft",str(total_individual_bank_draft_day),str(total_individual_bank_draft_month),str(total_individual_bank_draft_year)])
	data.append(["", "Cheque",str(total_individual_cheque_day),str(total_individual_cheque_month),str(total_individual_cheque_year)])
	data.append(["", "Credit",str(total_individual_credit_day),str(total_individual_credit_month),str(total_individual_credit_year)])

        #start of Total
	total_cash_day = float( total_company_cash_day ) + float( total_individual_cash_day )
	total_credit_card_day = float( total_company_credit_card_day ) + float( total_individual_credit_card_day )
	total_neft_rtgs_day = float( total_company_neft_rtgs_day ) + float( total_individual_neft_rtgs_day )
	total_bank_draft_day = float( total_company_bank_draft_day ) + float( total_individual_bank_draft_day )
	total_cheque_day = float( total_company_cheque_day ) + float( total_individual_cheque_day )
	total_credit_day = float( total_company_credit_day )+ float( total_individual_credit_day )

	total_cash_month = float( total_company_cash_month ) + float( total_individual_cash_month )
	total_credit_card_month =float( total_company_credit_card_month ) + float( total_individual_credit_card_month )
	total_neft_rtgs_month = float( total_company_neft_rtgs_month ) + float( total_individual_neft_rtgs_month )
	total_bank_draft_month = float( total_company_bank_draft_month ) + float( total_individual_bank_draft_month )
	total_cheque_month = float( total_company_cheque_month ) + float( total_individual_cheque_month )
	total_credit_month =float( total_company_credit_month ) + float( total_individual_credit_month )

	total_cash_year = float(total_company_cash_year) + float(total_individual_cash_year)
	total_credit_card_year = float(total_company_credit_card_year) + float(total_individual_credit_card_year)
	total_neft_rtgs_year = float(total_company_neft_rtgs_year) + float(total_individual_neft_rtgs_year)
	total_bank_draft_year = float(total_company_bank_draft_year) + float(total_individual_bank_draft_year)
	total_cheque_year = float(total_company_cheque_year) + float(total_individual_cheque_year)
	total_credit_year = float(total_company_credit_year) + float(total_individual_credit_year)
	
	data.append(["", "", "", ""])
	data.append(["Total", "Cash", str(total_cash_day),str(total_cash_month),str(total_cash_year)])
	data.append(["", "Credit Card",str(total_credit_card_day),str(total_credit_card_month),str(total_credit_card_year)])
	data.append(["", "NEFT/RTGS",str(total_neft_rtgs_day),str(total_neft_rtgs_month),str(total_neft_rtgs_year)])
	data.append(["", "Bank Draft",str(total_bank_draft_day),str(total_bank_draft_month),str(total_bank_draft_year)])
	data.append(["", "Cheque",str(total_cheque_day),str(total_cheque_month),str(total_cheque_year)])
	data.append(["", "Credit",str( total_credit_day),str(total_credit_month),str(total_credit_year)])

def get_invoice_amount(invoice_list):
	total_company_cash = 0
	total_company_credit_card = 0
	total_company_neft_rtgs = 0
	total_company_bank_draft = 0
	total_company_cheque = 0
	total_company_credit = 0
	total_individual_cash = 0
	total_individual_credit_card = 0
	total_individual_neft_rtgs = 0
	total_individual_bank_draft = 0
	total_individual_cheque = 0
	total_individual_credit = 0
	
	for invoice_data in invoice_list: 
		payment_term = ""
		customer_type = invoice_data['customer_type']
		amount = invoice_data['net_total']
		status = invoice_data['status']
		name = invoice_data['name']
		payment_term_value = get_payment_term(name)

		if len(payment_term_value)!=0:		
			payment_term = payment_term_value[0]["payment_term"]
		
		if payment_term =="Cash":
			if customer_type == "Company":
				total_company_cash = total_company_cash + amount
			elif customer_type == "Individual":
				total_individual_cash = total_individual_cash + amount
		if payment_term =="Credit Card":
			if customer_type == "Company":
				total_company_credit_card = total_company_credit_card + amount
			elif customer_type == "Individual":
				total_individual_credit_card = total_individual_credit_card + amount
		if payment_term =="NEFT/RTGS":
			if customer_type == "Company":
				total_company_neft_rtgs = total_company_neft_rtgs + amount
			elif customer_type == "Individual":
				total_individual_neft_rtgs = total_individual_neft_rtgs + amount
		if payment_term =="Bank Draft":
			if customer_type == "Company":
				total_company_bank_draft = total_company_bank_draft + amount
			elif customer_type == "Individual":
				total_individual_bank_draft = total_individual_bank_draft + amount
		if payment_term =="Cheque":
			if customer_type == "Company":
				total_company_cheque = total_company_cheque + amount
			elif customer_type == "Individual":
				total_individual_cheque = total_individual_cheque + amount
		if payment_term =="Credit":
			if customer_type == "Company":
				total_company_credit = total_company_credit + amount
			elif customer_type == "Individual":
				total_individual_credit = total_individual_credit + amount

		invoice_amount = {"company" : {"cash" : total_company_cash ,
					   "credit_card" : total_company_credit_card,
					   "neft_rtgs" : total_company_neft_rtgs,
					   "bank_draft" : total_company_bank_draft,
					   "cheque" :total_company_cheque,
					   "credit" : total_company_credit },
			      	  "individual": { "cash": total_individual_cash,
				 	      "credit_card":total_individual_credit_card,
					      "neft_rtgs":total_individual_neft_rtgs,
					      "bank_draft":total_individual_bank_draft,
					      "cheque":total_individual_cheque,
					      "credit":total_individual_credit }
			        }
	return invoice_amount
        #end of get amount fun
	
def get_payment_term(name):
	payment_term_value = frappe.db.sql("""select payment_term from `tabPayment Schedule` where parent=%s and docstatus=1""",name,as_dict=1)
	return payment_term_value

def get_day_wise_invoices():
	current_date = getdate(datetime.datetime.now())
	invoice_details = frappe.db.sql("""select customer_type, name, net_total, status from `tabSales Invoice` where posting_date = %s and 
					docstatus=1""", (current_date), as_dict=1)
	if len(invoice_details)!=0:
		return invoice_details
	else:
		return None

def get_month_wise_invoices():
	d = date.today()
	from_date = get_first_day(d)
	to_date = get_last_day(d)
	invoice_details = frappe.db.sql("""select customer_type, name, net_total, status from `tabSales Invoice` where posting_date >= %s and 
					posting_date <= %s and docstatus=1""", (from_date, to_date), as_dict=1)
	if len(invoice_details)!=0:
		return invoice_details
	else:
		return None

def get_year_wise_invoices():
	d = date.today()
	now = datetime.datetime.now()
	current_year = now.year
	from_date = str(current_year) + "-04-01"
	to_date = get_last_day(d)
	invoice_details = frappe.db.sql("""select customer_type, name, net_total, status from `tabSales Invoice` where posting_date >= %s and 
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

def get_last_day(dt,d_years=0, d_months=0):
	y, m = dt.year + d_years, dt.month + d_months
	last = calendar.monthrange(y,m)
	last_day = last[1]
	a, m = divmod(m-1, 12)
	return date(y+a, m+1,last_day)
