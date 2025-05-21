"""
Bid card tools for the HomeownerAgent.
"""
import json
import uuid
from typing import Dict, Any, Optional, List

def generate_bid_card(
    project_type: str,
    project_scope: str,
    timeline: Dict[str, Any],
    budget_range: Optional[Dict[str, float]] = None,
    location: Dict[str, str] = None,
    materials_preferences: Optional[Dict[str, Any]] = None,
    special_requirements: Optional[str] = None,
    accessibility_needs: Optional[Dict[str, Any]] = None,
    scheduling_constraints: Optional[Dict[str, Any]] = None,
    photo_urls: Optional[List[str]] = None,
    image_analysis_results: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates a structured bid card based on project information.
    
    This tool creates a standardized JSON structure that contractors can use to understand
    the project requirements and provide accurate bids.
    
    Args:
        project_type: Category of the project (e.g., "bathroom remodel", "kitchen renovation")
        project_scope: Detailed description of what the project entails
        timeline: Expected timeline information, e.g., {"start_date": "2025-06-01", "duration_weeks": 3}
        budget_range: Optional price range, e.g., {"min": 5000, "max": 10000, "currency": "USD"}
        location: Location details, e.g., {"city": "Seattle", "state": "WA", "zip": "98101"}
        materials_preferences: Optional preferences for materials, brands, etc.
        special_requirements: Optional text describing any special requirements
        accessibility_needs: Optional accessibility requirements
        scheduling_constraints: Optional scheduling constraints
        photo_urls: Optional list of uploaded photo URLs
        image_analysis_results: Optional results from analyzing uploaded photos
        
    Returns:
        dict: A structured bid card with the following:
            - status: "success" if generated successfully, "error" otherwise
            - bid_card: The completed bid card data or None if there was an error
            - error_message: Error details if status is "error"
    """
    try:
        # Validate required fields
        if not project_type:
            return {
                "status": "error",
                "error_message": "Project type is required",
                "bid_card": None
            }
            
        if not project_scope:
            return {
                "status": "error",
                "error_message": "Project scope is required",
                "bid_card": None
            }
            
        if not timeline:
            return {
                "status": "error",
                "error_message": "Timeline information is required",
                "bid_card": None
            }
            
        if not location:
            return {
                "status": "error",
                "error_message": "Location information is required",
                "bid_card": None
            }
        
        # Generate bid card ID
        bid_card_id = str(uuid.uuid4())
        
        # Create the bid card structure
        bid_card = {
            "id": bid_card_id,
            "project_type": project_type,
            "project_scope": project_scope,
            "timeline": timeline,
            "location": location,
            "status": "draft",
            "created_at": "2025-05-21T12:00:00Z",  # This would be dynamically generated in production
            "updated_at": "2025-05-21T12:00:00Z",  # This would be dynamically generated in production
        }
        
        # Add optional fields if provided
        if budget_range:
            bid_card["budget_range"] = budget_range
            
        if materials_preferences:
            bid_card["materials_preferences"] = materials_preferences
            
        if special_requirements:
            bid_card["special_requirements"] = special_requirements
            
        if accessibility_needs:
            bid_card["accessibility_needs"] = accessibility_needs
            
        if scheduling_constraints:
            bid_card["scheduling_constraints"] = scheduling_constraints
            
        if photo_urls:
            bid_card["photo_urls"] = photo_urls
            
        if image_analysis_results:
            bid_card["image_analysis_results"] = image_analysis_results
        
        return {
            "status": "success",
            "bid_card": bid_card,
            "message": "Bid card generated successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error generating bid card: {str(e)}",
            "bid_card": None
        }