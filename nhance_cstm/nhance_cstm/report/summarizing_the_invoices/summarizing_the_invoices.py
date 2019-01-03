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
	data.append(["Day", "", ""])
	get_day_wise_invoices()

	data.append(["", "", ""])
	data.append(["Month To Date", "", ""])
	get_month_wise_invoices()
	
	data.append(["", "", ""])
	data.append(["Year To Date", "", ""])
	get_year_wise_invoices()
	
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

def get_day_wise_invoices():
	current_date = getdate(datetime.datetime.now())
	c_date = frappe.utils.formatdate(current_date, "dd-MM-yyyy")
	individual_day = 0
	company_day = 0
	individual_day_key = frappe.db.sql("""select sum(net_total) as sum_net_total from `tabSales Invoice` where posting_date = %s and 
					docstatus=1 and customer_type= "Individual" """, (current_date), as_dict=1)
	if individual_day_key[0]["sum_net_total"]!= None:
		individual_day = individual_day_key[0]["sum_net_total"]		

	company_day_key = frappe.db.sql("""select sum(net_total) as sum_net_total from `tabSales Invoice` where posting_date = %s and 
					docstatus=1 and customer_type= "Company" """, (current_date), as_dict=1)
	if company_day_key[0]["sum_net_total"]!= None:
		company_day = company_day_key[0]["sum_net_total"]

	total_day = individual_day + company_day
	
	data.append([str(c_date), individual_day, company_day, total_day])	


def get_month_wise_invoices():
	d = date.today()
	from_date = get_first_day(d)
	to_date = getdate(datetime.datetime.now())
	now = datetime.datetime.now()
	current_year = now.year
	monthinteger = now.month
	current_month = datetime.date(1900, monthinteger, 1).strftime('%B')

	individual_month = 0
	company_month = 0

	individual_month_key = frappe.db.sql("""select sum(net_total) as sum_net_total from `tabSales Invoice` where posting_date >= %s and posting_date <= %s and docstatus=1 and customer_type= "Individual" """, (from_date, to_date), as_dict=1)
	if individual_month_key[0]["sum_net_total"]!= None:
		individual_month = individual_month_key[0]["sum_net_total"]	

	company_month_key = frappe.db.sql("""select sum(net_total) as sum_net_total from `tabSales Invoice` where posting_date >= %s and posting_date <= %s and docstatus=1 and customer_type= "Company" """, (from_date, to_date), as_dict=1)
	if company_month_key[0]["sum_net_total"]!= None:
		company_month = company_month_key[0]["sum_net_total"]

	total_month = individual_month + company_month

	data.append([ (str(current_month) + ", " + str(current_year)), individual_month,company_month, total_month])

def get_year_wise_invoices():
	now = datetime.datetime.now()
	current_year = now.year
	fiscal_year = frappe.defaults.get_user_default("fiscal_year")
	fiscal_year_start = fiscal_year[:4]
	from_date = str(fiscal_year_start) + "-04-01"
	to_date = getdate(datetime.datetime.now())


	individual_year = 0
	company_year = 0

	individual_year_key = frappe.db.sql("""select sum(net_total) as sum_net_total from `tabSales Invoice` where posting_date >= %s and 
					posting_date <= %s and docstatus=1 and customer_type="Individual" """, (from_date, to_date), as_dict=1)
	if individual_year_key[0]["sum_net_total"]!= None:
		individual_year = individual_year_key[0]["sum_net_total"]

	company_year_key = frappe.db.sql("""select sum(net_total) as sum_net_total from `tabSales Invoice` where posting_date >= %s and 
					posting_date <= %s and docstatus=1 and customer_type="Company" """, (from_date, to_date), as_dict=1)
	if company_year_key[0]["sum_net_total"]!= None:
		company_year = company_year_key[0]["sum_net_total"]

	total_year = individual_year + company_year

	data.append([ ("FY" + fiscal_year_start + "-"+ str(current_year)), individual_year,company_year, total_year])

def get_first_day(dt, d_years=0, d_months=0):
    # d_years, d_months are "deltas" to apply to dt
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m-1, 12)
    return date(y+a, m+1, 1)


