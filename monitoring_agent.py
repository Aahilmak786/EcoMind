"""
Environmental Monitoring Agent - Autonomous environmental data collection and analysis
"""

import asyncio
import aiohttp
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

from core.base_agent import BaseAgent

class EnvironmentalMonitoringAgent(BaseAgent):
    """Agent that autonomously monitors environmental conditions"""
    
    def __init__(self):
        super().__init__("EnvironmentalMonitoringAgent", cycle_interval=300)  # 5 minutes
        self.weather_api_key = os.getenv("WEATHER_API_KEY", "demo_key")
        self.air_quality_api_key = os.getenv("AIR_QUALITY_API_KEY", "demo_key")
        self.monitoring_locations = [
            {"name": "City Center", "lat": 40.7128, "lon": -74.0060},
            {"name": "Industrial Zone", "lat": 40.7589, "lon": -73.9851},
            {"name": "Residential Area", "lat": 40.6892, "lon": -74.0445}
        ]
        
    async def _setup(self):
        """Initialize monitoring systems"""
        self.session = aiohttp.ClientSession()
        self._store_memory("last_alert_time", datetime.now() - timedelta(hours=1))
        
    async def _cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'session'):
            await self.session.close()
            
    async def execute_cycle(self, shared_memory: Dict[str, Any]) -> Dict[str, Any]:
        """Execute autonomous monitoring cycle"""
        try:
            # Collect environmental data
            environmental_data = await self._collect_environmental_data()
            
            # Analyze data for anomalies
            analysis = await self._analyze_data(environmental_data)
            
            # Check for alerts
            alerts = await self._check_for_alerts(analysis)
            
            # Record action
            self._record_action("monitoring_cycle", {
                "locations_monitored": len(self.monitoring_locations),
                "alerts_generated": len(alerts),
                "data_points": len(environmental_data)
            })
            
            return {
                "environmental_data": environmental_data,
                "analysis": analysis,
                "alerts": alerts,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in monitoring cycle: {e}")
            return {"error": str(e)}
            
    async def _collect_environmental_data(self) -> List[Dict[str, Any]]:
        """Collect environmental data from multiple sources"""
        data = []
        
        for location in self.monitoring_locations:
            try:
                # Simulate weather data collection (replace with real API calls)
                weather_data = await self._get_weather_data(location)
                air_quality_data = await self._get_air_quality_data(location)
                
                location_data = {
                    "location": location["name"],
                    "coordinates": {"lat": location["lat"], "lon": location["lon"]},
                    "weather": weather_data,
                    "air_quality": air_quality_data,
                    "timestamp": datetime.now().isoformat()
                }
                
                data.append(location_data)
                
            except Exception as e:
                self.logger.error(f"Error collecting data for {location['name']}: {e}")
                
        return data
        
    async def _get_weather_data(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Get weather data for a location"""
        # Simulate weather API call (replace with real implementation)
        import random
        
        return {
            "temperature": round(random.uniform(15, 35), 1),
            "humidity": round(random.uniform(30, 90), 1),
            "wind_speed": round(random.uniform(0, 20), 1),
            "pressure": round(random.uniform(980, 1030), 1),
            "visibility": round(random.uniform(5, 15), 1)
        }
        
    async def _get_air_quality_data(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Get air quality data for a location"""
        # Simulate air quality API call (replace with real implementation)
        import random
        
        return {
            "aqi": random.randint(20, 150),
            "pm25": round(random.uniform(5, 50), 1),
            "pm10": round(random.uniform(10, 80), 1),
            "co": round(random.uniform(0.1, 2.0), 2),
            "no2": round(random.uniform(10, 60), 1),
            "o3": round(random.uniform(20, 100), 1)
        }
        
    async def _analyze_data(self, environmental_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze environmental data for patterns and anomalies"""
        analysis = {
            "average_aqi": 0,
            "pollution_hotspots": [],
            "weather_patterns": {},
            "trend_analysis": {}
        }
        
        if not environmental_data:
            return analysis
            
        # Calculate averages
        total_aqi = sum(data["air_quality"]["aqi"] for data in environmental_data)
        analysis["average_aqi"] = total_aqi / len(environmental_data)
        
        # Identify pollution hotspots
        for data in environmental_data:
            if data["air_quality"]["aqi"] > 100:  # Unhealthy threshold
                analysis["pollution_hotspots"].append({
                    "location": data["location"],
                    "aqi": data["air_quality"]["aqi"],
                    "severity": "high" if data["air_quality"]["aqi"] > 150 else "moderate"
                })
                
        # Weather pattern analysis
        temps = [data["weather"]["temperature"] for data in environmental_data]
        analysis["weather_patterns"] = {
            "avg_temperature": sum(temps) / len(temps),
            "temperature_range": max(temps) - min(temps)
        }
        
        return analysis
        
    async def _check_for_alerts(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for environmental alerts"""
        alerts = []
        
        # Air quality alerts
        if analysis["average_aqi"] > 100:
            alerts.append({
                "type": "air_quality",
                "severity": "high" if analysis["average_aqi"] > 150 else "moderate",
                "message": f"Average AQI is {analysis['average_aqi']:.1f} - Unhealthy air quality detected",
                "timestamp": datetime.now().isoformat(),
                "action_required": True
            })
            
        # Pollution hotspot alerts
        for hotspot in analysis["pollution_hotspots"]:
            alerts.append({
                "type": "pollution_hotspot",
                "severity": hotspot["severity"],
                "message": f"Pollution hotspot detected at {hotspot['location']} (AQI: {hotspot['aqi']})",
                "location": hotspot["location"],
                "timestamp": datetime.now().isoformat(),
                "action_required": True
            })
            
        # Store alerts in memory
        if alerts:
            self._store_memory("recent_alerts", alerts)
            self._store_memory("last_alert_time", datetime.now())
            
        return alerts
        
    async def _process_message(self, message: Dict[str, Any]) -> Any:
        """Process messages from other agents"""
        message_type = message.get("type")
        
        if message_type == "get_current_data":
            # Return current environmental data
            return self._get_memory("latest_environmental_data")
            
        elif message_type == "get_location_data":
            location = message.get("location")
            # Return data for specific location
            latest_data = self._get_memory("latest_environmental_data") or []
            for data in latest_data:
                if data.get("location") == location:
                    return data
            return None
            
        elif message_type == "set_monitoring_location":
            # Add new monitoring location
            new_location = message.get("location")
            if new_location:
                self.monitoring_locations.append(new_location)
                return {"status": "success", "message": "Location added"}
                
        return {"status": "unknown_message_type"}
        
    async def handle_pollution_alert(self, alert_data: Dict[str, Any]):
        """Handle pollution alert from external source"""
        self.logger.info(f"Handling external pollution alert: {alert_data}")
        
        # Increase monitoring frequency temporarily
        original_interval = self.cycle_interval
        self.cycle_interval = 60  # Monitor every minute during alert
        
        # Schedule return to normal interval after 30 minutes
        asyncio.create_task(self._reset_monitoring_interval(original_interval, 1800))
        
        self._record_action("pollution_alert_response", alert_data)
        
    async def _reset_monitoring_interval(self, original_interval: int, delay: int):
        """Reset monitoring interval after delay"""
        await asyncio.sleep(delay)
        self.cycle_interval = original_interval
        self.logger.info("Monitoring interval reset to normal")
