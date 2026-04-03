from flask import Blueprint, request, jsonify
from datetime import datetime

from ..schema import CategorySchema, CategoryDetailSchema
from ..models import db, Category

categories_bp = Blueprint('categories', __name__)

# =============== ROUTES ===============
@categories_bp.get('/categories')
def list_categories():
    categories = Category.query.all()
    schema = CategorySchema(many=True)
    return jsonify(schema.dump(categories)), 200

@categories_bp.get('/categories/<int:category_id>')
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    schema = CategoryDetailSchema()
    return jsonify(schema.dump(category)), 200

@categories_bp.post('/categories')
def create_category():
    data = request.get_json()

    schema = CategorySchema()
    try:
        category_data = schema.load(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    # check for uniqueness
    existing_category = Category.query.filter_by(name=category_data['name']).first()
    if existing_category:
        return jsonify({'error': 'Category with this name already exists'}), 400
    
    new_category = Category(
        name=category_data['name'],
        color=category_data.get('color')
    )
    db.session.add(new_category)
    db.session.commit()

    return jsonify(schema.dump(new_category)), 201

@categories_bp.delete('/categories/<int:category_id>')
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)

    # make sure that response has no tasks
    if len(category.tasks) > 0:
        return jsonify({'error': 'Cannot delete category with associated tasks'}), 400

    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted'}), 200