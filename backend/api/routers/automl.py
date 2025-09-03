from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import json
from pathlib import Path

from ...models import Document
from ...automl.orchestrator import AutoMLOrchestrator

router = APIRouter(
    prefix="/automl",
    tags=["automl"],
    responses={404: {"description": "Not found"}},
)

# Store active AutoML jobs
active_jobs = {}

class AutoMLConfig(BaseModel):
    """Configuration for AutoML optimization"""
    train_documents: List[Document]
    test_queries: List[Dict[str, Any]]
    base_config: Optional[Dict[str, Any]] = None
    num_configs: int = 10

class AutoMLJob(BaseModel):
    """AutoML job status"""
    job_id: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    progress: float = 0.0
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/start", response_model=Dict[str, str])
async def start_automl(
    config: AutoMLConfig,
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """
    Start a new AutoML optimization job
    
    Args:
        config: Configuration for the AutoML job
        
    Returns:
        Job ID for tracking progress
    """
    job_id = str(uuid.uuid4())
    
    # Initialize job
    active_jobs[job_id] = {
        'status': 'pending',
        'progress': 0.0,
        'results': None,
        'error': None
    }
    
    # Start background task
    background_tasks.add_task(
        run_automl_job,
        job_id=job_id,
        config=config
    )
    
    return {"job_id": job_id}

@router.get("/status/{job_id}", response_model=AutoMLJob)
async def get_job_status(job_id: str) -> AutoMLJob:
    """
    Get the status of an AutoML job
    
    Args:
        job_id: ID of the job to check
        
    Returns:
        Current job status and results if available
    """
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return AutoMLJob(job_id=job_id, **active_jobs[job_id])

@router.get("/results/{job_id}")
async def get_job_results(job_id: str) -> Dict[str, Any]:
    """
    Get the results of a completed AutoML job
    
    Args:
        job_id: ID of the job
        
    Returns:
        Job results including the best configuration found
    """
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = active_jobs[job_id]
    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    return job['results']

def run_automl_job(job_id: str, config: AutoMLConfig) -> None:
    """
    Run AutoML optimization in the background
    
    Args:
        job_id: ID of the job
        config: AutoML configuration
    """
    try:
        # Update job status
        active_jobs[job_id]['status'] = 'running'
        
        # Initialize orchestrator
        orchestrator = AutoMLOrchestrator(
            output_dir=f"automl_results/{job_id}",
            max_workers=4
        )
        
        # Run optimization
        results = orchestrator.run(
            train_documents=config.train_documents,
            test_queries=config.test_queries,
            base_config=config.base_config or {},
            num_configs=config.num_configs
        )
        
        # Update job status with results
        active_jobs[job_id].update({
            'status': 'completed',
            'progress': 1.0,
            'results': results
        })
        
    except Exception as e:
        # Update job status with error
        active_jobs[job_id].update({
            'status': 'failed',
            'error': str(e)
        })
