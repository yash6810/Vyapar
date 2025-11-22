# Deterministic workflow runner - acts on validated JSON
from typing import Dict

import json, uuid, os

os.makedirs('data/invoices', exist_ok=True)
os.makedirs('data/expenses', exist_ok=True)


def create_invoice(payload: Dict):
    inv_id = str(uuid.uuid4())
    path = f'data/invoices/{inv_id}.json'
    with open(path, 'w') as f:
        json.dump(payload, f, indent=2)
    total = payload.get('total')
    client = payload.get('client_name')
    return {'invoice_id': inv_id, 'summary': f'Invoice {inv_id} for {client} saved. Total: {total}'}


def record_expense(payload: Dict):
    exp_id = str(uuid.uuid4())
    path = f'data/expenses/{exp_id}.json'
    with open(path, 'w') as f:
        json.dump(payload, f, indent=2)
    return {'expense_id': exp_id, 'summary': f'Expense {exp_id} recorded. Amount: {payload.get("amount")}' }
