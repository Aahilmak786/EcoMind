"""
Agent Orchestrator - Coordinates all AI agents in the EcoMind system
"""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
import json

from core.base_agent import BaseAgent

class AgentOrchestrator:
    """Orchestrates multiple AI agents for coordinated environmental action"""
    
    def __init__(self, agents: List[BaseAgent]):
        self.agents = {agent.name: agent for agent in agents}
        self.running = False
        self.tasks = []
        self.logger = logging.getLogger(__name__)
        self.shared_memory = {}
        
    async def start(self):
        """Start all agents and begin orchestration"""
        self.running = True
        
        # Initialize all agents
        for agent in self.agents.values():
            await agent.initialize()
            
        # Start agent tasks
        for agent in self.agents.values():
            task = asyncio.create_task(self._run_agent(agent))
            self.tasks.append(task)
            
        # Start coordination task
        coordination_task = asyncio.create_task(self._coordinate_agents())
        self.tasks.append(coordination_task)
        
        self.logger.info("All agents started successfully")
        
    async def stop(self):
        """Stop all agents gracefully"""
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
            
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        # Shutdown agents
        for agent in self.agents.values():
            await agent.shutdown()
            
        self.logger.info("All agents stopped")
        
    async def _run_agent(self, agent: BaseAgent):
        """Run an individual agent"""
        while self.running:
            try:
                # Execute agent's autonomous cycle
                result = await agent.execute_cycle(self.shared_memory)
                
                # Update shared memory with agent results
                if result:
                    self.shared_memory[agent.name] = {
                        'last_update': datetime.now().isoformat(),
                        'data': result
                    }
                    
                # Wait before next cycle
                await asyncio.sleep(agent.cycle_interval)
                
            except Exception as e:
                self.logger.error(f"Error in agent {agent.name}: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                
    async def _coordinate_agents(self):
        """Coordinate actions between agents"""
        while self.running:
            try:
                # Check for coordination opportunities
                await self._check_cross_agent_actions()
                
                # Update global state
                await self._update_global_state()
                
                # Wait before next coordination cycle
                await asyncio.sleep(30)  # Coordinate every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in coordination: {e}")
                await asyncio.sleep(10)
                
    async def _check_cross_agent_actions(self):
        """Check for actions that require multiple agents"""
        # Example: If monitoring agent detects pollution, trigger predictive and community agents
        monitoring_data = self.shared_memory.get('EnvironmentalMonitoringAgent', {}).get('data', {})
        
        if monitoring_data.get('pollution_alert'):
            # Trigger predictive analysis
            if 'PredictiveActionAgent' in self.agents:
                await self.agents['PredictiveActionAgent'].handle_pollution_alert(monitoring_data)
                
            # Trigger community coordination
            if 'CommunityCoordinationAgent' in self.agents:
                await self.agents['CommunityCoordinationAgent'].coordinate_pollution_response(monitoring_data)
                
    async def _update_global_state(self):
        """Update global system state"""
        self.shared_memory['system'] = {
            'timestamp': datetime.now().isoformat(),
            'agents_running': len([a for a in self.agents.values() if a.is_active]),
            'total_actions': sum(a.action_count for a in self.agents.values()),
            'uptime': datetime.now().isoformat()
        }
        
    def is_running(self) -> bool:
        """Check if orchestrator is running"""
        return self.running
        
    async def get_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {
            'orchestrator_running': self.running,
            'agents': {},
            'shared_memory_keys': list(self.shared_memory.keys()),
            'system_info': self.shared_memory.get('system', {})
        }
        
        for name, agent in self.agents.items():
            status['agents'][name] = {
                'active': agent.is_active,
                'action_count': agent.action_count,
                'last_action': agent.last_action_time.isoformat() if agent.last_action_time else None,
                'status': await agent.get_status()
            }
            
        return status
        
    async def send_message_to_agent(self, agent_name: str, message: Dict[str, Any]) -> Any:
        """Send a message to a specific agent"""
        if agent_name in self.agents:
            return await self.agents[agent_name].handle_message(message)
        else:
            raise ValueError(f"Agent {agent_name} not found")
            
    async def broadcast_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Broadcast a message to all agents"""
        results = {}
        for name, agent in self.agents.items():
            try:
                results[name] = await agent.handle_message(message)
            except Exception as e:
                results[name] = f"Error: {e}"
        return results
