# EcoMind Setup Guide for Judges

## Quick Start (5 minutes)

### Prerequisites
- Python 3.9+ installed
- Git installed
- OpenAI API key (for AI functionality)

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ecomind-hackathon.git
cd ecomind-hackathon
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
```
Edit `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

4. **Run the system**
```bash
python main.py
```

5. **Access the application**
- Main Dashboard: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Agent Status: http://localhost:8000/agents/status

## Testing the Autonomous Agents

### 1. Check Agent Status
```bash
curl http://localhost:8000/api/agents/status
```

### 2. View Environmental Data
```bash
curl http://localhost:8000/api/environmental/current
```

### 3. Get System Dashboard
```bash
curl http://localhost:8000/api/dashboard
```

### 4. Test Community Features
```bash
curl http://localhost:8000/api/community/campaigns
```

## Demo Scenarios

### Scenario 1: Environmental Alert Response
1. Visit http://localhost:8000/api/environmental/current
2. Observe real-time environmental data
3. Check http://localhost:8000/api/agents/status to see agent responses
4. View community campaigns at http://localhost:8000/api/community/campaigns

### Scenario 2: Personal Coaching
1. Create a test user: `POST /api/coaching/users/test-user-123/profile`
2. Get recommendations: `GET /api/coaching/users/test-user-123/recommendations`
3. Complete an action: `POST /api/coaching/users/test-user-123/complete_action`
4. View updated dashboard: `GET /api/coaching/users/test-user-123/dashboard`

## Troubleshooting

### Common Issues

**Port already in use:**
```bash
# Change port in .env file or use different port
python main.py --port 8001
```

**Missing OpenAI API key:**
- Ensure OPENAI_API_KEY is set in .env file
- System will run in demo mode without API key (limited functionality)

**Database connection issues:**
- System uses SQLite by default (no setup required)
- For PostgreSQL, update DATABASE_URL in .env

## Architecture Verification

### Agent Independence Test
```python
# Each agent should show autonomous operation
import requests
import time

# Monitor agent cycles
for i in range(5):
    response = requests.get("http://localhost:8000/api/agents/status")
    print(f"Cycle {i}: {response.json()}")
    time.sleep(10)
```

### Decision Making Test
```python
# Verify autonomous decision making
response = requests.get("http://localhost:8000/api/analytics/environmental")
print("Environmental Analytics:", response.json())

response = requests.get("http://localhost:8000/api/analytics/community")
print("Community Analytics:", response.json())
```

## Performance Monitoring

### System Health
- CPU Usage: Monitor via `/api/agents/status`
- Memory Usage: Check agent memory consumption
- Response Times: API endpoint performance
- Error Rates: Monitor logs for exceptions

### Agent Performance
- Decision Frequency: Autonomous decisions per minute
- Accuracy Metrics: Prediction accuracy rates
- Coordination Efficiency: Inter-agent communication success

## File Structure Overview
```
ecomind-hackathon/
├── agents/                 # AI agent implementations
├── api/                   # REST API routes
├── core/                  # Core orchestration logic
├── static/                # Frontend assets
├── image_templates/       # Logo and media templates
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```
