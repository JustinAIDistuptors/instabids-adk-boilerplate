"""
Database interaction tools for agents.
"""
import os
import json
import uuid
from typing import Dict, Any, Optional, List
from supabase import create_client, Client

# Initialize Supabase client
def _get_supabase_client() -> Client:
    """
    Get the Supabase client.
    
    Returns:
        Client: The Supabase client.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    
    return create_client(url, key)

def save_bid_card(
    homeowner_id: str,
    bid_card_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Saves a bid card to the database.
    
    Args:
        homeowner_id: ID of the homeowner creating the bid card
        bid_card_data: The complete bid card data to save
        
    Returns:
        Dict[str, Any]: Response with status and result:
            - status: "success" or "error"
            - bid_card_id: ID of the saved bid card (if success)
            - error: Error message (if error)
    """
    try:
        # Get Supabase client
        supabase = _get_supabase_client()
        
        # Validate required fields
        required_fields = ["project_type", "project_scope", "timeline", "location"]
        for field in required_fields:
            if field not in bid_card_data:
                return {
                    "status": "error",
                    "error": f"Missing required field: {field}",
                    "bid_card_id": None
                }
        
        # Prepare bid card data for insertion
        bid_card_id = bid_card_data.get("id", str(uuid.uuid4()))
        
        insert_data = {
            "id": bid_card_id,
            "homeowner_id": homeowner_id,
            "project_name": bid_card_data.get("project_name", f"{bid_card_data['project_type']} Project"),
            "project_type": bid_card_data["project_type"],
            "project_scope": bid_card_data["project_scope"],
            "location": json.dumps(bid_card_data["location"]),
            "timeline": json.dumps(bid_card_data["timeline"]),
            "status": bid_card_data.get("status", "draft")
        }
        
        # Add optional fields if present
        if "budget_range" in bid_card_data:
            insert_data["budget_range"] = json.dumps(bid_card_data["budget_range"])
            
        if "photo_urls" in bid_card_data:
            insert_data["photo_urls"] = bid_card_data["photo_urls"]
            
        if "materials_preferences" in bid_card_data:
            insert_data["materials_preferences"] = json.dumps(bid_card_data["materials_preferences"])
            
        if "special_requirements" in bid_card_data:
            insert_data["special_requirements"] = bid_card_data["special_requirements"]
            
        if "accessibility_needs" in bid_card_data:
            insert_data["accessibility_needs"] = json.dumps(bid_card_data["accessibility_needs"])
            
        if "scheduling_constraints" in bid_card_data:
            insert_data["scheduling_constraints"] = json.dumps(bid_card_data["scheduling_constraints"])
            
        if "image_analysis_results" in bid_card_data:
            insert_data["image_analysis_results"] = json.dumps(bid_card_data["image_analysis_results"])
        
        # Insert into database
        result = supabase.table("instabids.bid_cards").insert(insert_data).execute()
        
        # Check for errors
        if "error" in result:
            return {
                "status": "error",
                "error": f"Database error: {result['error']}",
                "bid_card_id": None
            }
        
        # Success
        return {
            "status": "success",
            "bid_card_id": bid_card_id,
            "message": "Bid card saved successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error saving bid card: {str(e)}",
            "bid_card_id": None
        }

def get_bid_card(bid_card_id: str) -> Dict[str, Any]:
    """
    Retrieves a bid card from the database.
    
    Args:
        bid_card_id: The ID of the bid card to retrieve
        
    Returns:
        Dict[str, Any]: Response with status and result:
            - status: "success" or "error"
            - bid_card: The complete bid card data (if success)
            - error: Error message (if error)
    """
    try:
        # Get Supabase client
        supabase = _get_supabase_client()
        
        # Query the database
        result = supabase.table("instabids.bid_cards").select("*").eq("id", bid_card_id).execute()
        
        # Check for errors
        if "error" in result:
            return {
                "status": "error",
                "error": f"Database error: {result['error']}",
                "bid_card": None
            }
        
        # Check if bid card exists
        if not result.data or len(result.data) == 0:
            return {
                "status": "error",
                "error": f"Bid card not found: {bid_card_id}",
                "bid_card": None
            }
        
        # Process the bid card data
        bid_card = result.data[0]
        
        # Convert JSON strings back to objects
        for key in ["location", "timeline", "budget_range", "materials_preferences", 
                   "accessibility_needs", "scheduling_constraints", "image_analysis_results"]:
            if key in bid_card and bid_card[key] and isinstance(bid_card[key], str):
                try:
                    bid_card[key] = json.loads(bid_card[key])
                except:
                    # Keep as string if not valid JSON
                    pass
        
        # Success
        return {
            "status": "success",
            "bid_card": bid_card
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error retrieving bid card: {str(e)}",
            "bid_card": None
        }

def find_contractors(
    project_type: str,
    location: Dict[str, str],
    specialties: Optional[List[str]] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Finds contractors based on project type, location, and specialties.
    
    Args:
        project_type: Type of project (e.g., "bathroom remodel")
        location: Location details including city, state, and zip
        specialties: Optional list of required specialties
        limit: Maximum number of contractors to return
        
    Returns:
        Dict[str, Any]: Response with status and result:
            - status: "success" or "error"
            - contractors: List of matching contractors (if success)
            - error: Error message (if error)
    """
    try:
        # Get Supabase client
        supabase = _get_supabase_client()
        
        # Build the query
        query = supabase.table("instabids.contractors").select("*")
        
        # Filter by service area (simplified for this example)
        # In a real implementation, this would be more sophisticated
        # with geospatial queries or radius searches
        if "city" in location:
            query = query.like("service_areas->>city", f"%{location['city']}%")
            
        if "state" in location:
            query = query.like("service_areas->>state", f"%{location['state']}%")
            
        # Filter by services that include the project type
        query = query.like("services", f"%{project_type}%")
        
        # Filter by specialties if provided
        if specialties:
            for specialty in specialties:
                query = query.like("services", f"%{specialty}%")
        
        # Limit results
        query = query.limit(limit)
        
        # Execute query
        result = query.execute()
        
        # Check for errors
        if "error" in result:
            return {
                "status": "error",
                "error": f"Database error: {result['error']}",
                "contractors": []
            }
        
        # Return results
        return {
            "status": "success",
            "contractors": result.data,
            "count": len(result.data)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Error finding contractors: {str(e)}",
            "contractors": []
        }