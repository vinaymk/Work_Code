from fastapi import FastAPI
import uuid
import json
import os
import subprocess

app = FastAPI()
JOB_DIR = "jobs"
os.makedirs(JOB_DIR, exist_ok=True)

@app.post("/start_insert")
def start_insert(data: dict):
    job_id = str(uuid.uuid4())
    job_data = {
        "job_id": job_id,
        "status": "Pending",
        "data": data
    }

    job_file = f"{JOB_DIR}/{job_id}.json"
    with open(job_file, "w") as f:
        json.dump(job_data, f)

    # Fire off the background process
    subprocess.Popen(["python", "do_insert.py", job_id])

    return {"job_id": job_id, "status": "started"}

@app.get("/job_status/{job_id}")
def job_status(job_id: str):
    job_file = f"{JOB_DIR}/{job_id}.json"
    if not os.path.exists(job_file):
        return {"error": "Job not found"}
    with open(job_file, "r") as f:
        job_data = json.load(f)
    return {"job_id": job_id, "status": job_data["status"]}


######################################################################################################################################
############################################ Insert File #############################################################################

import sys
import json
import os
import time

JOB_DIR = "jobs"

def insert_to_db(data):
    # Simulated long-running insert logic
    print(f"Inserting to DB: {data}")
    time.sleep(5)
    print("Insert complete")

def main(job_id):
    job_file = f"{JOB_DIR}/{job_id}.json"

    with open(job_file, "r") as f:
        job_data = json.load(f)

    job_data["status"] = "Running"
    with open(job_file, "w") as f:
        json.dump(job_data, f)

    try:
        insert_to_db(job_data["data"])
        job_data["status"] = "Completed"
    except Exception as e:
        job_data["status"] = f"Failed: {str(e)}"

    with open(job_file, "w") as f:
        json.dump(job_data, f)

if __name__ == "__main__":
    job_id = sys.argv[1]
    main(job_id)
