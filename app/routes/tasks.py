from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.services.supabase_client import supabase
from app.auth.dependencies import get_current_user
from datetime import datetime, timezone
from enum import Enum

router = APIRouter(prefix="/tasks", tags=["tasks"])

class TaskStatus(str, Enum):
    created = "created"
    assigned = "assigned"
    in_process = "in_process"
    completed = "completed"

class TaskCreateRequest(BaseModel):
    title: str
    description: str
    total_minutes: float
    user_id: str

class TaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    total_minutes: Optional[float] = None
    user_id: Optional[str] = None
    status: Optional[TaskStatus] = None



@router.post("/create")
def create_task(task: TaskCreateRequest, current_user: dict = Depends(get_current_user)):
    try:
        if not current_user["is_admin"]:
            raise HTTPException(status_code=403, detail="Not authorized. Only admins can create tasks.")
        
        res = supabase.table("tasks").insert({
            "title": task.title,
            "description": task.description,
            "total_minutes": task.total_minutes,
            "user_id": task.user_id,
            "status": TaskStatus.created,
        }).execute()

        if not res.data:
            raise HTTPException(status_code=500, detail="Task creation failed")

        return res.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/{task_id}")
def get_task(task_id: str, current_user: dict = Depends(get_current_user)):
    try:
        if not current_user["is_admin"]:
            res = supabase.table("tasks").select("*").eq("id", task_id).eq("user_id", current_user["id"]).execute()
        else:
            res = supabase.table("tasks").select("*").eq("id", task_id).execute()

        if not res.data:
            raise HTTPException(status_code=404, detail="Task not found")

        return res.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/my_tasks")
def get_my_tasks(current_user: dict = Depends(get_current_user)):
    try:
        res = supabase.table("tasks").select("*").eq("user_id", current_user["id"]).execute()
        return res.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update/{task_id}")
def update_task(task_id: str, task: TaskUpdateRequest, current_user: dict = Depends(get_current_user)):
    try:
        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if not current_user["is_admin"]:
            if task.total_minutes:
                update_data["total_minutes"] = task.total_minutes
            if task.status:
                update_data["status"] = task.status
        else:
            if task.title:
                update_data["title"] = task.title
            if task.description:
                update_data["description"] = task.description
            if task.total_minutes:
                update_data["total_minutes"] = task.total_minutes
            if task.user_id:
                update_data["user_id"] = task.user_id
            if task.status:
                update_data["status"] = task.status

        res = supabase.table("tasks").update(update_data).eq("id", task_id).execute()

        if not res.data:
            raise HTTPException(status_code=500, detail="Task update failed")

        return res.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{task_id}")
def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    try:
        if not current_user["is_admin"]:
            raise HTTPException(status_code=403, detail="Not authorized. Only admins can delete tasks.")
        
        res = supabase.table("tasks").delete().eq("id", task_id).execute()

        if not res.data:
            raise HTTPException(status_code=500, detail="Task deletion failed")

        return {"detail": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/list")
def list_tasks(current_user: dict = Depends(get_current_user)):
    try:
        if not current_user["is_admin"]:
            raise HTTPException(status_code=403, detail="Not authorized. Only admins can view all tasks.")
        
        res = supabase.table("tasks").select("*").execute()
        return res.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))