from flask import Blueprint, abort, make_response, Response, request
import requests
from app.models.task import Task
from datetime import datetime
from sqlalchemy import asc, desc
from .route_utilities import validate_model, create_model, get_models_with_filters
from ..db import db
import os


bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@bp.post("")
def create_task():
    request_body = request.get_json()
    
    if "title" not in request_body or "description" not in request_body:
        return {"details": "Invalid data"}, 400
    
    task_data = {"title": request_body.get("title"), 
                 "description": request_body.get("description"), 
                 "completed_at": request_body.get("completed_at")}

    task_dict, status_code = create_model(Task, task_data)
    return {"task": task_dict}, status_code

@bp.get("")
def get_task():
    query_params = request.args.to_dict()
    sort_order = query_params.pop('sort', 'asc')
    sort_by = query_params.pop('sort_by', 'title')
    tasks_response = get_models_with_filters(Task, sort_by=sort_by, sort_order=sort_order)
    return tasks_response, 200
  

@bp.get("/<task_id>")
def get_one_task(task_id):
    task = validate_model(Task, task_id)
    response = {"task": task.to_dict()}

    if task.goal_id is not None: 
        response["task"]["goal_id"] = task.goal_id
    return response, 200

@bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()
    task.title = request_body["title"]
    task.description = request_body["description"]

    db.session.commit()

    return {"task": task.to_dict()}, 200

@bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)
    db.session.delete(task)
    db.session.commit()

    response = {
        "details": f'Task {task.id} "{task.title}" successfully deleted'
    }
    
    return response, 200


@bp.patch("/<task_id>/mark_complete")
def mark_task_complete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = datetime.now()
    db.session.commit()

    slack_token = os.environ.get("SLACK_BOT_TOKEN")  
    url = "https://slack.com/api/chat.postMessage"
    headers = {"Authorization": f"Bearer {slack_token}"}
    request_body = {
        "channel": "task-notifications",  
        "text": f"Someone just completed the task '{task.title}'"
    }
    requests.post(url, json=request_body, headers=headers)
    
    return{"task": task.to_dict()}, 200


@bp.patch("/<task_id>/mark_incomplete")
def mark_task_incomplete(task_id):
   
    task = validate_model(Task, task_id)

    task.completed_at = None
    db.session.commit()

    return {"task": task.to_dict()}
    
    