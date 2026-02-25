from fastapi import APIRouter, Depends, File, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.services.supabase_client import supabase
from app.auth.dependencies import get_current_user
from fastapi import UploadFile, File
from app.services.s3_bucket import s3_client, BUCKET_NAME
from app.services.ai_services import profile_task_generator_agent, profile_skills_generator_agent, embeddings_model
from pypdf import PdfReader
from io import BytesIO


router = APIRouter(prefix="/resumes", tags=["resumes"])

class ResumeResponse(BaseModel):
    id: str
    user_id: str
    s3_key: str
    profile_skills: str
    profile_tasks: str  


@router.post("/create")
async def create_resume(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    s3_key = None
    try:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")
              
        file_bytes = await file.read()
        file_extension = file.filename.split(".")[-1].lower()
        s3_key = f"resumes/{current_user['id']}/{current_user['id']}.{file_extension}"

        response = s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=file_bytes,
            ContentType="application/pdf"
        )
        pdf_reader = PdfReader(BytesIO(file_bytes))
        resume_text = ""

        for page in pdf_reader.pages:
            resume_text += page.extract_text() or ""

        profile_skills_response = await profile_skills_generator_agent.ainvoke({
            "messages": f"Extract keywords from the resume: \n{resume_text}"
        })
        profile_tasks_response = await profile_task_generator_agent.ainvoke({
            "messages": f"Generate task based on the resume: \n{resume_text}"
        })

        sparse_response = profile_skills_response["messages"][-1].content
        semantic_response = profile_tasks_response["messages"][-1].content
        embedding = embeddings_model.embed_query(semantic_response)

        create_response = supabase.table("resumes").upsert({
            "user_id": current_user["id"],
            "s3_key": s3_key,
            "profile_skills": sparse_response,
            "profile_tasks": semantic_response,
            "embedding": embedding},
            on_conflict="user_id"
            ).execute()
        
        if not create_response.data:
            raise Exception("Failed to save resume snippet")

        return {"message": "Resume snippet uploaded successfully", "s3_key": s3_key}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/me", response_model=ResumeResponse)
async def get_resume(current_user: dict = Depends(get_current_user)):
    try:
        response = supabase.table("resumes").select("*").eq("user_id", current_user["id"]).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Resume not found")

        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.delete("/delete")
async def delete_resume(current_user: dict = Depends(get_current_user)):
    try:
        existing = supabase.table("resumes").select("*").eq("user_id", current_user["id"]).execute()

        if not existing.data:
            raise HTTPException(status_code=404, detail="Resume not found")

        s3_key = existing.data[0]["s3_key"]

        if s3_key:
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=s3_key)

        delete_response = supabase.table("resumes").delete().eq("user_id", current_user["id"]).execute()

        if not delete_response.data:
            raise Exception("Failed to delete resume record")

        return {"message": "Resume deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))