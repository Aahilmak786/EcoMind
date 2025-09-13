"""
Personal Sustainability Coach Agent - Provides personalized environmental recommendations
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json
import os
from openai import AsyncOpenAI

from core.base_agent import BaseAgent

class PersonalSustainabilityCoach(BaseAgent):
    """Agent that provides personalized sustainability coaching and recommendations"""
    
    def __init__(self):
        super().__init__("PersonalSustainabilityCoach", cycle_interval=1800)  # 30 minutes
        self.openai_client = None
        self.user_profiles = {}
        self.coaching_sessions = []
        self.sustainability_challenges = []
        
    async def _setup(self):
        """Initialize coaching systems"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "demo_key":
            self.openai_client = AsyncOpenAI(api_key=api_key)
            
        # Initialize mock user profiles
        self.user_profiles = {
            "user_001": {
                "name": "Alice Johnson",
                "location": "City Center",
                "preferences": ["air_quality", "energy_saving"],
                "current_score": 75,
                "goals": ["reduce_carbon_footprint", "improve_air_quality"],
                "activity_history": [],
                "coaching_level": "intermediate"
            },
            "user_002": {
                "name": "Bob Smith", 
                "location": "Industrial Zone",
                "preferences": ["pollution_reduction", "community_action"],
                "current_score": 60,
                "goals": ["community_engagement", "pollution_awareness"],
                "activity_history": [],
                "coaching_level": "beginner"
            }
        }
        
        # Initialize sustainability challenges
        self.sustainability_challenges = [
            {
                "id": "challenge_001",
                "title": "7-Day Air Quality Improvement",
                "description": "Take daily actions to improve local air quality",
                "duration_days": 7,
                "difficulty": "easy",
                "points": 100,
                "actions": ["use_public_transport", "plant_indoor_plants", "report_air_quality"]
            },
            {
                "id": "challenge_002", 
                "title": "Community Environmental Hero",
                "description": "Coordinate with neighbors for environmental action",
                "duration_days": 14,
                "difficulty": "medium",
                "points": 250,
                "actions": ["organize_cleanup", "educate_neighbors", "start_green_initiative"]
            }
        ]
        
        self._store_memory("coaching_sessions_conducted", 0)
        self._store_memory("recommendations_generated", 0)
        
    async def _cleanup(self):
        """Cleanup resources"""
        pass
        
    async def execute_cycle(self, shared_memory: Dict[str, Any]) -> Dict[str, Any]:
        """Execute autonomous coaching cycle"""
        try:
            # Get environmental context
            monitoring_data = shared_memory.get("EnvironmentalMonitoringAgent", {}).get("data", {})
            community_data = shared_memory.get("CommunityCoordinationAgent", {}).get("data", {})
            
            # Generate personalized recommendations
            recommendations = await self._generate_personalized_recommendations(monitoring_data, community_data)
            
            # Update user progress
            progress_updates = await self._update_user_progress()
            
            # Create adaptive challenges
            new_challenges = await self._create_adaptive_challenges(monitoring_data)
            
            # Conduct coaching sessions
            coaching_sessions = await self._conduct_coaching_sessions(recommendations)
            
            self._record_action("coaching_cycle", {
                "recommendations_generated": len(recommendations),
                "users_coached": len(coaching_sessions),
                "challenges_created": len(new_challenges),
                "active_users": len(self.user_profiles)
            })
            
            return {
                "recommendations": recommendations,
                "progress_updates": progress_updates,
                "new_challenges": new_challenges,
                "coaching_sessions": coaching_sessions,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in coaching cycle: {e}")
            return {"error": str(e)}
            
    async def _generate_personalized_recommendations(self, monitoring_data: Dict[str, Any], community_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized sustainability recommendations for users"""
        recommendations = []
        
        for user_id, profile in self.user_profiles.items():
            user_recommendations = await self._generate_user_recommendations(
                user_id, profile, monitoring_data, community_data
            )
            recommendations.extend(user_recommendations)
            
        # Update recommendations count
        current_count = self._get_memory("recommendations_generated") or 0
        self._store_memory("recommendations_generated", current_count + len(recommendations))
        
        return recommendations
        
    async def _generate_user_recommendations(self, user_id: str, profile: Dict[str, Any], 
                                           monitoring_data: Dict[str, Any], community_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for a specific user"""
        recommendations = []
        user_location = profile.get("location", "general")
        preferences = profile.get("preferences", [])
        coaching_level = profile.get("coaching_level", "beginner")
        
        # Environmental context-based recommendations
        environmental_data = monitoring_data.get("environmental_data", [])
        location_data = next(
            (data for data in environmental_data if data.get("location") == user_location),
            None
        )
        
        if location_data:
            # Air quality recommendations
            if "air_quality" in preferences:
                aqi = location_data.get("air_quality", {}).get("aqi", 50)
                air_rec = await self._generate_air_quality_recommendation(user_id, aqi, coaching_level)
                if air_rec:
                    recommendations.append(air_rec)
                    
            # Weather-based recommendations
            weather = location_data.get("weather", {})
            weather_rec = await self._generate_weather_based_recommendation(user_id, weather, coaching_level)
            if weather_rec:
                recommendations.append(weather_rec)
                
        # Community action recommendations
        if "community_action" in preferences:
            active_campaigns = community_data.get("active_campaigns", [])
            community_rec = await self._generate_community_recommendation(user_id, active_campaigns, coaching_level)
            if community_rec:
                recommendations.append(community_rec)
                
        # Personalized goal recommendations
        goals = profile.get("goals", [])
        for goal in goals:
            goal_rec = await self._generate_goal_recommendation(user_id, goal, profile, coaching_level)
            if goal_rec:
                recommendations.append(goal_rec)
                
        return recommendations
        
    async def _generate_air_quality_recommendation(self, user_id: str, aqi: float, coaching_level: str) -> Dict[str, Any]:
        """Generate air quality-based recommendation"""
        if aqi <= 50:
            action = "enjoy_outdoor_activities"
            message = "Great air quality today! Perfect time for outdoor exercise or activities."
            priority = "low"
        elif aqi <= 100:
            action = "moderate_outdoor_activity"
            message = "Moderate air quality. Consider indoor plants to improve your home's air."
            priority = "medium"
        else:
            action = "limit_outdoor_exposure"
            message = "Poor air quality detected. Stay indoors and use air purifiers if available."
            priority = "high"
            
        difficulty = "easy" if coaching_level == "beginner" else "medium"
        
        return {
            "id": f"air_rec_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user_id": user_id,
            "type": "air_quality",
            "action": action,
            "message": message,
            "priority": priority,
            "difficulty": difficulty,
            "points": 15 if priority == "high" else 10,
            "context": {"current_aqi": aqi},
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=6)).isoformat()
        }
        
    async def _generate_weather_based_recommendation(self, user_id: str, weather: Dict[str, Any], coaching_level: str) -> Dict[str, Any]:
        """Generate weather-based sustainability recommendation"""
        temp = weather.get("temperature", 20)
        humidity = weather.get("humidity", 50)
        
        if temp > 30:
            action = "energy_saving_cooling"
            message = "Hot weather ahead! Use fans instead of AC when possible to save energy."
        elif temp < 10:
            action = "energy_efficient_heating"
            message = "Cold weather! Layer clothing and use efficient heating to reduce energy consumption."
        elif humidity > 80:
            action = "natural_dehumidifying"
            message = "High humidity! Open windows for natural ventilation instead of using dehumidifiers."
        else:
            action = "optimal_natural_ventilation"
            message = "Perfect weather for natural ventilation! Open windows to reduce energy usage."
            
        return {
            "id": f"weather_rec_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user_id": user_id,
            "type": "weather_based",
            "action": action,
            "message": message,
            "priority": "medium",
            "difficulty": "easy",
            "points": 12,
            "context": weather,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=12)).isoformat()
        }
        
    async def _generate_community_recommendation(self, user_id: str, active_campaigns: List[Dict[str, Any]], coaching_level: str) -> Dict[str, Any]:
        """Generate community action recommendation"""
        if not active_campaigns:
            return None
            
        # Find suitable campaign for user
        suitable_campaign = None
        for campaign in active_campaigns:
            if len(campaign.get("current_participants", [])) < campaign.get("target_participants", 10):
                suitable_campaign = campaign
                break
                
        if not suitable_campaign:
            return None
            
        difficulty = "medium" if coaching_level in ["intermediate", "advanced"] else "easy"
        
        return {
            "id": f"community_rec_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user_id": user_id,
            "type": "community_action",
            "action": "join_campaign",
            "message": f"Join the '{suitable_campaign['title']}' campaign to make a community impact!",
            "priority": suitable_campaign.get("priority", "medium"),
            "difficulty": difficulty,
            "points": 25,
            "context": {
                "campaign_id": suitable_campaign["id"],
                "campaign_title": suitable_campaign["title"]
            },
            "created_at": datetime.now().isoformat(),
            "expires_at": suitable_campaign.get("deadline")
        }
        
    async def _generate_goal_recommendation(self, user_id: str, goal: str, profile: Dict[str, Any], coaching_level: str) -> Dict[str, Any]:
        """Generate goal-specific recommendation"""
        goal_actions = {
            "reduce_carbon_footprint": {
                "action": "track_carbon_usage",
                "message": "Track your daily carbon footprint and find one area to improve today.",
                "points": 20
            },
            "improve_air_quality": {
                "action": "air_quality_action",
                "message": "Take one action today to improve air quality in your area.",
                "points": 18
            },
            "community_engagement": {
                "action": "engage_community",
                "message": "Connect with one neighbor about environmental issues today.",
                "points": 22
            },
            "pollution_awareness": {
                "action": "learn_pollution_sources",
                "message": "Learn about pollution sources in your area and share with others.",
                "points": 15
            }
        }
        
        goal_info = goal_actions.get(goal)
        if not goal_info:
            return None
            
        return {
            "id": f"goal_rec_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user_id": user_id,
            "type": "goal_based",
            "action": goal_info["action"],
            "message": goal_info["message"],
            "priority": "medium",
            "difficulty": coaching_level,
            "points": goal_info["points"],
            "context": {"goal": goal},
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=1)).isoformat()
        }
        
    async def _update_user_progress(self) -> List[Dict[str, Any]]:
        """Update progress for all users"""
        progress_updates = []
        
        for user_id, profile in self.user_profiles.items():
            # Calculate progress based on recent activities
            recent_activities = self._get_recent_activities(user_id)
            
            # Update sustainability score
            old_score = profile.get("current_score", 50)
            new_score = await self._calculate_sustainability_score(user_id, recent_activities)
            
            if new_score != old_score:
                profile["current_score"] = new_score
                
                progress_update = {
                    "user_id": user_id,
                    "old_score": old_score,
                    "new_score": new_score,
                    "change": new_score - old_score,
                    "recent_activities": len(recent_activities),
                    "updated_at": datetime.now().isoformat()
                }
                
                progress_updates.append(progress_update)
                
                # Level up coaching if score improved significantly
                if new_score - old_score > 10:
                    await self._check_coaching_level_up(user_id, profile)
                    
        return progress_updates
        
    def _get_recent_activities(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recent activities for a user"""
        profile = self.user_profiles.get(user_id, {})
        activities = profile.get("activity_history", [])
        
        # Return activities from last 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        recent_activities = [
            activity for activity in activities
            if datetime.fromisoformat(activity.get("timestamp", "2020-01-01")) > cutoff_date
        ]
        
        return recent_activities
        
    async def _calculate_sustainability_score(self, user_id: str, recent_activities: List[Dict[str, Any]]) -> int:
        """Calculate sustainability score based on activities"""
        base_score = 50
        activity_bonus = len(recent_activities) * 5  # 5 points per activity
        
        # Bonus for different types of activities
        activity_types = set(activity.get("type") for activity in recent_activities)
        diversity_bonus = len(activity_types) * 3
        
        # Bonus for high-impact activities
        impact_bonus = sum(
            activity.get("impact_points", 0) for activity in recent_activities
        )
        
        total_score = min(100, base_score + activity_bonus + diversity_bonus + impact_bonus)
        return total_score
        
    async def _check_coaching_level_up(self, user_id: str, profile: Dict[str, Any]):
        """Check if user should level up in coaching"""
        current_level = profile.get("coaching_level", "beginner")
        current_score = profile.get("current_score", 50)
        
        if current_level == "beginner" and current_score > 70:
            profile["coaching_level"] = "intermediate"
            self.logger.info(f"User {user_id} leveled up to intermediate coaching")
        elif current_level == "intermediate" and current_score > 85:
            profile["coaching_level"] = "advanced"
            self.logger.info(f"User {user_id} leveled up to advanced coaching")
            
    async def _create_adaptive_challenges(self, monitoring_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create challenges that adapt to current environmental conditions"""
        new_challenges = []
        
        # Check environmental conditions
        analysis = monitoring_data.get("analysis", {})
        alerts = monitoring_data.get("alerts", [])
        
        # Create challenge based on air quality
        avg_aqi = analysis.get("average_aqi", 50)
        if avg_aqi > 100:
            air_challenge = {
                "id": f"air_emergency_challenge_{datetime.now().strftime('%Y%m%d')}",
                "title": "Air Quality Emergency Response",
                "description": "Help improve air quality during this pollution event",
                "duration_days": 3,
                "difficulty": "medium",
                "points": 150,
                "actions": ["stay_indoors", "use_air_purifier", "report_pollution_sources", "share_air_quality_info"],
                "adaptive": True,
                "trigger": "high_aqi",
                "created_at": datetime.now().isoformat()
            }
            new_challenges.append(air_challenge)
            
        # Create challenge based on alerts
        if alerts:
            alert_challenge = {
                "id": f"alert_response_challenge_{datetime.now().strftime('%Y%m%d')}",
                "title": "Environmental Alert Response",
                "description": "Respond to current environmental alerts in your area",
                "duration_days": 5,
                "difficulty": "easy",
                "points": 100,
                "actions": ["follow_safety_guidelines", "help_neighbors", "report_conditions"],
                "adaptive": True,
                "trigger": "environmental_alerts",
                "created_at": datetime.now().isoformat()
            }
            new_challenges.append(alert_challenge)
            
        # Add new challenges to the list
        self.sustainability_challenges.extend(new_challenges)
        
        return new_challenges
        
    async def _conduct_coaching_sessions(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Conduct personalized coaching sessions"""
        sessions = []
        
        # Group recommendations by user
        user_recommendations = {}
        for rec in recommendations:
            user_id = rec.get("user_id")
            if user_id not in user_recommendations:
                user_recommendations[user_id] = []
            user_recommendations[user_id].append(rec)
            
        # Conduct session for each user with recommendations
        for user_id, user_recs in user_recommendations.items():
            session = await self._conduct_user_coaching_session(user_id, user_recs)
            if session:
                sessions.append(session)
                
        # Update sessions count
        current_count = self._get_memory("coaching_sessions_conducted") or 0
        self._store_memory("coaching_sessions_conducted", current_count + len(sessions))
        
        return sessions
        
    async def _conduct_user_coaching_session(self, user_id: str, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Conduct coaching session for a specific user"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return None
            
        # Prioritize recommendations
        high_priority_recs = [r for r in recommendations if r.get("priority") == "high"]
        medium_priority_recs = [r for r in recommendations if r.get("priority") == "medium"]
        
        # Create coaching session
        session = {
            "id": f"session_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "user_id": user_id,
            "user_name": profile.get("name", "User"),
            "coaching_level": profile.get("coaching_level", "beginner"),
            "current_score": profile.get("current_score", 50),
            "recommendations_count": len(recommendations),
            "high_priority_actions": len(high_priority_recs),
            "session_focus": await self._determine_session_focus(profile, recommendations),
            "personalized_message": await self._generate_coaching_message(profile, recommendations),
            "action_plan": await self._create_action_plan(profile, recommendations),
            "conducted_at": datetime.now().isoformat()
        }
        
        # Store session
        self.coaching_sessions.append(session)
        
        return session
        
    async def _determine_session_focus(self, profile: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> str:
        """Determine the focus area for the coaching session"""
        rec_types = [r.get("type") for r in recommendations]
        
        if "air_quality" in rec_types:
            return "air_quality_improvement"
        elif "community_action" in rec_types:
            return "community_engagement"
        elif "goal_based" in rec_types:
            return "personal_goal_achievement"
        else:
            return "general_sustainability"
            
    async def _generate_coaching_message(self, profile: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> str:
        """Generate personalized coaching message"""
        name = profile.get("name", "there")
        score = profile.get("current_score", 50)
        level = profile.get("coaching_level", "beginner")
        
        if self.openai_client:
            try:
                prompt = f"""
                Create a personalized, encouraging sustainability coaching message for {name}.
                
                User Profile:
                - Current sustainability score: {score}/100
                - Coaching level: {level}
                - Recent recommendations: {len(recommendations)}
                
                Make it motivational, specific, and actionable. Keep it under 100 words.
                """
                
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=150
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                self.logger.error(f"Error generating AI coaching message: {e}")
                
        # Fallback message
        if score >= 80:
            return f"Great work, {name}! Your sustainability score of {score} shows real commitment. Keep up the excellent environmental actions!"
        elif score >= 60:
            return f"Nice progress, {name}! You're at {score} points. A few more consistent actions will boost your environmental impact significantly."
        else:
            return f"Welcome to your sustainability journey, {name}! Starting at {score} points, every small action counts. Let's build momentum together!"
            
    async def _create_action_plan(self, profile: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create personalized action plan"""
        action_plan = []
        
        # Sort recommendations by priority and difficulty
        sorted_recs = sorted(
            recommendations,
            key=lambda x: (
                {"high": 3, "medium": 2, "low": 1}.get(x.get("priority", "low"), 1),
                {"easy": 1, "medium": 2, "hard": 3}.get(x.get("difficulty", "easy"), 1)
            ),
            reverse=True
        )
        
        # Create action items (max 5 per session)
        for i, rec in enumerate(sorted_recs[:5]):
            action_item = {
                "step": i + 1,
                "action": rec.get("action"),
                "description": rec.get("message"),
                "priority": rec.get("priority"),
                "difficulty": rec.get("difficulty"),
                "estimated_time": self._estimate_action_time(rec),
                "points": rec.get("points", 10),
                "deadline": rec.get("expires_at")
            }
            action_plan.append(action_item)
            
        return action_plan
        
    def _estimate_action_time(self, recommendation: Dict[str, Any]) -> str:
        """Estimate time required for an action"""
        difficulty = recommendation.get("difficulty", "easy")
        action_type = recommendation.get("type", "general")
        
        time_estimates = {
            ("easy", "air_quality"): "5-10 minutes",
            ("easy", "weather_based"): "2-5 minutes", 
            ("easy", "community_action"): "10-15 minutes",
            ("medium", "air_quality"): "15-30 minutes",
            ("medium", "community_action"): "30-60 minutes",
            ("hard", "community_action"): "1-2 hours"
        }
        
        return time_estimates.get((difficulty, action_type), "10-20 minutes")
        
    async def _process_message(self, message: Dict[str, Any]) -> Any:
        """Process messages from other agents or users"""
        message_type = message.get("type")
        
        if message_type == "get_user_recommendations":
            user_id = message.get("user_id")
            return await self._get_user_recommendations(user_id)
            
        elif message_type == "complete_action":
            user_id = message.get("user_id")
            action_data = message.get("action_data")
            return await self._handle_action_completion(user_id, action_data)
            
        elif message_type == "update_user_profile":
            user_id = message.get("user_id")
            profile_updates = message.get("profile_updates")
            return await self._update_user_profile(user_id, profile_updates)
            
        elif message_type == "get_coaching_stats":
            return {
                "total_users": len(self.user_profiles),
                "sessions_conducted": self._get_memory("coaching_sessions_conducted") or 0,
                "recommendations_generated": self._get_memory("recommendations_generated") or 0,
                "active_challenges": len(self.sustainability_challenges)
            }
            
        return {"status": "unknown_message_type"}
        
    async def _get_user_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get current recommendations for a user"""
        # Return recent recommendations for the user
        recent_sessions = [
            session for session in self.coaching_sessions[-10:]  # Last 10 sessions
            if session.get("user_id") == user_id
        ]
        
        if recent_sessions:
            latest_session = recent_sessions[-1]
            return latest_session.get("action_plan", [])
            
        return []
        
    async def _handle_action_completion(self, user_id: str, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user completing an action"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return {"status": "error", "message": "User not found"}
            
        # Record activity
        activity = {
            "action": action_data.get("action"),
            "type": action_data.get("type", "general"),
            "points": action_data.get("points", 10),
            "impact_points": action_data.get("impact_points", 5),
            "timestamp": datetime.now().isoformat(),
            "completed": True
        }
        
        profile["activity_history"].append(activity)
        
        # Update score
        current_score = profile.get("current_score", 50)
        new_score = min(100, current_score + activity["points"] // 10)
        profile["current_score"] = new_score
        
        return {
            "status": "success",
            "points_earned": activity["points"],
            "new_score": new_score,
            "score_change": new_score - current_score
        }
        
    async def _update_user_profile(self, user_id: str, profile_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        if user_id not in self.user_profiles:
            # Create new user profile
            self.user_profiles[user_id] = {
                "name": profile_updates.get("name", "User"),
                "location": profile_updates.get("location", "general"),
                "preferences": profile_updates.get("preferences", []),
                "current_score": 50,
                "goals": profile_updates.get("goals", []),
                "activity_history": [],
                "coaching_level": "beginner"
            }
        else:
            # Update existing profile
            self.user_profiles[user_id].update(profile_updates)
            
        return {"status": "success", "message": "Profile updated"}
        
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for a user"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return {"error": "User not found"}
            
        # Get recent recommendations
        recommendations = await self._get_user_recommendations(user_id)
        
        # Get available challenges
        available_challenges = [
            challenge for challenge in self.sustainability_challenges
            if challenge.get("difficulty") == profile.get("coaching_level", "beginner")
        ]
        
        # Calculate progress metrics
        recent_activities = self._get_recent_activities(user_id)
        
        dashboard = {
            "user_profile": profile,
            "current_recommendations": recommendations,
            "available_challenges": available_challenges[:3],  # Top 3 challenges
            "progress_metrics": {
                "current_score": profile.get("current_score", 50),
                "coaching_level": profile.get("coaching_level", "beginner"),
                "recent_activities": len(recent_activities),
                "goals_progress": await self._calculate_goals_progress(user_id)
            },
            "achievements": await self._get_user_achievements(user_id),
            "next_milestone": await self._get_next_milestone(user_id)
        }
        
        return dashboard
        
    async def _calculate_goals_progress(self, user_id: str) -> Dict[str, float]:
        """Calculate progress towards user goals"""
        profile = self.user_profiles.get(user_id, {})
        goals = profile.get("goals", [])
        recent_activities = self._get_recent_activities(user_id)
        
        progress = {}
        for goal in goals:
            # Calculate progress based on relevant activities
            relevant_activities = [
                activity for activity in recent_activities
                if goal.lower() in activity.get("action", "").lower()
            ]
            progress[goal] = min(100.0, len(relevant_activities) * 20)  # 20% per relevant activity
            
        return progress
        
    async def _get_user_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user achievements"""
        profile = self.user_profiles.get(user_id, {})
        score = profile.get("current_score", 50)
        activities = len(profile.get("activity_history", []))
        
        achievements = []
        
        if score >= 70:
            achievements.append({"title": "Sustainability Champion", "description": "Reached 70+ sustainability score"})
        if activities >= 10:
            achievements.append({"title": "Action Hero", "description": "Completed 10+ environmental actions"})
        if profile.get("coaching_level") == "advanced":
            achievements.append({"title": "Environmental Expert", "description": "Reached advanced coaching level"})
            
        return achievements
        
    async def _get_next_milestone(self, user_id: str) -> Dict[str, Any]:
        """Get next milestone for user"""
        profile = self.user_profiles.get(user_id, {})
        score = profile.get("current_score", 50)
        level = profile.get("coaching_level", "beginner")
        
        if level == "beginner" and score < 70:
            return {"title": "Intermediate Coach", "description": "Reach 70 points to unlock intermediate coaching", "target": 70, "current": score}
        elif level == "intermediate" and score < 85:
            return {"title": "Advanced Coach", "description": "Reach 85 points to unlock advanced coaching", "target": 85, "current": score}
        else:
            return {"title": "Sustainability Master", "description": "Maintain your excellent environmental impact!", "target": 100, "current": score}
