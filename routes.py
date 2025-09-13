"""
API Routes for EcoMind system
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

router = APIRouter()

# Pydantic models for request/response
class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    preferences: Optional[List[str]] = None
    goals: Optional[List[str]] = None

class ActionCompletion(BaseModel):
    action: str
    type: str = "general"
    points: int = 10
    impact_points: int = 5

class CampaignJoin(BaseModel):
    user_info: Dict[str, Any]

class MessageRequest(BaseModel):
    type: str
    data: Dict[str, Any] = {}

# Global variable to store orchestrator reference
_orchestrator = None

def set_orchestrator(orchestrator):
    """Set the orchestrator reference"""
    global _orchestrator
    _orchestrator = orchestrator

def get_orchestrator():
    """Get the orchestrator reference"""
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    return _orchestrator

@router.get("/dashboard")
async def get_system_dashboard():
    """Get system-wide dashboard data"""
    orchestrator = get_orchestrator()
    
    try:
        status = await orchestrator.get_status()
        
        # Get additional metrics
        monitoring_data = orchestrator.shared_memory.get("EnvironmentalMonitoringAgent", {}).get("data", {})
        community_data = orchestrator.shared_memory.get("CommunityCoordinationAgent", {}).get("data", {})
        
        dashboard = {
            "system_status": status,
            "environmental_summary": {
                "average_aqi": monitoring_data.get("analysis", {}).get("average_aqi", 0),
                "active_alerts": len(monitoring_data.get("alerts", [])),
                "monitoring_locations": len(monitoring_data.get("environmental_data", []))
            },
            "community_summary": {
                "active_campaigns": len(community_data.get("active_campaigns", [])),
                "total_participants": sum(
                    len(campaign.get("current_participants", []))
                    for campaign in community_data.get("active_campaigns", [])
                )
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/environmental/current")
async def get_current_environmental_data():
    """Get current environmental monitoring data"""
    orchestrator = get_orchestrator()
    
    monitoring_data = orchestrator.shared_memory.get("EnvironmentalMonitoringAgent", {}).get("data", {})
    
    if not monitoring_data:
        raise HTTPException(status_code=404, detail="No environmental data available")
        
    return {
        "environmental_data": monitoring_data.get("environmental_data", []),
        "analysis": monitoring_data.get("analysis", {}),
        "alerts": monitoring_data.get("alerts", []),
        "timestamp": monitoring_data.get("timestamp")
    }

@router.get("/environmental/predictions")
async def get_environmental_predictions():
    """Get environmental predictions"""
    orchestrator = get_orchestrator()
    
    predictive_data = orchestrator.shared_memory.get("PredictiveActionAgent", {}).get("data", {})
    
    return {
        "predictions": predictive_data.get("predictions", []),
        "actions_taken": predictive_data.get("actions_taken", []),
        "model_status": predictive_data.get("model_status", {}),
        "timestamp": predictive_data.get("timestamp")
    }

@router.get("/community/campaigns")
async def get_active_campaigns():
    """Get active community campaigns"""
    orchestrator = get_orchestrator()
    
    try:
        response = await orchestrator.send_message_to_agent(
            "CommunityCoordinationAgent",
            {"type": "get_active_campaigns"}
        )
        
        return {"campaigns": response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/community/campaigns/{campaign_id}/join")
async def join_campaign(campaign_id: str, join_request: CampaignJoin):
    """Join a community campaign"""
    orchestrator = get_orchestrator()
    
    try:
        response = await orchestrator.send_message_to_agent(
            "CommunityCoordinationAgent",
            {
                "type": "join_campaign",
                "campaign_id": campaign_id,
                "user_info": join_request.user_info
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/community/campaigns/{campaign_id}/complete_action")
async def complete_campaign_action(campaign_id: str, action_id: str, user_id: str):
    """Complete a campaign action"""
    orchestrator = get_orchestrator()
    
    try:
        response = await orchestrator.send_message_to_agent(
            "CommunityCoordinationAgent",
            {
                "type": "complete_action",
                "campaign_id": campaign_id,
                "action_id": action_id,
                "user_id": user_id
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/coaching/users/{user_id}/dashboard")
async def get_user_dashboard(user_id: str):
    """Get personalized dashboard for a user"""
    orchestrator = get_orchestrator()
    
    try:
        # Get dashboard from coaching agent
        coach_agent = orchestrator.agents.get("PersonalSustainabilityCoach")
        if not coach_agent:
            raise HTTPException(status_code=503, detail="Coaching agent not available")
            
        dashboard = await coach_agent.get_user_dashboard(user_id)
        
        if "error" in dashboard:
            raise HTTPException(status_code=404, detail=dashboard["error"])
            
        return dashboard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/coaching/users/{user_id}/recommendations")
async def get_user_recommendations(user_id: str):
    """Get current recommendations for a user"""
    orchestrator = get_orchestrator()
    
    try:
        response = await orchestrator.send_message_to_agent(
            "PersonalSustainabilityCoach",
            {
                "type": "get_user_recommendations",
                "user_id": user_id
            }
        )
        
        return {"recommendations": response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/coaching/users/{user_id}/complete_action")
async def complete_user_action(user_id: str, action: ActionCompletion):
    """Complete a user action"""
    orchestrator = get_orchestrator()
    
    try:
        response = await orchestrator.send_message_to_agent(
            "PersonalSustainabilityCoach",
            {
                "type": "complete_action",
                "user_id": user_id,
                "action_data": action.dict()
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/coaching/users/{user_id}/profile")
async def update_user_profile(user_id: str, profile_update: UserProfileUpdate):
    """Update user profile"""
    orchestrator = get_orchestrator()
    
    try:
        response = await orchestrator.send_message_to_agent(
            "PersonalSustainabilityCoach",
            {
                "type": "update_user_profile",
                "user_id": user_id,
                "profile_updates": profile_update.dict(exclude_unset=True)
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/status")
async def get_agents_status():
    """Get detailed status of all agents"""
    orchestrator = get_orchestrator()
    
    try:
        return await orchestrator.get_status()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/{agent_name}/message")
async def send_message_to_agent(agent_name: str, message: MessageRequest):
    """Send a message to a specific agent"""
    orchestrator = get_orchestrator()
    
    try:
        response = await orchestrator.send_message_to_agent(
            agent_name,
            {
                "type": message.type,
                **message.data
            }
        )
        
        return {"response": response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/system/broadcast")
async def broadcast_message(message: MessageRequest):
    """Broadcast a message to all agents"""
    orchestrator = get_orchestrator()
    
    try:
        response = await orchestrator.broadcast_message({
            "type": message.type,
            **message.data
        })
        
        return {"responses": response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/environmental")
async def get_environmental_analytics():
    """Get environmental analytics and trends"""
    orchestrator = get_orchestrator()
    
    monitoring_data = orchestrator.shared_memory.get("EnvironmentalMonitoringAgent", {}).get("data", {})
    predictive_data = orchestrator.shared_memory.get("PredictiveActionAgent", {}).get("data", {})
    
    # Calculate trends and analytics
    environmental_data = monitoring_data.get("environmental_data", [])
    
    analytics = {
        "air_quality_trend": _calculate_aqi_trend(environmental_data),
        "pollution_hotspots": monitoring_data.get("analysis", {}).get("pollution_hotspots", []),
        "prediction_accuracy": _calculate_prediction_accuracy(predictive_data),
        "environmental_alerts_summary": _summarize_alerts(monitoring_data.get("alerts", [])),
        "timestamp": datetime.now().isoformat()
    }
    
    return analytics

@router.get("/analytics/community")
async def get_community_analytics():
    """Get community engagement analytics"""
    orchestrator = get_orchestrator()
    
    community_data = orchestrator.shared_memory.get("CommunityCoordinationAgent", {}).get("data", {})
    
    analytics = {
        "engagement_metrics": community_data.get("engagement_metrics", {}),
        "campaign_success_rates": _calculate_campaign_success_rates(community_data.get("active_campaigns", [])),
        "participation_trends": _calculate_participation_trends(community_data.get("active_campaigns", [])),
        "impact_metrics": _calculate_community_impact(community_data.get("active_campaigns", [])),
        "timestamp": datetime.now().isoformat()
    }
    
    return analytics

@router.get("/analytics/coaching")
async def get_coaching_analytics():
    """Get coaching effectiveness analytics"""
    orchestrator = get_orchestrator()
    
    try:
        response = await orchestrator.send_message_to_agent(
            "PersonalSustainabilityCoach",
            {"type": "get_coaching_stats"}
        )
        
        return {
            "coaching_stats": response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions for analytics
def _calculate_aqi_trend(environmental_data: List[Dict[str, Any]]) -> str:
    """Calculate AQI trend from environmental data"""
    if len(environmental_data) < 2:
        return "insufficient_data"
        
    aqi_values = []
    for data in environmental_data:
        if "air_quality" in data and "aqi" in data["air_quality"]:
            aqi_values.append(data["air_quality"]["aqi"])
            
    if len(aqi_values) < 2:
        return "insufficient_data"
        
    # Simple trend calculation
    recent_avg = sum(aqi_values[-3:]) / len(aqi_values[-3:])
    earlier_avg = sum(aqi_values[:-3]) / len(aqi_values[:-3]) if len(aqi_values) > 3 else recent_avg
    
    if recent_avg > earlier_avg + 5:
        return "worsening"
    elif recent_avg < earlier_avg - 5:
        return "improving"
    else:
        return "stable"

def _calculate_prediction_accuracy(predictive_data: Dict[str, Any]) -> float:
    """Calculate prediction accuracy"""
    model_status = predictive_data.get("model_status", {})
    
    if not model_status:
        return 0.0
        
    # Average accuracy across all models
    accuracies = [model.get("accuracy", 0) for model in model_status.values()]
    return sum(accuracies) / len(accuracies) if accuracies else 0.0

def _summarize_alerts(alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize environmental alerts"""
    if not alerts:
        return {"total": 0, "by_severity": {}, "by_type": {}}
        
    by_severity = {}
    by_type = {}
    
    for alert in alerts:
        severity = alert.get("severity", "unknown")
        alert_type = alert.get("type", "unknown")
        
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_type[alert_type] = by_type.get(alert_type, 0) + 1
        
    return {
        "total": len(alerts),
        "by_severity": by_severity,
        "by_type": by_type
    }

def _calculate_campaign_success_rates(campaigns: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculate campaign success rates"""
    if not campaigns:
        return {"overall": 0.0, "by_type": {}}
        
    success_rates = {}
    type_rates = {}
    
    for campaign in campaigns:
        campaign_type = campaign.get("type", "unknown")
        target = campaign.get("target_participants", 1)
        current = len(campaign.get("current_participants", []))
        
        success_rate = (current / target) * 100 if target > 0 else 0
        
        if campaign_type not in type_rates:
            type_rates[campaign_type] = []
        type_rates[campaign_type].append(success_rate)
        
    # Calculate averages
    overall_rates = []
    for rates in type_rates.values():
        overall_rates.extend(rates)
        
    overall_success = sum(overall_rates) / len(overall_rates) if overall_rates else 0
    
    type_averages = {
        campaign_type: sum(rates) / len(rates)
        for campaign_type, rates in type_rates.items()
    }
    
    return {
        "overall": overall_success,
        "by_type": type_averages
    }

def _calculate_participation_trends(campaigns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate participation trends"""
    if not campaigns:
        return {"total_participants": 0, "average_per_campaign": 0}
        
    total_participants = sum(
        len(campaign.get("current_participants", []))
        for campaign in campaigns
    )
    
    return {
        "total_participants": total_participants,
        "average_per_campaign": total_participants / len(campaigns),
        "active_campaigns": len(campaigns)
    }

def _calculate_community_impact(campaigns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate community impact metrics"""
    if not campaigns:
        return {"total_impact_score": 0, "actions_completed": 0}
        
    total_impact = sum(
        campaign.get("metrics", {}).get("impact_score", 0)
        for campaign in campaigns
    )
    
    total_actions = sum(
        campaign.get("metrics", {}).get("actions_completed", 0)
        for campaign in campaigns
    )
    
    return {
        "total_impact_score": total_impact,
        "actions_completed": total_actions,
        "average_impact_per_campaign": total_impact / len(campaigns) if campaigns else 0
    }
