import os
from openai import OpenAI
from pymongo import MongoClient
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

# --- Initialize NVIDIA NIM Client ---
nim_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY2")
)

# --- MongoDB Setup ---
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["your_db_name"]  # Replace with your DB name
requests_col = db["service_requests"]

# --- Tool Functions ---


def get_my_jobs(serviceman_username: str) -> str:
    """Fetch all pending jobs for a serviceman."""
    jobs = list(requests_col.find({
        "assigned_to": serviceman_username,
        "status": {"$ne": "Completed"}
    }))
    if not jobs:
        return "No pending jobs found."
    return "\n".join([f"Job ID: {job['_id']}, Description: {job.get('description', 'N/A')}" for job in jobs])


def complete_job(job_id: str, serviceman_username: str) -> str:
    """Mark a job as completed. Works with string IDs (e.g., 'job1')."""
    try:
        result = requests_col.update_one(
            {"_id": job_id, "assigned_to": serviceman_username},
            {"$set": {"status": "Completed"}}
        )
        if result.modified_count == 0:
            return "Error: Job not found or already completed."
        return f"Job {job_id} marked as completed."
    except Exception as e:
        return f"Error updating job: {str(e)}"


def get_job_status(job_id: str) -> str:
    """Fetch the status of a specific job by ID."""
    job = requests_col.find_one({"_id": job_id})
    if not job:
        return f"No job found with ID: {job_id}"
    return f"Job {job_id} status: {job.get('status', 'Unknown')}"


def get_my_jobs(serviceman_username: str) -> str:
    """List jobs with better formatting."""
    jobs = list(requests_col.find({
        "assigned_to": serviceman_username,
        "status": {"$ne": "Completed"}
    }))
    if not jobs:
        return "No pending jobs found."

    response = []
    for job in jobs:
        response.append(
            f"🔧 *Job ID:* `{job['_id']}`\n"
            f"📝 *Description:* {job.get('description', 'N/A')}\n"
            f"🔄 *Status:* {job['status']}\n"
        )
    return "\n".join(response)

# --- Agent Logic ---


def run_agent(user_input: str, serviceman_username: str = "ramu123") -> str:
    # Lowercase input for case-insensitive matching
    input_lower = user_input.lower()

    if "my jobs" in input_lower or "list jobs" in input_lower:
        return get_my_jobs(serviceman_username)

    elif "complete" in input_lower:
        # Extract job ID from input (e.g., "complete job 123")
        words = user_input.split()
        job_id = words[-1] if len(words) > 1 else None
        if not job_id:
            return "Please specify a Job ID (e.g., 'complete job 123')."
        return complete_job(job_id, serviceman_username)

    elif "status of job" in input_lower:
        # Extract job ID from input
        job_id = input_lower.split("status of job")[-1].strip()
        return get_job_status(job_id)

    else:
        # General questions
        response = nim_client.chat.completions.create(
            model="mistralai/mistral-7b-instruct-v0.3",
            messages=[
                {"role": "system", "content": f"You are a serviceman assistant. Current user: {serviceman_username}. Use tools when asked about jobs."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.2,
            stream=False
        )
        return response.choices[0].message.content
