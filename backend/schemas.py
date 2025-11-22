# JSON schemas and validation helpers
from jsonschema import validate, ValidationError

INVOICE_SCHEMA = {
    'type': 'object',
    'required': ['client_name','invoice_date','items','gst_pct','total', 'due_date'],
    'properties': {
        'client_name': {'type': 'string'},
        'invoice_date': {'type': 'string', 'pattern':'^\\d{4}-\\d{2}-\\d{2}$'},
        'due_date': {'type': 'string', 'pattern':'^\\d{4}-\\d{2}-\\d{2}$'},
        'status': {'type': 'string', 'default': 'unpaid'},
        'items': {'type': 'array'},
        'gst_pct': {'type': 'number'},
        'total': {'type': 'number'},
        'currency': {'type': 'string', 'default': 'INR'},
        'tags': {'type': 'array', 'items': {'type': 'string'}}
    }
}

EXPENSE_SCHEMA = {
    'type': 'object',
    'required': ['category','amount','date','payment_method'],
    'properties': {
        'category': {'type': 'array', 'items': {'type': 'string'}},
        'amount': {'type':'number'},
        'vendor': {'type':'string'},
        'date': {'type':'string'},
        'payment_method': {'type':'string'},
        'gst_applicable': {'type':'boolean'},
        'notes': {'type':'string'},
        'currency': {'type': 'string', 'default': 'INR'}
    }
}


def validate_schema(data: dict, schema: dict):
    try:
        validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)


def validate_invoice(data: dict):
    return validate_schema(data, INVOICE_SCHEMA)


from dateutil.parser import parse

...

def validate_expense(data: dict):
    is_valid, err = validate_schema(data, EXPENSE_SCHEMA)
    if not is_valid:
        return is_valid, err
    
    try:
        # Validate and reformat date
        parsed_date = parse(data['date'])
        data['date'] = parsed_date.strftime('%Y-%m-%d')
        return True, None
    except ValueError:
        return False, "Invalid date format"
