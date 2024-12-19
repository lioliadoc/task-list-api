from flask import Blueprint, request, abort, make_response
from app.models.goal import Goal
from app.models.task import Task
from .route_utilities import validate_model, create_model, get_models_with_filters
from ..db import db

bp = Blueprint("goal_bp", __name__, url_prefix="/goals")

@bp.post("")
def create_goal():
    request_body = request.get_json()
    if "title" not in request_body or not request_body["title"]:
        return {"details": "Invalid data"}, 400
    
    goal_data = {"title": request_body.get("title")}
    goal_dict, status_code = create_model(Goal, goal_data)

    return {"goal": goal_dict}, status_code

@bp.get("")
def get_goal():

    goals_response = get_models_with_filters(Goal)
    return goals_response, 200
    

@bp.get("/<goal_id>")
def get_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)
   
    return {"goal":goal.to_dict()}


@bp.put("<goal_id>")
def update_one_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()
    
    goal.title = request_body["title"]
    db.session.commit()

    return {"goal": goal.to_dict()}, 200
 

@bp.delete("<goal_id>")
def delete_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    
    db.session.delete(goal)
    db.session.commit()

    response = {
        "details": f'Goal {goal.id} "{goal.title}" successfully deleted'
    }
    return response, 200

@bp.post("/<goal_id>/tasks")
def associate_tasks_with_goal(goal_id):
    goal = validate_model(Goal, goal_id) 
    request_body = request.get_json()
    task_ids = request_body.get("task_ids", [])
    
    for task_id in task_ids:
        task = validate_model(Task,task_id)  
        task.goal_id = goal.id
    
    db.session.commit()
    
    return {
        "id": goal.id,
        "task_ids": task_ids
    }, 200

@bp.get("/<goal_id>/tasks")
def get_tasks_of_goal(goal_id):
    goal = validate_model(Goal, goal_id)  
    
    tasks_data = [
        {
            "id": task.id,
            "goal_id": task.goal_id,
            "title": task.title,
            "description": task.description,
            "is_complete": bool(task.completed_at)
        }
        for task in goal.tasks
    ]
    
    return {
        "id": goal.id,
        "title": goal.title,
        "tasks": tasks_data
    }, 200

