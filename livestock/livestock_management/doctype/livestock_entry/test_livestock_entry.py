# Copyright (c) 2023, Bantoo and Contributors
# See license.txt

# import frappe
from frappe.tests.utils import FrappeTestCase


class TestLivestockEntry(FrappeTestCase):
    pass

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime
from datetime import datetime

class LivestockEntry(Document):
    def on_submit(self):
        # Check if this is the first Livestock Entry for the user's company
        existing_balance = frappe.get_all(
            "Livestock Balance",
            filters={"company": self.company, "livestock": self.livestock},
            fields=["name"],
            limit=1,
        )

        if not existing_balance:
            if self.entry_type != "Stock Take":
                frappe.throw(_("You need to enter the first <strong>Stock Take</strong> entry for <strong>{0}</strong>.").format(self.livestock))

            # Create initial Livestock Balance entry for Stock Take
            livestock_balance = frappe.new_doc("Livestock Balance")
            livestock_balance.company = self.company
            livestock_balance.livestock = self.livestock
            livestock_balance.current_balance = self.quantity
            livestock_balance.last_balance = 0
            livestock_balance.last_transaction = self.name
            livestock_balance.insert(ignore_permissions=True)

        else:
            livestock_balance = frappe.get_doc("Livestock Balance", existing_balance[0].name)
            last_balance = livestock_balance.current_balance

            if get_datetime(self.date) < get_datetime(livestock_balance.date):
                livestock_balance.current_balance = self.recalculate_balance(last_balance)

            else:
                if self.entry_type == "Stock Take":
                    # Update Livestock Balance for Stock Take
                    livestock_balance.current_balance = self.quantity

                else:
                    effect_on_qty = frappe.get_value("Livestock Entry Type", self.entry_type, "effect_on_qty")
                    if effect_on_qty == "Increase":
                        # Update Livestock Balance for Increase
                        livestock_balance.current_balance = last_balance + self.quantity
                    elif effect_on_qty == "Decrease":
                        # Update Livestock Balance for Decrease
                        livestock_balance.current_balance = last_balance - self.quantity

            livestock_balance.last_balance = last_balance
            livestock_balance.last_transaction = self.name
            livestock_balance.save(ignore_permissions=True)

    def on_cancel(self):
        existing_balance = frappe.get_all(
            "Livestock Balance",
            filters={"company": self.company, "livestock": self.livestock},
            fields=["name"],
            limit=1,
        )
        livestock_balance = frappe.get_doc("Livestock Balance", existing_balance[0].name)
        last_balance = livestock_balance.current_balance
        livestock_balance.current_balance = self.recalculate_balance(last_balance)
        livestock_balance.last_balance = last_balance
        livestock_balance.save(ignore_permissions=True)

    def recalculate_balance(self, last_balance):
        # Adjust the balances starting from the previous stock take
        previous_stock_take = frappe.get_all(
            "Livestock Entry",
            filters={
                "company": self.company,
                "livestock": self.livestock,
                "entry_type": "Stock Take",
                "date": ("<=", self.date),
                "docstatus": 1,
            },
            fields=["date", "quantity", "entry_type"],
            order_by="date DESC",
            limit=1,
        )

        if previous_stock_take:
            last_balance = previous_stock_take[0].quantity

        # Adjust the balances for subsequent entries
        stock_entries = frappe.get_all(
            "Livestock Entry",
            filters={
                "company": self.company,
                "livestock": self.livestock,
                "date": (">=", previous_stock_take[0].date),
                "docstatus": 1,
            },
            fields=["name", "quantity", "entry_type"],
            order_by="date",
            limit=0
        )

        for entry in stock_entries:
            if entry.entry_type == "Stock Take":
                last_balance = entry.quantity
                continue

            effect_on_qty = frappe.get_value("Livestock Entry Type", entry.entry_type, "effect_on_qty")
            if effect_on_qty == "Increase":
                last_balance += entry.quantity
            elif effect_on_qty == "Decrease":
                last_balance -= entry.quantity

        return last_balance


# Tests
def test_livestock_entry():
    entry = LivestockEntry()
    entry.company = "Test Company"
    entry.livestock = "Test Livestock"
    entry.quantity = 10
    entry.date = datetime.now()

    # Test case: First entry is not Stock Take
    entry.entry_type = "Increase"
    try:
        entry.on_submit()
    except frappe.exceptions.ValidationError as e:
        assert str(e) == "You need to enter the first Stock Take entry for Test Livestock."

    # Test case: First entry is Stock Take
    entry.entry_type = "Stock Take"
    entry.on_submit()

    # Test case: Submitting a subsequent Increase entry
    entry.quantity = 5
    entry.entry_type = "Increase"
    entry.on_submit()
    livestock_balance = frappe.get_value(
        "Livestock Balance",
        filters={"company": "Test Company", "livestock": "Test Livestock"},
        fieldname=["current_balance"]
    )
    assert livestock_balance == 15

    # Test case: Submitting a subsequent Decrease entry
    entry.quantity = 3
    entry.entry_type = "Decrease"
    entry.on_submit()
    livestock_balance = frappe.get_value(
        "Livestock Balance",
        filters={"company": "Test Company", "livestock": "Test Livestock"},
        fieldname=["current_balance"]
    )
    assert livestock_balance == 12

    # Test case: Submitting a backdated Increase entry
    entry.quantity = 2
    entry.entry_type = "Increase"
    entry.date = datetime.now().replace(year=2022)
    entry.on_submit()
    livestock_balance = frappe.get_value(
        "Livestock Balance",
        filters={"company": "Test Company", "livestock": "Test Livestock"},
        fieldname=["current_balance"]
    )
    assert livestock_balance == 14

    # Test case: Submitting a backdated Decrease entry
    entry.quantity = 4
    entry.entry_type = "Decrease"
    entry.date = datetime.now().replace(year=2021)
    entry.on_submit()
    livestock_balance = frappe.get_value(
        "Livestock Balance",
        filters={"company": "Test Company", "livestock": "Test Livestock"},
        fieldname=["current_balance"]
    )
    assert livestock_balance == 10

    # Test case: Cancel a submitted entry
    entry.on_cancel()
    livestock_balance = frappe.get_value(
        "Livestock Balance",
        filters={"company": "Test Company", "livestock": "Test Livestock"},
        fieldname=["current_balance"]
    )
    assert livestock_balance == 14

    print("Livestock Entry tests passed!")


if __name__ == "__main__":
    test_livestock_entry()

test_livestock_entry()