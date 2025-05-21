"""
BidCardModule implementation.

This module handles the business logic for bid cards,
including creation, validation, and management.
"""
from typing import Dict, Any, Optional, List
import uuid
import json
from datetime import datetime

from ..tools.database_tools import save_bid_card, get_bid_card

class BidCardModule:
    """
    Business logic for creating, validating, and managing bid cards.
    """
    
    def __init__(self):
        """Initialize the BidCardModule."""
        pass
    
    def validate_bid_card_data(self, bid_card_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates bid card data to ensure all required fields are present
        and constraints are met.
        
        Args:
            bid_card_data: The bid card data to validate
            
        Returns:
            Dict containing validation result:
                - valid: True if valid, False otherwise
                - errors: List of error messages if not valid
        """
        errors = []
        
        # Check required fields
        required_fields = ["project_type", "project_scope", "timeline", "location"]
        for field in required_fields:
            if field not in bid_card_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate timeline structure
        if "timeline" in bid_card_data:
            timeline = bid_card_data["timeline"]
            if not isinstance(timeline, dict):
                errors.append("Timeline must be a dictionary")
            else:
                # Check for timeline minimum requirements
                timeline_requirements = ["start_date"] if "duration_weeks" not in timeline else []
                for req in timeline_requirements:
                    if req not in timeline:
                        errors.append(f"Timeline missing required field: {req}")
        
        # Validate location structure
        if "location" in bid_card_data:
            location = bid_card_data["location"]
            if not isinstance(location, dict):
                errors.append("Location must be a dictionary")
            else:
                # Check for location minimum requirements
                location_requirements = ["city", "state"]
                for req in location_requirements:
                    if req not in location:
                        errors.append(f"Location missing required field: {req}")
        
        # Return validation result
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def create_bid_card(
        self, 
        homeowner_id: str, 
        project_type: str,
        project_scope: str,
        timeline: Dict[str, Any],
        location: Dict[str, str],
        budget_range: Optional[Dict[str, float]] = None,
        materials_preferences: Optional[Dict[str, Any]] = None,
        special_requirements: Optional[str] = None,
        accessibility_needs: Optional[Dict[str, Any]] = None,
        scheduling_constraints: Optional[Dict[str, Any]] = None,
        photo_urls: Optional[List[str]] = None,
        image_analysis_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Creates a new bid card with the provided information.
        
        Args:
            homeowner_id: ID of the homeowner creating the bid card
            project_type: Category of the project
            project_scope: Detailed description of what the project entails
            timeline: Expected timeline information
            location: Location details
            budget_range: Optional price range
            materials_preferences: Optional preferences for materials, brands, etc.
            special_requirements: Optional text describing any special requirements
            accessibility_needs: Optional accessibility requirements
            scheduling_constraints: Optional scheduling constraints
            photo_urls: Optional list of uploaded photo URLs
            image_analysis_results: Optional results from analyzing uploaded photos
            
        Returns:
            Dict containing the result of the operation:
                - status: "success" or "error"
                - bid_card_id: ID of the created bid card (if success)
                - bid_card: The complete bid card data (if success)
                - error: Error message (if error)
        """
        # Create bid card data structure
        bid_card_data = {
            "id": str(uuid.uuid4()),
            "project_type": project_type,
            "project_scope": project_scope,
            "timeline": timeline,
            "location": location,
            "status": "draft",
        }
        
        # Add optional fields if provided
        if budget_range:
            bid_card_data["budget_range"] = budget_range
            
        if materials_preferences:
            bid_card_data["materials_preferences"] = materials_preferences
            
        if special_requirements:
            bid_card_data["special_requirements"] = special_requirements
            
        if accessibility_needs:
            bid_card_data["accessibility_needs"] = accessibility_needs
            
        if scheduling_constraints:
            bid_card_data["scheduling_constraints"] = scheduling_constraints
            
        if photo_urls:
            bid_card_data["photo_urls"] = photo_urls
            
        if image_analysis_results:
            bid_card_data["image_analysis_results"] = image_analysis_results
        
        # Validate bid card data
        validation = self.validate_bid_card_data(bid_card_data)
        if not validation["valid"]:
            return {
                "status": "error",
                "error": f"Invalid bid card data: {', '.join(validation['errors'])}",
                "bid_card_id": None,
                "bid_card": None
            }
        
        # Save the bid card to the database
        result = save_bid_card(homeowner_id, bid_card_data)
        
        if result["status"] == "error":
            return {
                "status": "error",
                "error": result["error"],
                "bid_card_id": None,
                "bid_card": None
            }
        
        # Return the result
        return {
            "status": "success",
            "bid_card_id": result["bid_card_id"],
            "bid_card": bid_card_data,
            "message": "Bid card created successfully"
        }
    
    def update_bid_card(
        self,
        bid_card_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates an existing bid card with the provided changes.
        
        Args:
            bid_card_id: ID of the bid card to update
            updates: Dictionary of fields to update and their new values
            
        Returns:
            Dict containing the result of the operation:
                - status: "success" or "error"
                - bid_card: The updated bid card data (if success)
                - error: Error message (if error)
        """
        # Retrieve the existing bid card
        result = get_bid_card(bid_card_id)
        
        if result["status"] == "error":
            return {
                "status": "error",
                "error": result["error"],
                "bid_card": None
            }
        
        # Get the current bid card data
        bid_card = result["bid_card"]
        
        # Apply updates
        for key, value in updates.items():
            bid_card[key] = value
        
        # Update the modified timestamp
        bid_card["updated_at"] = datetime.now().isoformat()
        
        # Validate the updated bid card
        validation = self.validate_bid_card_data(bid_card)
        if not validation["valid"]:
            return {
                "status": "error",
                "error": f"Invalid bid card data after updates: {', '.join(validation['errors'])}",
                "bid_card": None
            }
        
        # Save the updated bid card
        result = save_bid_card(bid_card["homeowner_id"], bid_card)
        
        if result["status"] == "error":
            return {
                "status": "error",
                "error": result["error"],
                "bid_card": None
            }
        
        # Return the result
        return {
            "status": "success",
            "bid_card": bid_card,
            "message": "Bid card updated successfully"
        }