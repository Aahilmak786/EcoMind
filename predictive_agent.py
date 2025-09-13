"""
Predictive Action Agent - Uses ML to predict environmental issues and take autonomous actions
"""

import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import json
import os
from openai import AsyncOpenAI

from core.base_agent import BaseAgent

class PredictiveActionAgent(BaseAgent):
    """Agent that predicts environmental issues and takes autonomous preventive actions"""
    
    def __init__(self):
        super().__init__("PredictiveActionAgent", cycle_interval=600)  # 10 minutes
        self.openai_client = None
        self.prediction_threshold = float(os.getenv("PREDICTION_THRESHOLD", "0.7"))
        self.historical_data = []
        self.prediction_models = {}
        
    async def _setup(self):
        """Initialize prediction systems"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "demo_key":
            self.openai_client = AsyncOpenAI(api_key=api_key)
        
        # Initialize prediction models
        self.prediction_models = {
            "air_quality": {"accuracy": 0.85, "last_trained": datetime.now()},
            "weather_patterns": {"accuracy": 0.78, "last_trained": datetime.now()},
            "pollution_events": {"accuracy": 0.82, "last_trained": datetime.now()}
        }
        
        self._store_memory("predictions_made", 0)
        self._store_memory("actions_taken", 0)
        
    async def _cleanup(self):
        """Cleanup resources"""
        pass
        
    async def execute_cycle(self, shared_memory: Dict[str, Any]) -> Dict[str, Any]:
        """Execute autonomous prediction and action cycle"""
        try:
            # Get latest environmental data
            monitoring_data = shared_memory.get("EnvironmentalMonitoringAgent", {}).get("data", {})
            
            if not monitoring_data:
                return {"status": "no_data", "message": "No monitoring data available"}
            
            # Update historical data
            self._update_historical_data(monitoring_data)
            
            # Generate predictions
            predictions = await self._generate_predictions(monitoring_data)
            
            # Evaluate predictions and take actions
            actions = await self._evaluate_and_act(predictions, monitoring_data)
            
            # Update models based on feedback
            await self._update_models(monitoring_data)
            
            self._record_action("prediction_cycle", {
                "predictions_generated": len(predictions),
                "actions_taken": len(actions),
                "data_points_analyzed": len(self.historical_data)
            })
            
            return {
                "predictions": predictions,
                "actions_taken": actions,
                "model_status": self.prediction_models,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in prediction cycle: {e}")
            return {"error": str(e)}
            
    def _update_historical_data(self, monitoring_data: Dict[str, Any]):
        """Update historical data for model training"""
        if "environmental_data" in monitoring_data:
            # Add timestamp and store data
            timestamped_data = {
                "timestamp": datetime.now().isoformat(),
                "data": monitoring_data["environmental_data"]
            }
            
            self.historical_data.append(timestamped_data)
            
            # Keep only last 1000 data points
            if len(self.historical_data) > 1000:
                self.historical_data = self.historical_data[-1000:]
                
    async def _generate_predictions(self, monitoring_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate environmental predictions using ML models"""
        predictions = []
        
        # Air Quality Prediction
        aqi_prediction = await self._predict_air_quality(monitoring_data)
        if aqi_prediction:
            predictions.append(aqi_prediction)
            
        # Weather Pattern Prediction
        weather_prediction = await self._predict_weather_patterns(monitoring_data)
        if weather_prediction:
            predictions.append(weather_prediction)
            
        # Pollution Event Prediction
        pollution_prediction = await self._predict_pollution_events(monitoring_data)
        if pollution_prediction:
            predictions.append(pollution_prediction)
            
        # Store predictions count
        current_count = self._get_memory("predictions_made") or 0
        self._store_memory("predictions_made", current_count + len(predictions))
        
        return predictions
        
    async def _predict_air_quality(self, monitoring_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict future air quality conditions"""
        try:
            environmental_data = monitoring_data.get("environmental_data", [])
            if not environmental_data:
                return None
                
            # Calculate trend from recent data
            recent_aqi_values = []
            for data in environmental_data:
                if "air_quality" in data and "aqi" in data["air_quality"]:
                    recent_aqi_values.append(data["air_quality"]["aqi"])
                    
            if len(recent_aqi_values) < 2:
                return None
                
            # Simple trend analysis (replace with ML model)
            current_avg = sum(recent_aqi_values) / len(recent_aqi_values)
            trend = self._calculate_trend(recent_aqi_values)
            
            # Predict next 6 hours
            predicted_aqi = current_avg + (trend * 6)  # 6 hours ahead
            confidence = min(0.95, self.prediction_models["air_quality"]["accuracy"])
            
            prediction = {
                "type": "air_quality",
                "current_value": current_avg,
                "predicted_value": predicted_aqi,
                "prediction_time": (datetime.now() + timedelta(hours=6)).isoformat(),
                "confidence": confidence,
                "trend": "improving" if trend < 0 else "worsening" if trend > 0 else "stable",
                "risk_level": self._assess_aqi_risk(predicted_aqi)
            }
            
            # Use AI for enhanced prediction if available
            if self.openai_client:
                enhanced_prediction = await self._enhance_prediction_with_ai(prediction, monitoring_data)
                if enhanced_prediction:
                    prediction.update(enhanced_prediction)
                    
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting air quality: {e}")
            return None
            
    async def _predict_weather_patterns(self, monitoring_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict weather pattern changes"""
        try:
            environmental_data = monitoring_data.get("environmental_data", [])
            if not environmental_data:
                return None
                
            # Analyze weather trends
            temps = []
            humidity = []
            pressure = []
            
            for data in environmental_data:
                if "weather" in data:
                    weather = data["weather"]
                    temps.append(weather.get("temperature", 0))
                    humidity.append(weather.get("humidity", 0))
                    pressure.append(weather.get("pressure", 1000))
                    
            if len(temps) < 2:
                return None
                
            # Calculate trends
            temp_trend = self._calculate_trend(temps)
            pressure_trend = self._calculate_trend(pressure)
            
            # Predict weather changes
            prediction = {
                "type": "weather_patterns",
                "temperature_trend": temp_trend,
                "pressure_trend": pressure_trend,
                "predicted_conditions": self._predict_weather_conditions(temp_trend, pressure_trend),
                "prediction_time": (datetime.now() + timedelta(hours=12)).isoformat(),
                "confidence": self.prediction_models["weather_patterns"]["accuracy"]
            }
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting weather patterns: {e}")
            return None
            
    async def _predict_pollution_events(self, monitoring_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict potential pollution events"""
        try:
            analysis = monitoring_data.get("analysis", {})
            alerts = monitoring_data.get("alerts", [])
            
            # Check for pollution event indicators
            risk_factors = []
            
            # High AQI trend
            if analysis.get("average_aqi", 0) > 80:
                risk_factors.append("high_baseline_pollution")
                
            # Existing pollution hotspots
            if analysis.get("pollution_hotspots"):
                risk_factors.append("active_hotspots")
                
            # Recent alerts
            if alerts:
                risk_factors.append("recent_alerts")
                
            if not risk_factors:
                return None
                
            # Calculate pollution event probability
            probability = min(0.95, len(risk_factors) * 0.3)
            
            prediction = {
                "type": "pollution_event",
                "probability": probability,
                "risk_factors": risk_factors,
                "predicted_severity": "high" if probability > 0.7 else "moderate",
                "prediction_time": (datetime.now() + timedelta(hours=4)).isoformat(),
                "confidence": self.prediction_models["pollution_events"]["accuracy"],
                "recommended_actions": self._get_pollution_prevention_actions(probability)
            }
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting pollution events: {e}")
            return None
            
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend from a series of values"""
        if len(values) < 2:
            return 0
            
        # Simple linear trend calculation
        x = np.arange(len(values))
        y = np.array(values)
        
        # Calculate slope
        n = len(values)
        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x * x) - np.sum(x) ** 2)
        
        return slope
        
    def _assess_aqi_risk(self, aqi: float) -> str:
        """Assess risk level based on AQI value"""
        if aqi <= 50:
            return "good"
        elif aqi <= 100:
            return "moderate"
        elif aqi <= 150:
            return "unhealthy_sensitive"
        elif aqi <= 200:
            return "unhealthy"
        else:
            return "hazardous"
            
    def _predict_weather_conditions(self, temp_trend: float, pressure_trend: float) -> str:
        """Predict weather conditions based on trends"""
        if pressure_trend < -0.5:
            return "storm_approaching"
        elif pressure_trend > 0.5:
            return "clearing_weather"
        elif temp_trend > 2:
            return "warming_trend"
        elif temp_trend < -2:
            return "cooling_trend"
        else:
            return "stable_conditions"
            
    def _get_pollution_prevention_actions(self, probability: float) -> List[str]:
        """Get recommended actions to prevent pollution events"""
        actions = []
        
        if probability > 0.5:
            actions.extend([
                "increase_monitoring_frequency",
                "alert_community_coordinators",
                "prepare_air_filtration_systems"
            ])
            
        if probability > 0.7:
            actions.extend([
                "activate_emergency_protocols",
                "coordinate_traffic_reduction",
                "notify_health_authorities"
            ])
            
        return actions
        
    async def _enhance_prediction_with_ai(self, prediction: Dict[str, Any], monitoring_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance predictions using AI analysis"""
        try:
            prompt = f"""
            Analyze this environmental prediction and provide enhanced insights:
            
            Prediction: {json.dumps(prediction, indent=2)}
            Current Data: {json.dumps(monitoring_data.get('analysis', {}), indent=2)}
            
            Provide:
            1. Risk assessment refinement
            2. Additional factors to consider
            3. Specific recommendations
            4. Confidence adjustment reasoning
            
            Respond in JSON format with keys: risk_assessment, factors, recommendations, confidence_notes
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            ai_analysis = json.loads(response.choices[0].message.content)
            return {
                "ai_enhanced": True,
                "ai_analysis": ai_analysis
            }
            
        except Exception as e:
            self.logger.error(f"Error enhancing prediction with AI: {e}")
            return None
            
    async def _evaluate_and_act(self, predictions: List[Dict[str, Any]], monitoring_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate predictions and take autonomous actions"""
        actions = []
        
        for prediction in predictions:
            # Determine if action is needed
            if self._should_take_action(prediction):
                action = await self._take_autonomous_action(prediction, monitoring_data)
                if action:
                    actions.append(action)
                    
        # Update actions count
        current_count = self._get_memory("actions_taken") or 0
        self._store_memory("actions_taken", current_count + len(actions))
        
        return actions
        
    def _should_take_action(self, prediction: Dict[str, Any]) -> bool:
        """Determine if autonomous action should be taken"""
        confidence = prediction.get("confidence", 0)
        
        if prediction["type"] == "air_quality":
            risk_level = prediction.get("risk_level", "good")
            return confidence > self.prediction_threshold and risk_level in ["unhealthy", "hazardous"]
            
        elif prediction["type"] == "pollution_event":
            probability = prediction.get("probability", 0)
            return confidence > self.prediction_threshold and probability > 0.6
            
        elif prediction["type"] == "weather_patterns":
            conditions = prediction.get("predicted_conditions", "")
            return confidence > self.prediction_threshold and "storm" in conditions
            
        return False
        
    async def _take_autonomous_action(self, prediction: Dict[str, Any], monitoring_data: Dict[str, Any]) -> Dict[str, Any]:
        """Take autonomous action based on prediction"""
        action = {
            "timestamp": datetime.now().isoformat(),
            "prediction_type": prediction["type"],
            "action_type": "",
            "details": {},
            "success": True
        }
        
        try:
            if prediction["type"] == "air_quality":
                action.update(await self._handle_air_quality_prediction(prediction))
                
            elif prediction["type"] == "pollution_event":
                action.update(await self._handle_pollution_event_prediction(prediction))
                
            elif prediction["type"] == "weather_patterns":
                action.update(await self._handle_weather_prediction(prediction))
                
        except Exception as e:
            action["success"] = False
            action["error"] = str(e)
            self.logger.error(f"Error taking action: {e}")
            
        return action
        
    async def _handle_air_quality_prediction(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle air quality prediction actions"""
        return {
            "action_type": "air_quality_alert",
            "details": {
                "predicted_aqi": prediction.get("predicted_value"),
                "risk_level": prediction.get("risk_level"),
                "notifications_sent": ["community_coordinator", "health_authorities"],
                "preventive_measures": ["increase_monitoring", "prepare_air_filters"]
            }
        }
        
    async def _handle_pollution_event_prediction(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pollution event prediction actions"""
        recommended_actions = prediction.get("recommended_actions", [])
        
        return {
            "action_type": "pollution_prevention",
            "details": {
                "probability": prediction.get("probability"),
                "actions_initiated": recommended_actions,
                "emergency_protocols": prediction.get("predicted_severity") == "high",
                "coordination_requests": ["traffic_management", "industrial_monitoring"]
            }
        }
        
    async def _handle_weather_prediction(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Handle weather prediction actions"""
        return {
            "action_type": "weather_preparation",
            "details": {
                "predicted_conditions": prediction.get("predicted_conditions"),
                "preparation_actions": ["secure_monitoring_equipment", "adjust_sampling_frequency"],
                "alerts_issued": prediction.get("predicted_conditions") == "storm_approaching"
            }
        }
        
    async def _update_models(self, monitoring_data: Dict[str, Any]):
        """Update prediction models based on new data"""
        # Simulate model updates (replace with actual ML model training)
        for model_name in self.prediction_models:
            # Slightly improve accuracy over time
            current_accuracy = self.prediction_models[model_name]["accuracy"]
            self.prediction_models[model_name]["accuracy"] = min(0.95, current_accuracy + 0.001)
            self.prediction_models[model_name]["last_trained"] = datetime.now()
            
    async def _process_message(self, message: Dict[str, Any]) -> Any:
        """Process messages from other agents"""
        message_type = message.get("type")
        
        if message_type == "get_predictions":
            return self._get_memory("latest_predictions")
            
        elif message_type == "request_prediction":
            prediction_type = message.get("prediction_type")
            data = message.get("data", {})
            
            if prediction_type == "air_quality":
                return await self._predict_air_quality(data)
            elif prediction_type == "pollution_event":
                return await self._predict_pollution_events(data)
                
        elif message_type == "update_threshold":
            new_threshold = message.get("threshold")
            if 0 <= new_threshold <= 1:
                self.prediction_threshold = new_threshold
                return {"status": "success", "new_threshold": new_threshold}
                
        return {"status": "unknown_message_type"}
        
    async def handle_pollution_alert(self, alert_data: Dict[str, Any]):
        """Handle pollution alert from monitoring agent"""
        self.logger.info(f"Processing pollution alert for prediction: {alert_data}")
        
        # Generate immediate prediction based on alert
        prediction = await self._predict_pollution_events(alert_data)
        
        if prediction and prediction.get("probability", 0) > 0.5:
            # Take immediate action
            action = await self._take_autonomous_action(prediction, alert_data)
            self._record_action("emergency_prediction_response", {
                "alert_processed": True,
                "prediction_generated": prediction is not None,
                "action_taken": action is not None
            })
            
            return {
                "prediction": prediction,
                "action": action,
                "status": "processed"
            }
            
        return {"status": "no_action_needed"}
