"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from pymongo import MongoClient
import logging

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['mergington_school']
activities_collection = db['activities']

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initialize database with hardcoded activities
def init_database():
    """Initialize the database with default activities if collection is empty"""
    if activities_collection.count_documents({}) == 0:
        default_activities = {
            "Chess Club": {
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
            },
            "Programming Class": {
                "description": "Learn programming fundamentals and build software projects",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                "max_participants": 20,
                "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
            },
            "Gym Class": {
                "description": "Physical education and sports activities",
                "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                "max_participants": 30,
                "participants": ["john@mergington.edu", "olivia@mergington.edu"]
            },
            # Sports activities
            "Soccer Team": {
                "description": "Join the school soccer team and compete in local leagues",
                "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
                "max_participants": 18,
                "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
            },
            "Basketball Club": {
                "description": "Practice basketball skills and play friendly matches",
                "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
                "max_participants": 15,
                "participants": ["liam@mergington.edu", "ava@mergington.edu"]
            },
            # Artistic activities
            "Art Club": {
                "description": "Explore painting, drawing, and other visual arts",
                "schedule": "Mondays, 3:30 PM - 5:00 PM",
                "max_participants": 16,
                "participants": ["ella@mergington.edu", "noah@mergington.edu"]
            },
            "Drama Society": {
                "description": "Participate in acting, stage production, and theater games",
                "schedule": "Thursdays, 4:00 PM - 5:30 PM",
                "max_participants": 20,
                "participants": ["amelia@mergington.edu", "jack@mergington.edu"]
            },
            # Intellectual activities
            "Mathletes": {
                "description": "Compete in math competitions and solve challenging problems",
                "schedule": "Fridays, 2:30 PM - 3:30 PM",
                "max_participants": 10,
                "participants": ["ethan@mergington.edu", "grace@mergington.edu"]
            },
            "Science Club": {
                "description": "Conduct experiments and explore scientific concepts",
                "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
                "max_participants": 14,
                "participants": ["benjamin@mergington.edu", "chloe@mergington.edu"]
            }
        }
        
        # Insert activities with activity name as the key
        for activity_name, activity_data in default_activities.items():
            document = {
                "_id": activity_name,  # Use activity name as the document ID
                **activity_data
            }
            activities_collection.insert_one(document)
        
        print("Database initialized with default activities")

# Initialize database on startup
init_database()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    """Get all activities from the database"""
    activities = {}
    for doc in activities_collection.find():
        activity_name = doc["_id"]
        # Remove MongoDB's _id field and recreate the activities dictionary
        activity_data = {k: v for k, v in doc.items() if k != "_id"}
        activities[activity_name] = activity_data
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    activity = activities_collection.find_one({"_id": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up")
    
    # Add student to the activity
    activities_collection.update_one(
        {"_id": activity_name},
        {"$push": {"participants": email}}
    )
    return {"message": f"Signed up {email} for {activity_name}"}


@app.post("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    activity = activities_collection.find_one({"_id": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Validate student is registered
    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student not registered")
    
    # Remove student from the activity
    activities_collection.update_one(
        {"_id": activity_name},
        {"$pull": {"participants": email}}
    )
    return {"message": f"Removed {email} from {activity_name}"}
