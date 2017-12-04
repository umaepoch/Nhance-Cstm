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
				"name": "reference_name"
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
				"name": "reference_document",
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
def make_bom(source_name, target_doc=None):

	quot_record = frappe.get_doc("Quotation", source_name)
	

	company = quot_record.company
	single_bom = 0

	project = frappe.db.sql("""select distinct so.project from `tabSales Order` so, `tabSales Order Item` si where si.parent = so.name and si.prevdoc_docname = %s""", (quot_record.name))
	if project:
		project_id = project[0][0]
		quot_record_items = frappe.db.sql("""select qi.item_code as qi_item, qi.qty as qty, qi.grouping as qi_group from `tabQuotation Item` qi where qi.parent = %s and qi.create_bom = 1 and bom_level = 2 order by qi.grouping""" , (quot_record.name), as_dict=1)

		if quot_record_items:

						
			for quot_record_item in quot_record_items:
				bom_main_item = quot_record_item.qi_item
				bom_qty = quot_record_item.qty
				grouping = quot_record_item.qi_group

				quot_record_bom_items = frappe.db.sql("""select qi.item_code as qi_item, qi.qty as qty from `tabQuotation Item` qi where qi.parent = %s and qi.create_bom = 0 and qi.grouping = %s and qi.display_in_quotation = 0 order by qi.item_code""" , (quot_record.name, grouping), as_dict=1)
			
				if quot_record_bom_items:
					
					newJson = {
					"company": company,
					"doctype": "BOM",
					"item": bom_main_item,
					"quantity": bom_qty,
					"project": project_id,
					"items": [
					]
					}
					
					for record in quot_record_bom_items:
						item = record.qi_item
						qty = record.qty

						if item:
							item_record = frappe.get_doc("Item", item)

			
			
							innerJson =	{
								"doctype": "BOM Item",
								"item_code": item,
								"description": item_record.description,
								"uom": item_record.stock_uom,
								"qty": qty
	
						
								}
		
							newJson["items"].append(innerJson)

					doc = frappe.new_doc("BOM")
					doc.update(newJson)
					doc.save()
					frappe.db.commit()
					doc.submit()
					docname = doc.name
					frappe.msgprint(_("BOM Created - " + docname))

				else:
					frappe.msgprint(_("There are no BOM Items present in the quotation. Could not create a BOM for this Item."))
					
		else:
			single_bom = 1

		quot_record_items1 = frappe.db.sql("""select qi.item_code as qi_item, qi.qty as qty, qi.grouping as qi_group from `tabQuotation Item` qi where qi.parent = %s and qi.create_bom = 1 and bom_level = 1 order by qi.grouping""" , (quot_record.name), as_dict=1)
		if quot_record_items1:
	
			for quot_record_item in quot_record_items1:
				bom_main_item = quot_record_item.qi_item
				bom_qty = quot_record_item.qty
				grouping = quot_record_item.qi_group

				if single_bom == 1:

					quot_record_bom_items = frappe.db.sql("""select qi.item_code as qi_item, qi.qty as qty from `tabQuotation Item` qi where qi.parent = %s and qi.create_bom = 0 and qi.display_in_quotation = 0 order by qi.item_code""" , (quot_record.name), as_dict=1)
				else:
					quot_record_bom_items = frappe.db.sql("""select qi.item_code as qi_item, qi.qty as qty from `tabQuotation Item` qi where qi.parent = %s and ((qi.create_bom = 1 and qi.display_in_quotation = 0 and bom_level = 2) or (qi.create_bom = 0 and grouping = %s and qi.item_code != "Control Panel") or (qi.create_bom = 0 and grouping = "" and qi.display_in_quotation = 0)) order by qi.item_code""" , (quot_record.name, grouping), as_dict=1)

				if quot_record_bom_items:
					
					newJson = {
					"company": company,
					"doct2ype": "BOM",
					"item": bom_main_item,
					"quantity": bom_qty,
					"project": project_id,
					"items": [
					]
					}
					
					for record in quot_record_bom_items:
						item = record.qi_item
						qty = record.qty

						if item:
							item_record = frappe.get_doc("Item", item)

			
			
							innerJson =	{
								"doctype": "BOM Item",
								"item_code": item,
								"description": item_record.description,
								"uom": item_record.stock_uom,
								"qty": qty
	
						
								}
		
							newJson["items"].append(innerJson)

					doc = frappe.new_doc("BOM")
					doc.update(newJson)
					doc.save()
					frappe.db.commit()
					doc.submit()
					docname = doc.name
					frappe.msgprint(_("BOM Created - " + docname))

				else:
					frappe.msgprint(_("There are no BOM Items present in the quotation. Could not create a BOM for this Item."))
					
		else:
				frappe.throw(_("There are no BOMs to be created."))

		
	else:
		frappe.msgprint(_("Please create Sales Order and Project before creating BOM"))
	

@frappe.whitelist()
def make_cust_project(source_name, target_doc=None):
	global alloc_whse
	def postprocess(source, doc):
		doc.project_type = "External"
		sales_record = frappe.get_doc("Sales Order", source_name)
		customer = sales_record.customer
		doc.project_name = customer + "-" + source_name[-5:]
 		doc.production_bench = get_free_workbenches()

		if doc.production_bench:
			pass
		else:
			frappe.msgprint(_("There is no free production bench available. Please allocate manually"))

	doc = get_mapped_doc("Sales Order", source_name, {
		"Sales Order": {
			"doctype": "Project",
			"validation": {
				"docstatus": ["=", 1]
			},
			"field_map":{
				"name" : "sales_order",
				"base_grand_total" : "estimated_costing",
			}
		},
		"Sales Order Item": {
			"doctype": "Project Task",
			"field_map": {
				"description": "title",
			},
		}
	}, target_doc, postprocess)

	return doc

@frappe.whitelist()
def get_free_workbenches():

	workbench_warehouses = frappe.db.sql("""select name from `tabWarehouse` where parent_warehouse = "Production Benches - PISPL" order by name""", as_dict=1)

	for whse_record in workbench_warehouses:
		alloc_whse = frappe.db.sql("""select is_active from `tabProject` where production_bench = %s and is_active = "Yes" order by name""", (whse_record["name"]), as_dict=1)
		if alloc_whse:
			pass
		else:
			return whse_record["name"]

