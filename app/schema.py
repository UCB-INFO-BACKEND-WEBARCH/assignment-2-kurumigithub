from marshmallow import Schema, fields, validate, ValidationError
import re

def validate_title(title):
    if not title or len(title) < 1 or len(title) > 100:
        raise ValidationError('Length must be between 1 and 100.')
    
def validate_description(description):
    if description and len(description) > 500:
        raise ValidationError('Length must not exceed 500.')
    
def validate_name(name):
    if not name or len(name) < 1 or len(name) > 50:
        raise ValidationError('Length must be between 1 and 50.')
    
def validate_color(color):
    if color and not re.match(r'^#[A-Fa-f0-9]{6}$', color):
        raise ValidationError('Must be a valid hex color code.')


class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate_title)
    description = fields.Str(allow_none=True, validate=validate_description)
    completed = fields.Bool(load_default=False)
    due_date = fields.DateTime(allow_none=True, format='iso8601')
    category_id = fields.Int(allow_none=True)
    category = fields.Nested(
        'CategorySchema', 
        only=('id', 'name', 'color'), 
        dump_only=True)
    created_at = fields.DateTime(dump_only=True, format='iso')
    updated_at = fields.DateTime(dump_only=True, format='iso')

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate_name)
    color = fields.Str(allow_none=True, validate=validate_color)

    task_count = fields.Method('get_task_count', dump_only=True)
    def get_task_count(self, obj):
        return len(obj.tasks) if obj.tasks else 0
    
class CategoryDetailSchema(CategorySchema):
    tasks = fields.List(fields.Nested("TaskSchema", exclude=('category',)), dump_only=True)