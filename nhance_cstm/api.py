from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words
from frappe import _, throw, msgprint
from frappe.model.mapper import get_mapped_doc

from frappe.model.naming import make_autoname

from erpnext.utilities.transaction_base import TransactionBase
from erpnext.accounts.party import get_party_account_currency
from frappe.desk.notifications import clear_doctype_notifications

@frappe.whitelist()
def make_proposal_stage(source_name, target_doc=None):


	target_doc = get_mapped_doc("Opportunity", source_name, {
		"Opportunity": {
			"doctype": "Proposal Stage",
			"field_map": {
				"doctype": "stage_doctype",
				"name": "document_number"
			 }
		}
	
	}, target_doc, set_missing_values)


	return target_doc

@frappe.whitelist()
def make_proposal_stage_q(source_name, target_doc=None):


	target_doc = get_mapped_doc("Quotation", source_name, {
		"Quotation": {
			"doctype": "Proposal Stage",
			"field_map": {
				"name": "document_number",
				"doctype": "stage_doctype"
			 }
		}
	
	}, target_doc, set_missing_values)


	return target_doc


@frappe.whitelist()
def make_interactions(source_name, target_doc=None):

	target_doc = get_mapped_doc("Opportunity", source_name, {
		"Opportunity": {
			"doctype": "Interactions",
			"field_map": {
				"name": "opportunity",
				"doctype": "reference_doctype"
				}
		}
		
	}, target_doc, set_missing_values)

	return target_doc

@frappe.whitelist()
def make_interactions_quot(source_name, target_doc=None):
	src_name = "Quotation"
	target_doc = get_mapped_doc("Quotation", source_name, {
		"Quotation": {
			"doctype": "Interactions",
			"field_map": {
				"name": "quotation",
				"doctype": "reference_doctype"
				}
		}
		
	}, target_doc, set_missing_values)

	return target_doc

@frappe.whitelist()
def make_interactions_so(source_name, target_doc=None):
	src_name = "Sales Order"
	target_doc = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Interactions",
			"field_map": {
				"name": "sales_order",
				"doctype": "reference_doctype"
				}
		}
		
	}, target_doc, set_missing_values)

	return target_doc

@frappe.whitelist()
def make_interactions_si(source_name, target_doc=None):
	src_name = "Sales Invoice"
	target_doc = get_mapped_doc("Sales Invoice", source_name, {
		"Sales Invoice": {
			"doctype": "Interactions",
			"field_map": {
				"name": "reference_document",
				"doctype": "reference_doctype"
				}
		}
		
	}, target_doc, set_missing_values)

	return target_doc


@frappe.whitelist()
def set_proposal_stage_values(opportunity):

        
	max_closing_date = frappe.db.sql("""select max(closing_date) from `tabProposal Stage` where reference_name=%s""",
				(opportunity))
				
        sc_rec = frappe.db.sql("""select value, closing_date, stage, opportunity_purpose, buying_status, support_needed, competition_status
		from `tabProposal Stage`
		where reference_name=%s and closing_date = %s""",
		(opportunity, max_closing_date))
        return sc_rec

def set_missing_values(source, target_doc):
	target_doc.run_method("set_missing_values")
	target_doc.run_method("calculate_taxes_and_totals")

@frappe.whitelist()
def get_contact(customer):
	contact = frappe.db.sql("""select con.name from `tabContact` con, `tabDynamic Link` dy where dy.link_name = %s and dy.parent = con.name""", (customer))
	
	return contact


@frappe.whitelist()
def get_address(customer):
	address = frappe.db.sql("""select ad.name from `tabAddress` ad, `tabDynamic Link` dy where dy.link_name = %s and dy.parent = ad.name""", (customer))

	return address
	

@frappe.whitelist()
def get_item_price_details(item_code):
	
	item_details = []
	supplier_details = []
	last_3Days_Details = frappe.db.sql("""select rate,parent from `tabPurchase Order Item` as tpoi where item_code = %s and DATE(creation) > (NOW() - INTERVAL 3 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled')) order by creation desc limit 3""", (item_code), as_dict=1)
	#print "############-length of last_3Days_Details[0]['parent']::", (last_3Days_Details)
	i=0
	for po_Number in last_3Days_Details:
		last_3Days_po_Number = last_3Days_Details[i]['parent']
		last_3Days_supplier = frappe.db.sql("""select supplier from `tabPurchase Order` where name = %s and DATE(creation) > (NOW() - INTERVAL 3 DAY) order by creation desc limit 3""", last_3Days_po_Number, as_dict=1)
		supplier_details.extend(last_3Days_supplier)
		i = i + 1
	#print "###-supplier_details::", supplier_details
	max_last_180Days_Details = frappe.db.sql("""select parent,rate as max_price_rate from (select parent,rate from `tabPurchase Order Item`  as tpoi where item_code = %s and DATE(creation) > (NOW() - INTERVAL 180 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled')) order by rate desc limit 1) t1""", (item_code), as_dict=1)
	#print "#######-max_last_180Days_Details::", max_last_180Days_Details
	max_last_180Days_po_Number = max_last_180Days_Details[0]['parent']
	max_last_180Days_supplier = frappe.db.sql("""select supplier from `tabPurchase Order` where name = %s""", max_last_180Days_po_Number, as_dict=1)


	min_last_180Days_Details = frappe.db.sql("""select parent,rate as min_price_rate from (select parent,rate from `tabPurchase Order Item`  as tpoi where item_code = %s and DATE(creation) > (NOW() - INTERVAL 180 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled')) order by rate asc limit 1) t1""", (item_code), as_dict=1)

	#print "#######-min_last_180Days_Details::", min_last_180Days_Details
	min_last_180Days_po_Number = min_last_180Days_Details[0]['parent']
	min_last_180Days_supplier = frappe.db.sql("""select supplier from `tabPurchase Order` where name = %s""", min_last_180Days_po_Number, as_dict=1)

	last_180Days_Avg_Price = frappe.db.sql("""select avg(rate) as avg_price from `tabPurchase Order Item` as tpoi where item_code = %s and DATE(creation) > (NOW() - INTERVAL 180 DAY) and ((select status from `tabPurchase Order` where name=tpoi.parent) not in ('Draft','Cancelled'))""", (item_code), as_dict=1)


	#last_3Days_Details.extend(last_3Days_supplier)
	max_last_180Days_Details.extend(max_last_180Days_supplier)
	min_last_180Days_Details.extend(min_last_180Days_supplier)

	item_details.append(last_3Days_Details)
	item_details.append(max_last_180Days_Details)
	item_details.append(min_last_180Days_Details)
	item_details.append(last_180Days_Avg_Price)
	item_details.append(supplier_details)
	print "###############-item_details::", item_details
	return item_details
