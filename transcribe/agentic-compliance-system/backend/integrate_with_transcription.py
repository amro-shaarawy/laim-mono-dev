"""
Integration Helper for Existing Transcription System

This module provides easy integration functions that you can add to your existing
transcription system (live.py, app.py, etc.) to enable real-time compliance monitoring.
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplianceMonitor:
    """
    Simple compliance monitoring integration for existing transcription systems.
    
    Usage:
        # In your existing transcription system
        monitor = ComplianceMonitor("http://localhost:8000")
        
        # Process transcript segments as they come in
        await monitor.process_segment("Speaker_1", "We should use creative accounting...")
    """
    
    def __init__(self, backend_url: str = "http://localhost:8000", 
                 alert_callback: Optional[Callable] = None):
        self.backend_url = backend_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.alert_callback = alert_callback
        self.websocket: Optional[aiohttp.ClientWebSocketResponse] = None
        self._connected = False
    
    async def start(self):
        """Initialize the compliance monitor"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Test connection
            async with self.session.get(f"{self.backend_url}/health") as response:
                if response.status == 200:
                    logger.info("✅ Connected to compliance monitoring system")
                    self._connected = True
                    
                    # Start WebSocket connection for alerts
                    await self._connect_websocket()
                else:
                    logger.error("❌ Failed to connect to compliance system")
                    self._connected = False
                    
        except Exception as e:
            logger.error(f"❌ Error starting compliance monitor: {e}")
            self._connected = False
    
    async def stop(self):
        """Stop the compliance monitor"""
        if self.websocket:
            await self.websocket.close()
        if self.session:
            await self.session.close()
        self._connected = False
        logger.info("🛑 Compliance monitor stopped")
    
    async def _connect_websocket(self):
        """Connect to WebSocket for real-time alerts"""
        try:
            ws_url = self.backend_url.replace("http", "ws") + "/ws"
            self.websocket = await self.session.ws_connect(ws_url)
            logger.info("✅ Connected to WebSocket for real-time alerts")
            
            # Start listening for alerts in background
            asyncio.create_task(self._listen_for_alerts())
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to WebSocket: {e}")
    
    async def _listen_for_alerts(self):
        """Listen for real-time alerts"""
        if not self.websocket:
            return
        
        try:
            async for msg in self.websocket:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    if data.get("type") == "compliance_alert":
                        alert = data.get("data", {})
                        await self._handle_alert(alert)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {self.websocket.exception()}")
                    break
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
    
    async def _handle_alert(self, alert: Dict[str, Any]):
        """Handle incoming compliance alerts"""
        severity = alert.get("severity", "low")
        message = alert.get("message", "Unknown alert")
        speaker_id = alert.get("speaker_id", "Unknown")
        
        # Log the alert
        logger.warning(f"🚨 COMPLIANCE ALERT - {severity.upper()}: {message} (Speaker: {speaker_id})")
        
        # Call custom callback if provided
        if self.alert_callback:
            try:
                await self.alert_callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    async def process_segment(self, speaker_id: str, content: str, 
                            timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a transcript segment for compliance violations.
        
        Args:
            speaker_id: Identifier for the speaker
            content: The transcript content to analyze
            timestamp: Optional timestamp (defaults to current time)
        
        Returns:
            Dict containing processing results
        """
        if not self._connected:
            logger.warning("⚠️ Compliance monitor not connected, skipping processing")
            return {"error": "Not connected"}
        
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
                logger.info(f"📝 Processed transcript segment for {speaker_id}")
                return result
        except Exception as e:
            logger.error(f"❌ Error processing transcript: {e}")
            return {"error": str(e)}
    
    async def upload_document(self, title: str, content: str, 
                            category: str = "general") -> Dict[str, Any]:
        """
        Upload a regulatory document to the compliance system.
        
        Args:
            title: Document title
            content: Document content
            category: Compliance category (esg, financial, legal, etc.)
        
        Returns:
            Dict containing upload results
        """
        if not self._connected:
            logger.warning("⚠️ Compliance monitor not connected, skipping upload")
            return {"error": "Not connected"}
        
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
                logger.info(f"📄 Uploaded document: {title}")
                return result
        except Exception as e:
            logger.error(f"❌ Error uploading document: {e}")
            return {"error": str(e)}
    
    def is_connected(self) -> bool:
        """Check if the compliance monitor is connected"""
        return self._connected

# Integration functions for your existing transcription system

async def setup_compliance_monitoring(backend_url: str = "http://localhost:8000",
                                    alert_callback: Optional[Callable] = None) -> ComplianceMonitor:
    """
    Set up compliance monitoring for your transcription system.
    
    Usage in your existing system:
        # At the start of your transcription system
        monitor = await setup_compliance_monitoring()
        
        # In your transcription loop
        await monitor.process_segment("Speaker_1", transcript_text)
    """
    monitor = ComplianceMonitor(backend_url, alert_callback)
    await monitor.start()
    return monitor

def create_alert_callback(display_function: Optional[Callable] = None):
    """
    Create a custom alert callback function.
    
    Args:
        display_function: Function to display alerts (e.g., print, UI update, etc.)
    
    Returns:
        Callback function for handling alerts
    """
    async def alert_callback(alert: Dict[str, Any]):
        severity = alert.get("severity", "low")
        message = alert.get("message", "Unknown alert")
        speaker_id = alert.get("speaker_id", "Unknown")
        
        # Default display
        if display_function:
            display_function(alert)
        else:
            # Simple console display
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
    
    return alert_callback

# Example integration with your existing live.py
"""
# Add this to your existing live.py or app.py

import asyncio
from integrate_with_transcription import setup_compliance_monitoring, create_alert_callback

# Create alert callback
def display_alert(alert):
    # Custom alert display logic
    print(f"🚨 {alert['message']}")

alert_callback = create_alert_callback(display_alert)

# In your main function or transcription loop:
async def main():
    # Set up compliance monitoring
    monitor = await setup_compliance_monitoring(alert_callback=alert_callback)
    
    # Your existing transcription code here...
    # When you get a transcript segment:
    transcript = "We should use creative accounting methods..."
    await monitor.process_segment("Speaker_1", transcript)
    
    # Don't forget to stop when done
    await monitor.stop()

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
"""

# Example integration with your existing app.py (Gradio)
"""
# Add this to your existing app.py

import asyncio
from integrate_with_transcription import setup_compliance_monitoring

# Global variable for the monitor
compliance_monitor = None

async def setup_compliance():
    global compliance_monitor
    compliance_monitor = await setup_compliance_monitoring()

# In your translation function:
async def handle_translation(audio_file, target_language):
    # Your existing translation code...
    translated_text = translator.translate_audio(audio_file)
    
    # Add compliance monitoring
    if compliance_monitor and compliance_monitor.is_connected():
        await compliance_monitor.process_segment("User", translated_text)
    
    return translated_text

# Set up compliance monitoring when the app starts
if __name__ == "__main__":
    # Set up compliance monitoring
    asyncio.run(setup_compliance())
    
    # Your existing Gradio app code...
    interface.launch()
""" 