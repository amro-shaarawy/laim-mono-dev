from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json
import os
from datetime import datetime
import uvicorn

# Import our agents
from agents.compliance_agent import ComplianceAgent, ComplianceViolation
from agents.document_classifier_agent import DocumentClassifierAgent, DocumentCategory
from agents.alert_manager_agent import AlertManagerAgent, ComplianceAlert, AlertSeverity, AlertType

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Pydantic models for API requests/responses
class TranscriptSegment(BaseModel):
    speaker_id: str
    timestamp: str
    content: str

class DocumentUpload(BaseModel):
    title: str
    content: str
    category: Optional[str] = "general"

class AlertFilter(BaseModel):
    severity: Optional[str] = None
    speaker_id: Optional[str] = None
    time_range_minutes: Optional[int] = None

# Initialize FastAPI app
app = FastAPI(
    title="Agentic AI Compliance System",
    description="Real-time compliance monitoring using CrewAI agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for agents
compliance_agent: Optional[ComplianceAgent] = None
document_classifier: Optional[DocumentClassifierAgent] = None
alert_manager: Optional[AlertManagerAgent] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected clients
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Alert callback function for WebSocket broadcasting
async def alert_callback(alert: ComplianceAlert):
    """Callback function to send alerts to connected WebSocket clients"""
    alert_data = {
        "type": "compliance_alert",
        "data": {
            "id": alert.id,
            "speaker_id": alert.speaker_id,
            "timestamp": alert.timestamp,
            "message": alert.message,
            "severity": alert.severity.value,
            "alert_type": alert.alert_type.value,
            "action_required": alert.action_required,
            "action_items": alert.action_items
        }
    }
    await manager.broadcast(json.dumps(alert_data))

# Initialize agents on startup
@app.on_event("startup")
async def startup_event():
    global compliance_agent, document_classifier, alert_manager
    
    # Get API keys from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    pinecone_index_name = os.getenv("PINECONE_INDEX_NAME", "compliance-documents")
    
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    if not pinecone_api_key:
        raise ValueError("PINECONE_API_KEY environment variable is required")
    
    try:
        # Initialize agents
        compliance_agent = ComplianceAgent(
            pinecone_api_key=pinecone_api_key,
            pinecone_index_name=pinecone_index_name,
            openai_api_key=openai_api_key
        )
        
        document_classifier = DocumentClassifierAgent(
            openai_api_key=openai_api_key
        )
        
        alert_manager = AlertManagerAgent(
            openai_api_key=openai_api_key,
            alert_callback=alert_callback
        )
        
        print("✅ All agents initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing agents: {e}")
        raise

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": {
            "compliance_agent": compliance_agent is not None,
            "document_classifier": document_classifier is not None,
            "alert_manager": alert_manager is not None
        }
    }

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Process transcript segment endpoint
@app.post("/api/process-transcript")
async def process_transcript_segment(segment: TranscriptSegment):
    """Process a transcript segment for compliance violations"""
    if not compliance_agent or not alert_manager:
        raise HTTPException(status_code=500, detail="Agents not initialized")
    
    try:
        # Process the transcript segment for compliance violations
        violations = await compliance_agent.process_transcript_segment(
            transcript=segment.content,
            speaker_id=segment.speaker_id,
            timestamp=segment.timestamp
        )
        
        # Process violations through alert manager
        alerts = []
        for violation in violations:
            violation_data = {
                "speaker_id": violation.speaker_id,
                "timestamp": violation.timestamp,
                "transcript_segment": violation.transcript_segment,
                "violation_type": violation.violation_type,
                "severity": violation.severity,
                "matched_document": violation.matched_document,
                "confidence_score": violation.confidence_score,
                "context": violation.context
            }
            
            alert = await alert_manager.process_violation(violation_data)
            if alert:
                alerts.append(alert)
        
        return {
            "success": True,
            "violations_detected": len(violations),
            "alerts_generated": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing transcript: {str(e)}")

# Upload document endpoint
@app.post("/api/upload-document")
async def upload_document(document: DocumentUpload):
    """Upload and classify a regulatory document"""
    if not document_classifier or not compliance_agent:
        raise HTTPException(status_code=500, detail="Agents not initialized")
    
    try:
        # Classify the document
        category = await document_classifier.classify_document(
            document_content=document.content,
            document_title=document.title
        )
        
        # Add document to vector database
        success = compliance_agent.add_document_to_database(
            document_content=document.content,
            document_title=document.title,
            category=category.category
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add document to database")
        
        return {
            "success": True,
            "document_id": f"doc_{datetime.now().timestamp()}",
            "classification": {
                "category": category.category,
                "subcategory": category.subcategory,
                "confidence": category.confidence,
                "keywords": category.keywords
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

# Get alerts endpoint
@app.get("/api/alerts")
async def get_alerts(
    severity: Optional[str] = None,
    speaker_id: Optional[str] = None,
    time_range_minutes: Optional[int] = None
):
    """Get filtered alerts"""
    if not alert_manager:
        raise HTTPException(status_code=500, detail="Alert manager not initialized")
    
    try:
        # Convert severity string to enum if provided
        severity_enum = None
        if severity:
            try:
                severity_enum = AlertSeverity(severity)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
        
        alerts = alert_manager.get_alerts(
            severity_filter=severity_enum,
            speaker_filter=speaker_id,
            time_range_minutes=time_range_minutes
        )
        
        return {
            "alerts": [alert.dict() for alert in alerts],
            "total_count": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alerts: {str(e)}")

# Acknowledge alert endpoint
@app.post("/api/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, acknowledged_by: str):
    """Acknowledge an alert"""
    if not alert_manager:
        raise HTTPException(status_code=500, detail="Alert manager not initialized")
    
    try:
        success = alert_manager.acknowledge_alert(alert_id, acknowledged_by)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "success": True,
            "alert_id": alert_id,
            "acknowledged_by": acknowledged_by,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error acknowledging alert: {str(e)}")

# Get alert statistics endpoint
@app.get("/api/alerts/statistics")
async def get_alert_statistics():
    """Get alert statistics"""
    if not alert_manager:
        raise HTTPException(status_code=500, detail="Alert manager not initialized")
    
    try:
        stats = alert_manager.get_alert_statistics()
        return {
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

# Get compliance statistics endpoint
@app.get("/api/compliance/statistics")
async def get_compliance_statistics():
    """Get compliance system statistics"""
    if not compliance_agent:
        raise HTTPException(status_code=500, detail="Compliance agent not initialized")
    
    try:
        stats = compliance_agent.get_compliance_statistics()
        return {
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving compliance statistics: {str(e)}")

# Get available categories endpoint
@app.get("/api/categories")
async def get_categories():
    """Get available compliance categories"""
    if not document_classifier:
        raise HTTPException(status_code=500, detail="Document classifier not initialized")
    
    try:
        categories = document_classifier.list_categories()
        category_info = {}
        
        for category in categories:
            category_info[category] = document_classifier.get_category_info(category)
        
        return {
            "categories": categories,
            "category_info": category_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving categories: {str(e)}")

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 