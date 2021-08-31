from marshmallow import fields
from marshmallow import Schema


class CsvExportSchema(Schema):
    Email = fields.String(attribute='E-mail')
