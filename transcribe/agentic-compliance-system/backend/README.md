# Agentic AI Compliance System Backend

A real-time compliance monitoring system built with CrewAI agents that processes multilingual transcripts and detects regulatory violations against documents stored in a vector database.

## 🏗️ Architecture

The system consists of three main CrewAI agents:

1. **Compliance Agent** - Analyzes transcript segments for violations against regulatory documents
2. **Document Classifier Agent** - Automatically categorizes uploaded regulatory documents
3. **Alert Manager Agent** - Generates and manages compliance alerts with severity levels

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Pinecone API key

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Create Pinecone index:**
   ```bash
   # The system will automatically create the index if it doesn't exist
   # Make sure your Pinecone API key has the necessary permissions
   ```

4. **Run the server:**
   ```bash
   cd backend
   python main.py
   ```

The server will start on `http://localhost:8000`

## 📋 API Endpoints

### Health Check
- `GET /health` - Check system status

### WebSocket
- `WS /ws` - Real-time alert streaming

### Transcript Processing
- `POST /api/process-transcript` - Process transcript segments for violations

### Document Management
- `POST /api/upload-document` - Upload and classify regulatory documents
- `GET /api/categories` - Get available compliance categories

### Alert Management
- `GET /api/alerts` - Get filtered alerts
- `POST /api/alerts/{alert_id}/acknowledge` - Acknowledge an alert
- `GET /api/alerts/statistics` - Get alert statistics

### System Statistics
- `GET /api/compliance/statistics` - Get compliance system statistics

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for LLM operations | Yes | - |
| `PINECONE_API_KEY` | Pinecone API key for vector database | Yes | - |
| `PINECONE_INDEX_NAME` | Pinecone index name | No | `compliance-documents` |
| `PINECONE_ENVIRONMENT` | Pinecone environment | No | `gcp-starter` |

### Agent Configuration

Each agent can be configured through their respective classes:

```python
# Compliance Agent
compliance_agent = ComplianceAgent(
    pinecone_api_key="your_key",
    pinecone_index_name="your_index",
    openai_api_key="your_key"
)

# Document Classifier
classifier = DocumentClassifierAgent(
    openai_api_key="your_key"
)

# Alert Manager
alert_manager = AlertManagerAgent(
    openai_api_key="your_key",
    alert_callback=your_callback_function
)
```

## 🧠 Agent Details

### Compliance Agent

**Purpose:** Analyzes transcript segments for compliance violations

**CrewAI Agents:**
- **Compliance Analyst** - Identifies potential violations
- **Context Analyzer** - Determines severity and business impact
- **Alert Generator** - Creates actionable alerts

**Tools:**
- Vector database search
- Document similarity analysis
- Compliance rule matching

### Document Classifier Agent

**Purpose:** Automatically categorizes regulatory documents

**CrewAI Agents:**
- **Document Analyzer** - Identifies key themes and topics
- **Classifier** - Assigns compliance categories
- **Metadata Extractor** - Extracts keywords and important phrases

**Categories:**
- ESG (Environmental, Social, Governance)
- Financial
- Legal
- Ethical
- Operational
- Industry-specific

### Alert Manager Agent

**Purpose:** Manages compliance alerts and notifications

**CrewAI Agents:**
- **Alert Assessor** - Evaluates violation severity
- **Alert Formulator** - Creates clear alert messages
- **Action Planner** - Determines required actions

**Alert Types:**
- Compliance Violation
- Policy Breach
- Regulatory Risk
- Ethical Concern
- Operational Issue

**Severity Levels:**
- Low
- Medium
- High
- Critical

## 📊 Usage Examples

### Processing a Transcript Segment

```python
import requests

# Process a transcript segment
response = requests.post("http://localhost:8000/api/process-transcript", json={
    "speaker_id": "speaker_1",
    "timestamp": "2024-01-15T10:30:00Z",
    "content": "We should consider creative accounting methods to improve our quarterly results."
})

print(response.json())
```

### Uploading a Document

```python
# Upload a regulatory document
response = requests.post("http://localhost:8000/api/upload-document", json={
    "title": "Financial Reporting Standards",
    "content": "All financial statements must be prepared in accordance with GAAP...",
    "category": "financial"
})

print(response.json())
```

### WebSocket Connection for Real-time Alerts

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'compliance_alert') {
        console.log('New alert:', data.data);
        // Handle the alert in your UI
    }
};
```

## 🔍 Monitoring and Debugging

### Logs

The system provides detailed logging for debugging:

```bash
# View logs
tail -f logs/compliance_system.log
```

### Statistics

Monitor system performance:

```bash
# Get alert statistics
curl http://localhost:8000/api/alerts/statistics

# Get compliance statistics
curl http://localhost:8000/api/compliance/statistics
```

### Health Check

```bash
curl http://localhost:8000/health
```

## 🛠️ Development

### Adding New Compliance Categories

1. Update the `compliance_categories` dictionary in `DocumentClassifierAgent`
2. Add relevant keywords and subcategories
3. Test with sample documents

### Customizing Alert Logic

1. Modify the `_should_suppress_alert` method in `AlertManagerAgent`
2. Adjust severity thresholds
3. Update alert message templates

### Extending Agent Tools

1. Add new tools to the respective agent classes
2. Update the agent creation in `_create_agents` methods
3. Test with sample data

## 🚨 Troubleshooting

### Common Issues

1. **Pinecone Connection Error**
   - Verify API key and environment
   - Check index permissions
   - Ensure index exists

2. **OpenAI API Errors**
   - Verify API key is valid
   - Check rate limits
   - Ensure sufficient credits

3. **Agent Initialization Failures**
   - Check all environment variables
   - Verify API keys are working
   - Review error logs

### Performance Optimization

1. **Reduce API Calls**
   - Implement caching for document embeddings
   - Batch process transcript segments
   - Use connection pooling

2. **Improve Response Time**
   - Optimize vector search parameters
   - Use async processing where possible
   - Implement request queuing

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the troubleshooting section 