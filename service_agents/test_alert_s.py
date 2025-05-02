import os
from serviceman_agent import run_agent
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Test Data Setup ---
def setup_test_data():
    """Insert test jobs into MongoDB before running tests."""
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client["your_db_name"]
    db.service_requests.delete_many({})  # Clear existing test data
    
    # Add test jobs for "ramu123"
    db.service_requests.insert_many([
        {
            "_id": "job1",
            "assigned_to": "ramu123",
            "status": "Assigned",
            "description": "Fix leaking pipe",
            "photo_url": "http://example.com/pipe.jpg"
        },
        {
            "_id": "job2",
            "assigned_to": "ramu123",
            "status": "Pending",
            "description": "Install new lights",
            "photo_url": "http://example.com/lights.jpg"
        }
    ])

# --- Test Cases ---
def test_list_jobs():
    print("\n=== TEST 1: List Jobs ===")
    response = run_agent("List my jobs", serviceman_username="ramu123")
    print(response)
    assert "Fix leaking pipe" in response  # Verify test job appears

def test_complete_job():
    print("\n=== TEST 2: Complete Job ===")
    response = run_agent("Complete job job1", serviceman_username="ramu123")
    print(response)
    assert "marked as completed" in response

def test_general_query():
    print("\n=== TEST 3: General Question ===")
    response = run_agent("How do I fix a pipe?", serviceman_username="ramu123")
    print(response)
    assert "pipe" in response.lower()  # Verify model responds contextually

def test_error_cases():
    print("\n=== TEST 4: Edge Cases ===")
    
    # Test completing non-existent job
    print(run_agent("Complete job invalid_id", serviceman_username="ramu123"))
    
    # Test completing already completed job
    print(run_agent("Complete job job1", serviceman_username="ramu123"))  # job1 was completed in TEST 2

# --- Main Execution ---
if __name__ == "__main__":
    setup_test_data()  # Initialize test data
    test_list_jobs()
    test_complete_job()
    test_general_query()
    print("\nAll tests completed!")