from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, timezone
from redis import Redis
from rq import Queue
import os

from ..schema import TaskSchema
from ..models import db, Task
from ..jobs import send_reminder

tasks_bp = Blueprint('tasks', __name__)

redis_client = Redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'))
task_queue = Queue('tasks', connection=redis_client)

def queue_notification(due_date):
    if not due_date:
        return False
    
    now = datetime.now(timezone.utc)

    if due_date.tzinfo is None:
        due_date = due_date.replace(tzinfo=timezone.utc)

    if due_date <= now:
        return False
    
    twenty_four_hours_later = now + timedelta(hours=24)
    return due_date <= twenty_four_hours_later

# =============== ROUTES ===============

@tasks_bp.get('/tasks')
def list_tasks():
    query = Task.query
    
    completed = request.args.get('completed')
    if completed is not None:
        is_completed = completed.lower() == 'true'
        query = query.filter_by(completed=is_completed)
    
    tasks = query.all()

    schema = TaskSchema(many=True)
    return jsonify({
        "tasks": schema.dump(tasks)
    }), 200


@tasks_bp.get('/tasks/<int:task_id>')
def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    schema = TaskSchema()
    return jsonify(schema.dump(task)), 200


@tasks_bp.post('/tasks')
def create_task():
    data = request.get_json()
    
    schema = TaskSchema()
    try:
        task_data = schema.load(data)
    except Exception as e:
        # return jsonify({'error': str(e)}), 400
        return jsonify({'error': e.messages}), 400
    
    new_task = Task(
        title=task_data['title'],
        description=task_data.get('description'),
        completed=task_data.get('completed', False),
        due_date=task_data.get('due_date'),
        category_id=task_data.get('category_id')
    )
    db.session.add(new_task)
    db.session.commit()

    # Background Task Logic
    notification_queued = False
    if queue_notification(new_task.due_date):
        task_queue.enqueue(send_reminder, new_task.title)
        notification_queued = True

    response_data = schema.dump(new_task)

    return jsonify({
        'task': response_data,
        'notification_queued': notification_queued
    }), 201


@tasks_bp.put('/tasks/<int:task_id>')
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()

    # partial=True allows for partial updates, so we don't require all fields to be present
    schema = TaskSchema(partial=True)
    try:
        task_data = schema.load(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    if 'title' in task_data:
        task.title = task_data['title']
    if 'description' in task_data:
        task.description = task_data['description']
    if 'completed' in task_data:
        task.completed = task_data['completed']
    if 'due_date' in task_data:
        task.due_date = datetime.fromisoformat(task_data['due_date']) if task_data['due_date'] else None
    if 'category_id' in task_data:
        task.category_id = task_data['category_id']
    if 'category' in task_data:
        task.category = task_data['category']

    db.session.commit()
    
    schema = TaskSchema()
    return jsonify(schema.dump(task)), 200


@tasks_bp.delete('/tasks/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'}), 200