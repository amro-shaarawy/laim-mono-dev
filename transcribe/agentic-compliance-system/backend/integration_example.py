"""
Integration Example: Connecting Transcription System with Compliance Monitoring

This script demonstrates how to integrate your existing real-time transcription system
with the new CrewAI-based compliance monitoring system.
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class ComplianceIntegration:
    """Integration class for connecting transcription with compliance monitoring"""
    
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket: Optional[aiohttp.ClientWebSocketResponse] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        if self.websocket:
            await self.websocket.close()
    
    async def connect_websocket(self):
        """Connect to WebSocket for real-time alerts"""
        try:
            ws_url = self.backend_url.replace("http", "ws") + "/ws"
            self.websocket = await self.session.ws_connect(ws_url)
            print("✅ Connected to WebSocket for real-time alerts")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to WebSocket: {e}")
            return False
    
    async def process_transcript_segment(self, speaker_id: str, content: str, timestamp: Optional[str] = None) -> Dict[str, Any]:
        """Process a transcript segment for compliance violations"""
        if not timestamp:
            timestamp = datetime.now().isoformat()
        
        payload = {
            "speaker_id": speaker_id,
            "timestamp": timestamp,
            "content": content
        }
        
        try:
            async with self.session.post(
                f"{self.backend_url}/api/process-transcript",
                json=payload
            ) as response:
                result = await response.json()
                print(f"📝 Processed transcript segment: {result}")
                return result
        except Exception as e:
            print(f"❌ Error processing transcript: {e}")
            return {"error": str(e)}
    
    async def upload_document(self, title: str, content: str, category: str = "general") -> Dict[str, Any]:
        """Upload a regulatory document"""
        payload = {
            "title": title,
            "content": content,
            "category": category
        }
        
        try:
            async with self.session.post(
                f"{self.backend_url}/api/upload-document",
                json=payload
            ) as response:
                result = await response.json()
                print(f"📄 Uploaded document: {result}")
                return result
        except Exception as e:
            print(f"❌ Error uploading document: {e}")
            return {"error": str(e)}
    
    async def get_alerts(self, severity: Optional[str] = None, speaker_id: Optional[str] = None) -> Dict[str, Any]:
        """Get compliance alerts"""
        params = {}
        if severity:
            params["severity"] = severity
        if speaker_id:
            params["speaker_id"] = speaker_id
        
        try:
            async with self.session.get(
                f"{self.backend_url}/api/alerts",
                params=params
            ) as response:
                result = await response.json()
                return result
        except Exception as e:
            print(f"❌ Error getting alerts: {e}")
            return {"error": str(e)}
    
    async def listen_for_alerts(self):
        """Listen for real-time alerts via WebSocket"""
        if not self.websocket:
            print("❌ WebSocket not connected")
            return
        
        try:
            async for msg in self.websocket:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if data.get("type") == "compliance_alert":
                        alert = data.get("data", {})
                        await self.handle_alert(alert)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print(f"WebSocket error: {self.websocket.exception()}")
                    break
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
    
    async def handle_alert(self, alert: Dict[str, Any]):
        """Handle incoming compliance alerts"""
        severity = alert.get("severity", "low")
        message = alert.get("message", "Unknown alert")
        speaker_id = alert.get("speaker_id", "Unknown")
        
        # Color-coded alert display
        severity_colors = {
            "critical": "🔴",
            "high": "🟠", 
            "medium": "🟡",
            "low": "🟢"
        }
        
        color = severity_colors.get(severity, "⚪")
        print(f"\n{color} COMPLIANCE ALERT {color}")
        print(f"Speaker: {speaker_id}")
        print(f"Severity: {severity.upper()}")
        print(f"Message: {message}")
        print(f"Time: {alert.get('timestamp', 'Unknown')}")
        
        if alert.get("action_required"):
            print("⚠️  ACTION REQUIRED")
            for action in alert.get("action_items", []):
                print(f"   • {action}")
        print("-" * 50)

# Example integration with your existing transcription system
async def integrate_with_transcription():
    """Example of integrating with your existing transcription system"""
    
    # Sample regulatory documents to upload
    sample_documents = [
        {
            "title": "Financial Reporting Standards",
            "content": "All financial statements must be prepared in accordance with Generally Accepted Accounting Principles (GAAP). Any creative accounting methods or manipulation of financial data is strictly prohibited and may result in legal action.",
            "category": "financial"
        },
        {
            "title": "Environmental Compliance Policy",
            "content": "The company is committed to environmental sustainability. All operations must comply with environmental regulations. Carbon emissions must be reported accurately and any environmental violations must be immediately reported to management.",
            "category": "esg"
        },
        {
            "title": "Ethical Business Conduct",
            "content": "All employees must maintain the highest ethical standards. Bribery, corruption, and conflicts of interest are strictly prohibited. Any ethical concerns must be reported through the appropriate channels.",
            "category": "ethical"
        }
    ]
    
    # Sample transcript segments (simulating your real-time transcription)
    sample_transcripts = [
        {
            "speaker_id": "CEO",
            "content": "We need to improve our quarterly results. Maybe we can use some creative accounting methods to make the numbers look better.",
            "expected_violation": "financial"
        },
        {
            "speaker_id": "CFO", 
            "content": "I understand the pressure, but we must follow GAAP standards. Any manipulation could result in serious legal consequences.",
            "expected_violation": None
        },
        {
            "speaker_id": "Operations Manager",
            "content": "We can save money by not reporting some of our carbon emissions. No one will notice anyway.",
            "expected_violation": "esg"
        },
        {
            "speaker_id": "Sales Director",
            "content": "I have a contact who can help us win this contract. We might need to offer some incentives under the table.",
            "expected_violation": "ethical"
        }
    ]
    
    async with ComplianceIntegration() as integration:
        # Connect to WebSocket for real-time alerts
        await integration.connect_websocket()
        
        # Start listening for alerts in background
        alert_task = asyncio.create_task(integration.listen_for_alerts())
        
        print("📚 Uploading sample regulatory documents...")
        
        # Upload sample documents
        for doc in sample_documents:
            await integration.upload_document(
                title=doc["title"],
                content=doc["content"],
                category=doc["category"]
            )
            await asyncio.sleep(1)  # Small delay between uploads
        
        print("\n🎙️ Processing sample transcript segments...")
        
        # Process sample transcript segments
        for transcript in sample_transcripts:
            print(f"\n📝 Processing: {transcript['speaker_id']} - '{transcript['content']}'")
            
            result = await integration.process_transcript_segment(
                speaker_id=transcript["speaker_id"],
                content=transcript["content"]
            )
            
            if transcript["expected_violation"]:
                print(f"Expected violation type: {transcript['expected_violation']}")
            
            await asyncio.sleep(2)  # Delay between segments
        
        # Wait a bit for processing
        print("\n⏳ Waiting for processing to complete...")
        await asyncio.sleep(5)
        
        # Get all alerts
        print("\n📊 Retrieving all alerts...")
        alerts = await integration.get_alerts()
        print(f"Total alerts: {alerts.get('total_count', 0)}")
        
        # Cancel the alert listening task
        alert_task.cancel()
        try:
            await alert_task
        except asyncio.CancelledError:
            pass

# Example of integrating with your existing live transcription system
async def integrate_with_live_transcription():
    """Example of integrating with your existing live transcription system"""
    
    async with ComplianceIntegration() as integration:
        # Connect to WebSocket
        await integration.connect_websocket()
        
        # Start listening for alerts
        alert_task = asyncio.create_task(integration.listen_for_alerts())
        
        print("🎙️ Live transcription integration example")
        print("This simulates how you would integrate with your existing transcription system")
        print("Press Ctrl+C to stop")
        
        try:
            # Simulate real-time transcript processing
            while True:
                # In your real system, this would come from your transcription pipeline
                # For example, from your existing live.py or app.py
                
                # Simulate receiving transcript segments
                sample_segments = [
                    ("Speaker_1", "We should consider some creative accounting methods."),
                    ("Speaker_2", "That would violate our compliance policies."),
                    ("Speaker_3", "Maybe we can offer some incentives to win this contract."),
                ]
                
                for speaker_id, content in sample_segments:
                    print(f"\n🎤 {speaker_id}: {content}")
                    
                    # Process the segment for compliance violations
                    await integration.process_transcript_segment(
                        speaker_id=speaker_id,
                        content=content
                    )
                    
                    await asyncio.sleep(3)  # Simulate real-time processing
                
                await asyncio.sleep(10)  # Wait before next batch
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping live transcription integration")
        finally:
            alert_task.cancel()
            try:
                await alert_task
            except asyncio.CancelledError:
                pass

if __name__ == "__main__":
    print("🚀 Agentic AI Compliance System Integration Examples")
    print("=" * 60)
    
    # Run the integration example
    asyncio.run(integrate_with_transcription())
    
    print("\n" + "=" * 60)
    print("Live transcription integration example:")
    print("Uncomment the line below to run the live integration example")
    # asyncio.run(integrate_with_live_transcription()) 