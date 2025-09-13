"""
Community Coordination Agent - Orchestrates collective environmental actions
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
import os
from openai import AsyncOpenAI

from core.base_agent import BaseAgent

class CommunityCoordinationAgent(BaseAgent):
    """Agent that coordinates community-wide environmental actions"""
    
    def __init__(self):
        super().__init__("CommunityCoordinationAgent", cycle_interval=900)  # 15 minutes
        self.openai_client = None
        self.action_radius = float(os.getenv("COMMUNITY_ACTION_RADIUS", "10"))  # km
        self.active_campaigns = []
        self.community_members = []
        self.coordination_history = []
        
    async def _setup(self):
        """Initialize community coordination systems"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "demo_key":
            self.openai_client = AsyncOpenAI(api_key=api_key)
            
        # Initialize mock community data
        self.community_members = [
            {"id": "user_001", "name": "Alice Johnson", "location": "City Center", "engagement_score": 85},
            {"id": "user_002", "name": "Bob Smith", "location": "Industrial Zone", "engagement_score": 72},
            {"id": "user_003", "name": "Carol Davis", "location": "Residential Area", "engagement_score": 91},
            {"id": "org_001", "name": "Green City Initiative", "type": "organization", "reach": 500},
            {"id": "org_002", "name": "Local Environmental Group", "type": "organization", "reach": 200}
        ]
        
        self._store_memory("campaigns_created", 0)
        self._store_memory("participants_coordinated", 0)
        
    async def _cleanup(self):
        """Cleanup resources"""
        pass
        
    async def execute_cycle(self, shared_memory: Dict[str, Any]) -> Dict[str, Any]:
        """Execute autonomous community coordination cycle"""
        try:
            # Get environmental data and predictions
            monitoring_data = shared_memory.get("EnvironmentalMonitoringAgent", {}).get("data", {})
            predictive_data = shared_memory.get("PredictiveActionAgent", {}).get("data", {})
            
            # Assess community coordination needs
            coordination_needs = await self._assess_coordination_needs(monitoring_data, predictive_data)
            
            # Create or update campaigns
            campaigns = await self._manage_campaigns(coordination_needs)
            
            # Coordinate community actions
            coordinated_actions = await self._coordinate_actions(campaigns)
            
            # Update engagement metrics
            engagement_metrics = await self._update_engagement_metrics()
            
            self._record_action("coordination_cycle", {
                "coordination_needs": len(coordination_needs),
                "active_campaigns": len(self.active_campaigns),
                "actions_coordinated": len(coordinated_actions),
                "community_members": len(self.community_members)
            })
            
            return {
                "coordination_needs": coordination_needs,
                "active_campaigns": self.active_campaigns,
                "coordinated_actions": coordinated_actions,
                "engagement_metrics": engagement_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in coordination cycle: {e}")
            return {"error": str(e)}
            
    async def _assess_coordination_needs(self, monitoring_data: Dict[str, Any], predictive_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess what community coordination is needed"""
        needs = []
        
        # Check monitoring alerts
        alerts = monitoring_data.get("alerts", [])
        for alert in alerts:
            if alert.get("action_required"):
                needs.append({
                    "type": "alert_response",
                    "priority": "high" if alert.get("severity") == "high" else "medium",
                    "location": alert.get("location", "general"),
                    "description": f"Community response needed for {alert.get('type')} alert",
                    "source": "monitoring_agent",
                    "data": alert
                })
                
        # Check predictions
        predictions = predictive_data.get("predictions", [])
        for prediction in predictions:
            if prediction.get("confidence", 0) > 0.7:
                needs.append({
                    "type": "preventive_action",
                    "priority": "medium",
                    "location": "general",
                    "description": f"Preventive community action for predicted {prediction.get('type')}",
                    "source": "predictive_agent",
                    "data": prediction
                })
                
        # Check for ongoing environmental issues
        analysis = monitoring_data.get("analysis", {})
        if analysis.get("average_aqi", 0) > 100:
            needs.append({
                "type": "air_quality_improvement",
                "priority": "high",
                "location": "general",
                "description": "Community action needed to improve air quality",
                "source": "analysis",
                "data": analysis
            })
            
        return needs
        
    async def _manage_campaigns(self, coordination_needs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create and manage community campaigns"""
        new_campaigns = []
        
        for need in coordination_needs:
            # Check if campaign already exists for this need
            existing_campaign = self._find_existing_campaign(need)
            
            if existing_campaign:
                # Update existing campaign
                await self._update_campaign(existing_campaign, need)
            else:
                # Create new campaign
                campaign = await self._create_campaign(need)
                if campaign:
                    self.active_campaigns.append(campaign)
                    new_campaigns.append(campaign)
                    
        # Clean up completed campaigns
        self._cleanup_completed_campaigns()
        
        return new_campaigns
        
    def _find_existing_campaign(self, need: Dict[str, Any]) -> Dict[str, Any]:
        """Find existing campaign for a coordination need"""
        for campaign in self.active_campaigns:
            if (campaign.get("type") == need.get("type") and 
                campaign.get("location") == need.get("location") and
                campaign.get("status") == "active"):
                return campaign
        return None
        
    async def _create_campaign(self, need: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new community campaign"""
        campaign_id = f"campaign_{len(self.active_campaigns) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        campaign = {
            "id": campaign_id,
            "type": need.get("type"),
            "priority": need.get("priority"),
            "location": need.get("location"),
            "title": await self._generate_campaign_title(need),
            "description": need.get("description"),
            "actions": await self._generate_campaign_actions(need),
            "target_participants": await self._calculate_target_participants(need),
            "current_participants": [],
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
            "metrics": {
                "participants_joined": 0,
                "actions_completed": 0,
                "impact_score": 0
            }
        }
        
        # Update campaigns count
        current_count = self._get_memory("campaigns_created") or 0
        self._store_memory("campaigns_created", current_count + 1)
        
        return campaign
        
    async def _generate_campaign_title(self, need: Dict[str, Any]) -> str:
        """Generate an engaging campaign title"""
        need_type = need.get("type", "environmental_action")
        location = need.get("location", "community")
        
        titles = {
            "alert_response": f"Emergency Response: {location} Environmental Alert",
            "preventive_action": f"Prevent Environmental Issues in {location}",
            "air_quality_improvement": f"Clear Air Initiative for {location}",
            "pollution_reduction": f"Pollution Prevention Campaign - {location}",
            "default": f"Environmental Action Needed in {location}"
        }
        
        return titles.get(need_type, titles["default"])
        
    async def _generate_campaign_actions(self, need: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific actions for a campaign"""
        need_type = need.get("type")
        priority = need.get("priority", "medium")
        
        base_actions = []
        
        if need_type == "alert_response":
            base_actions = [
                {"action": "report_environmental_conditions", "points": 10, "difficulty": "easy"},
                {"action": "share_safety_information", "points": 15, "difficulty": "easy"},
                {"action": "organize_local_cleanup", "points": 50, "difficulty": "hard"},
                {"action": "contact_local_authorities", "points": 25, "difficulty": "medium"}
            ]
        elif need_type == "air_quality_improvement":
            base_actions = [
                {"action": "use_public_transportation", "points": 20, "difficulty": "easy"},
                {"action": "plant_air_purifying_plants", "points": 30, "difficulty": "medium"},
                {"action": "organize_car_free_day", "points": 100, "difficulty": "hard"},
                {"action": "install_air_quality_monitor", "points": 40, "difficulty": "medium"}
            ]
        else:
            base_actions = [
                {"action": "environmental_monitoring", "points": 15, "difficulty": "easy"},
                {"action": "community_education", "points": 25, "difficulty": "medium"},
                {"action": "organize_group_action", "points": 75, "difficulty": "hard"}
            ]
            
        # Add metadata to actions
        for action in base_actions:
            action.update({
                "id": f"action_{len(base_actions)}_{datetime.now().strftime('%H%M%S')}",
                "participants": [],
                "completed_count": 0,
                "impact_estimate": action["points"] * 2
            })
            
        return base_actions
        
    async def _calculate_target_participants(self, need: Dict[str, Any]) -> int:
        """Calculate target number of participants for a campaign"""
        priority = need.get("priority", "medium")
        location = need.get("location", "general")
        
        base_target = 10
        
        if priority == "high":
            base_target *= 3
        elif priority == "medium":
            base_target *= 2
            
        # Adjust based on location
        if location != "general":
            # Specific location campaigns need fewer participants
            base_target = max(5, base_target // 2)
            
        return min(base_target, len(self.community_members))
        
    async def _update_campaign(self, campaign: Dict[str, Any], need: Dict[str, Any]):
        """Update existing campaign with new information"""
        # Update priority if higher
        if need.get("priority") == "high" and campaign.get("priority") != "high":
            campaign["priority"] = "high"
            campaign["target_participants"] = min(
                campaign["target_participants"] * 2, 
                len(self.community_members)
            )
            
        # Extend deadline if needed
        current_deadline = datetime.fromisoformat(campaign["deadline"])
        if current_deadline < datetime.now() + timedelta(days=3):
            campaign["deadline"] = (datetime.now() + timedelta(days=7)).isoformat()
            
    def _cleanup_completed_campaigns(self):
        """Remove completed or expired campaigns"""
        current_time = datetime.now()
        
        self.active_campaigns = [
            campaign for campaign in self.active_campaigns
            if (campaign.get("status") == "active" and 
                datetime.fromisoformat(campaign["deadline"]) > current_time)
        ]
        
    async def _coordinate_actions(self, campaigns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Coordinate community actions for campaigns"""
        coordinated_actions = []
        
        for campaign in self.active_campaigns:
            # Recruit participants
            new_participants = await self._recruit_participants(campaign)
            
            # Assign actions to participants
            action_assignments = await self._assign_actions(campaign, new_participants)
            
            # Track progress
            progress = await self._track_campaign_progress(campaign)
            
            if new_participants or action_assignments:
                coordinated_actions.append({
                    "campaign_id": campaign["id"],
                    "new_participants": len(new_participants),
                    "action_assignments": len(action_assignments),
                    "progress": progress,
                    "timestamp": datetime.now().isoformat()
                })
                
        return coordinated_actions
        
    async def _recruit_participants(self, campaign: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recruit participants for a campaign"""
        new_participants = []
        target = campaign.get("target_participants", 10)
        current = len(campaign.get("current_participants", []))
        
        if current >= target:
            return new_participants
            
        # Find suitable community members
        suitable_members = await self._find_suitable_participants(campaign)
        
        # Recruit based on engagement and location
        needed = min(target - current, len(suitable_members))
        
        for i in range(needed):
            if i < len(suitable_members):
                member = suitable_members[i]
                
                # Simulate recruitment success based on engagement
                engagement = member.get("engagement_score", 50)
                recruitment_probability = min(0.9, engagement / 100)
                
                # Simulate recruitment (replace with actual notification system)
                if self._simulate_recruitment_success(recruitment_probability):
                    participant = {
                        "user_id": member["id"],
                        "name": member["name"],
                        "joined_at": datetime.now().isoformat(),
                        "assigned_actions": [],
                        "completed_actions": []
                    }
                    
                    campaign["current_participants"].append(participant)
                    new_participants.append(participant)
                    
        # Update participants count
        current_count = self._get_memory("participants_coordinated") or 0
        self._store_memory("participants_coordinated", current_count + len(new_participants))
        
        return new_participants
        
    async def _find_suitable_participants(self, campaign: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find community members suitable for a campaign"""
        suitable = []
        campaign_location = campaign.get("location", "general")
        
        for member in self.community_members:
            # Check if already participating
            current_participants = campaign.get("current_participants", [])
            if any(p.get("user_id") == member["id"] for p in current_participants):
                continue
                
            # Check location match
            if campaign_location != "general":
                if member.get("location") != campaign_location:
                    continue
                    
            # Check engagement level
            if member.get("engagement_score", 0) > 30:  # Minimum engagement threshold
                suitable.append(member)
                
        # Sort by engagement score
        suitable.sort(key=lambda x: x.get("engagement_score", 0), reverse=True)
        
        return suitable
        
    def _simulate_recruitment_success(self, probability: float) -> bool:
        """Simulate recruitment success"""
        import random
        return random.random() < probability
        
    async def _assign_actions(self, campaign: Dict[str, Any], participants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assign actions to campaign participants"""
        assignments = []
        
        for participant in participants:
            # Find suitable actions for this participant
            suitable_actions = await self._find_suitable_actions(campaign, participant)
            
            if suitable_actions:
                # Assign 1-2 actions per participant
                num_actions = min(2, len(suitable_actions))
                assigned_actions = suitable_actions[:num_actions]
                
                for action in assigned_actions:
                    assignment = {
                        "participant_id": participant["user_id"],
                        "action_id": action["id"],
                        "action_name": action["action"],
                        "assigned_at": datetime.now().isoformat(),
                        "deadline": (datetime.now() + timedelta(days=3)).isoformat(),
                        "status": "assigned"
                    }
                    
                    assignments.append(assignment)
                    participant["assigned_actions"].append(assignment)
                    
        return assignments
        
    async def _find_suitable_actions(self, campaign: Dict[str, Any], participant: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find actions suitable for a participant"""
        actions = campaign.get("actions", [])
        suitable = []
        
        for action in actions:
            # Check if action is not over-assigned
            max_participants = 5  # Max participants per action
            current_participants = len(action.get("participants", []))
            
            if current_participants < max_participants:
                suitable.append(action)
                
        return suitable
        
    async def _track_campaign_progress(self, campaign: Dict[str, Any]) -> Dict[str, Any]:
        """Track progress of a campaign"""
        participants = campaign.get("current_participants", [])
        actions = campaign.get("actions", [])
        
        # Calculate completion rates
        total_assignments = sum(len(p.get("assigned_actions", [])) for p in participants)
        total_completions = sum(len(p.get("completed_actions", [])) for p in participants)
        
        completion_rate = (total_completions / total_assignments * 100) if total_assignments > 0 else 0
        
        # Calculate impact score
        impact_score = sum(
            action.get("impact_estimate", 0) * action.get("completed_count", 0)
            for action in actions
        )
        
        progress = {
            "participants": len(participants),
            "target_participants": campaign.get("target_participants", 0),
            "participation_rate": len(participants) / campaign.get("target_participants", 1) * 100,
            "completion_rate": completion_rate,
            "impact_score": impact_score,
            "actions_available": len(actions),
            "total_assignments": total_assignments,
            "total_completions": total_completions
        }
        
        # Update campaign metrics
        campaign["metrics"].update({
            "participants_joined": len(participants),
            "actions_completed": total_completions,
            "impact_score": impact_score
        })
        
        return progress
        
    async def _update_engagement_metrics(self) -> Dict[str, Any]:
        """Update community engagement metrics"""
        total_members = len(self.community_members)
        active_participants = set()
        
        # Count active participants across all campaigns
        for campaign in self.active_campaigns:
            for participant in campaign.get("current_participants", []):
                active_participants.add(participant["user_id"])
                
        engagement_rate = len(active_participants) / total_members * 100 if total_members > 0 else 0
        
        metrics = {
            "total_community_members": total_members,
            "active_participants": len(active_participants),
            "engagement_rate": engagement_rate,
            "active_campaigns": len(self.active_campaigns),
            "total_campaigns_created": self._get_memory("campaigns_created") or 0,
            "total_participants_coordinated": self._get_memory("participants_coordinated") or 0
        }
        
        return metrics
        
    async def _process_message(self, message: Dict[str, Any]) -> Any:
        """Process messages from other agents"""
        message_type = message.get("type")
        
        if message_type == "get_active_campaigns":
            return self.active_campaigns
            
        elif message_type == "join_campaign":
            campaign_id = message.get("campaign_id")
            user_info = message.get("user_info")
            return await self._handle_campaign_join(campaign_id, user_info)
            
        elif message_type == "complete_action":
            campaign_id = message.get("campaign_id")
            action_id = message.get("action_id")
            user_id = message.get("user_id")
            return await self._handle_action_completion(campaign_id, action_id, user_id)
            
        elif message_type == "get_community_stats":
            return await self._update_engagement_metrics()
            
        return {"status": "unknown_message_type"}
        
    async def _handle_campaign_join(self, campaign_id: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user joining a campaign"""
        campaign = next((c for c in self.active_campaigns if c["id"] == campaign_id), None)
        
        if not campaign:
            return {"status": "error", "message": "Campaign not found"}
            
        # Check if user already participating
        current_participants = campaign.get("current_participants", [])
        if any(p.get("user_id") == user_info.get("id") for p in current_participants):
            return {"status": "error", "message": "User already participating"}
            
        # Add participant
        participant = {
            "user_id": user_info["id"],
            "name": user_info.get("name", "Anonymous"),
            "joined_at": datetime.now().isoformat(),
            "assigned_actions": [],
            "completed_actions": []
        }
        
        campaign["current_participants"].append(participant)
        
        return {"status": "success", "message": "Successfully joined campaign"}
        
    async def _handle_action_completion(self, campaign_id: str, action_id: str, user_id: str) -> Dict[str, Any]:
        """Handle action completion by user"""
        campaign = next((c for c in self.active_campaigns if c["id"] == campaign_id), None)
        
        if not campaign:
            return {"status": "error", "message": "Campaign not found"}
            
        # Find participant
        participant = next(
            (p for p in campaign.get("current_participants", []) if p.get("user_id") == user_id),
            None
        )
        
        if not participant:
            return {"status": "error", "message": "Participant not found"}
            
        # Find action
        action = next((a for a in campaign.get("actions", []) if a["id"] == action_id), None)
        
        if not action:
            return {"status": "error", "message": "Action not found"}
            
        # Mark action as completed
        completion = {
            "action_id": action_id,
            "completed_at": datetime.now().isoformat(),
            "points_earned": action.get("points", 0)
        }
        
        participant["completed_actions"].append(completion)
        action["completed_count"] = action.get("completed_count", 0) + 1
        
        return {"status": "success", "points_earned": action.get("points", 0)}
        
    async def coordinate_pollution_response(self, pollution_data: Dict[str, Any]):
        """Coordinate community response to pollution alert"""
        self.logger.info(f"Coordinating pollution response: {pollution_data}")
        
        # Create emergency campaign
        emergency_need = {
            "type": "pollution_emergency",
            "priority": "high",
            "location": pollution_data.get("location", "general"),
            "description": "Emergency community response to pollution event",
            "source": "pollution_alert",
            "data": pollution_data
        }
        
        campaign = await self._create_campaign(emergency_need)
        
        if campaign:
            self.active_campaigns.append(campaign)
            
            # Immediately recruit high-engagement participants
            emergency_participants = await self._recruit_emergency_participants(campaign)
            
            self._record_action("pollution_response_coordination", {
                "campaign_created": True,
                "emergency_participants": len(emergency_participants),
                "location": pollution_data.get("location")
            })
            
            return {
                "campaign": campaign,
                "participants": emergency_participants,
                "status": "coordinated"
            }
            
        return {"status": "failed_to_coordinate"}
        
    async def _recruit_emergency_participants(self, campaign: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recruit participants for emergency campaigns"""
        # Target high-engagement members first
        high_engagement_members = [
            member for member in self.community_members
            if member.get("engagement_score", 0) > 70
        ]
        
        participants = []
        for member in high_engagement_members[:10]:  # Recruit up to 10 emergency participants
            participant = {
                "user_id": member["id"],
                "name": member["name"],
                "joined_at": datetime.now().isoformat(),
                "assigned_actions": [],
                "completed_actions": [],
                "emergency_participant": True
            }
            
            campaign["current_participants"].append(participant)
            participants.append(participant)
            
        return participants
