"""
Base Agent Class - Foundation for all EcoMind AI agents
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class BaseAgent(ABC):
    """Abstract base class for all AI agents in the EcoMind system"""
    
    def __init__(self, name: str, cycle_interval: int = 60):
        self.name = name
        self.cycle_interval = cycle_interval  # seconds between autonomous cycles
        self.is_active = False
        self.action_count = 0
        self.last_action_time: Optional[datetime] = None
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.memory = {}
        
    async def initialize(self):
        """Initialize the agent"""
        self.is_active = True
        self.logger.info(f"Agent {self.name} initialized")
        await self._setup()
        
    async def shutdown(self):
        """Shutdown the agent gracefully"""
        self.is_active = False
        await self._cleanup()
        self.logger.info(f"Agent {self.name} shutdown")
        
    @abstractmethod
    async def _setup(self):
        """Agent-specific setup logic"""
        pass
        
    @abstractmethod
    async def _cleanup(self):
        """Agent-specific cleanup logic"""
        pass
        
    @abstractmethod
    async def execute_cycle(self, shared_memory: Dict[str, Any]) -> Dict[str, Any]:
        """Execute one autonomous cycle of the agent"""
        pass
        
    async def handle_message(self, message: Dict[str, Any]) -> Any:
        """Handle incoming messages from other agents or the orchestrator"""
        self.logger.info(f"Received message: {message}")
        return await self._process_message(message)
        
    @abstractmethod
    async def _process_message(self, message: Dict[str, Any]) -> Any:
        """Process incoming messages - implemented by subclasses"""
        pass
        
    async def get_status(self) -> Dict[str, Any]:
        """Get current status of the agent"""
        return {
            'name': self.name,
            'active': self.is_active,
            'action_count': self.action_count,
            'last_action': self.last_action_time.isoformat() if self.last_action_time else None,
            'cycle_interval': self.cycle_interval,
            'memory_keys': list(self.memory.keys())
        }
        
    def _record_action(self, action_type: str, details: Dict[str, Any] = None):
        """Record an action taken by the agent"""
        self.action_count += 1
        self.last_action_time = datetime.now()
        self.logger.info(f"Action recorded: {action_type} - {details}")
        
    def _store_memory(self, key: str, value: Any):
        """Store information in agent memory"""
        self.memory[key] = {
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        
    def _get_memory(self, key: str) -> Any:
        """Retrieve information from agent memory"""
        return self.memory.get(key, {}).get('value')
