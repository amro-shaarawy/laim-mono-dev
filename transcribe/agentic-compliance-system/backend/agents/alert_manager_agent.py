from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any, Optional, Callable
import json
from pydantic import BaseModel
from datetime import datetime
import asyncio
from enum import Enum

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(str, Enum):
    """Alert types"""
    COMPLIANCE_VIOLATION = "compliance_violation"
    POLICY_BREACH = "policy_breach"
    REGULATORY_RISK = "regulatory_risk"
    ETHICAL_CONCERN = "ethical_concern"
    OPERATIONAL_ISSUE = "operational_issue"

class ComplianceAlert(BaseModel):
    """Model for compliance alerts"""
    id: str
    speaker_id: str
    timestamp: str
    transcript_segment: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    matched_document: Optional[str] = None
    confidence_score: float
    context: Optional[str] = None
    action_required: bool = False
    action_items: List[str] = []
    created_at: str
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[str] = None

class AlertManagerAgent:
    """Alert management agent using CrewAI"""
    
    def __init__(self, openai_api_key: str, alert_callback: Optional[Callable] = None):
        self.openai_api_key = openai_api_key
        self.alert_callback = alert_callback
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model="gpt-4o-mini",
            temperature=0.1
        )
        
        # Create CrewAI agents
        self._create_agents()
        
        # Alert storage (in production, this would be a database)
        self.alerts: List[ComplianceAlert] = []
        self.alert_counter = 0
        
        # Alert thresholds and filters
        self.severity_thresholds = {
            AlertSeverity.LOW: 0.6,
            AlertSeverity.MEDIUM: 0.7,
            AlertSeverity.HIGH: 0.8,
            AlertSeverity.CRITICAL: 0.9
        }
        
        # Alert suppression settings
        self.suppress_duplicates = True
        self.duplicate_time_window = 300  # 5 minutes
        self.max_alerts_per_speaker = 10  # per session
    
    def _create_agents(self):
        """Create the CrewAI agents for alert management"""
        
        # Alert Assessment Agent
        self.alert_assessor = Agent(
            role="Alert Assessment Specialist",
            goal="Assess compliance violations and determine appropriate alert severity and type",
            backstory="""You are an expert in compliance risk assessment and alert management. 
            You can quickly evaluate the severity of compliance issues and determine the appropriate 
            level of alert needed for board members and compliance officers.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self._assess_violation_tool]
        )
        
        # Alert Formulation Agent
        self.alert_formulator = Agent(
            role="Alert Formulation Expert",
            goal="Create clear, actionable alert messages suitable for board-level communication",
            backstory="""You are an expert in risk communication and alert formulation. 
            You create clear, concise, and actionable alerts that help decision-makers understand 
            compliance risks without causing unnecessary alarm or confusion.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self._formulate_alert_tool]
        )
        
        # Action Planning Agent
        self.action_planner = Agent(
            role="Action Planning Specialist",
            goal="Determine required actions and next steps for compliance violations",
            backstory="""You are an expert in compliance remediation and action planning. 
            You can identify the specific actions needed to address compliance violations 
            and provide clear guidance on next steps.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self._plan_actions_tool]
        )
    
    def _assess_violation_tool(self, violation_data: str) -> str:
        """Tool for assessing violation severity and type"""
        try:
            data = json.loads(violation_data)
            
            assessment = {
                "severity": AlertSeverity.LOW.value,
                "alert_type": AlertType.COMPLIANCE_VIOLATION.value,
                "confidence": data.get("confidence_score", 0.0),
                "risk_factors": [],
                "business_impact": "minimal"
            }
            
            # Assess severity based on confidence and content
            confidence = data.get("confidence_score", 0.0)
            transcript = data.get("transcript_segment", "").lower()
            
            # Determine severity based on confidence and keywords
            if confidence >= 0.9 or any(word in transcript for word in ["fraud", "criminal", "illegal", "bribery"]):
                assessment["severity"] = AlertSeverity.CRITICAL.value
                assessment["business_impact"] = "severe"
            elif confidence >= 0.8 or any(word in transcript for word in ["violation", "breach", "prohibited", "penalty"]):
                assessment["severity"] = AlertSeverity.HIGH.value
                assessment["business_impact"] = "significant"
            elif confidence >= 0.7 or any(word in transcript for word in ["risk", "concern", "issue", "non-compliance"]):
                assessment["severity"] = AlertSeverity.MEDIUM.value
                assessment["business_impact"] = "moderate"
            
            # Determine alert type based on content
            if any(word in transcript for word in ["ethical", "integrity", "conflict"]):
                assessment["alert_type"] = AlertType.ETHICAL_CONCERN.value
            elif any(word in transcript for word in ["financial", "accounting", "audit"]):
                assessment["alert_type"] = AlertType.REGULATORY_RISK.value
            elif any(word in transcript for word in ["policy", "procedure", "guideline"]):
                assessment["alert_type"] = AlertType.POLICY_BREACH.value
            elif any(word in transcript for word in ["operational", "safety", "security"]):
                assessment["alert_type"] = AlertType.OPERATIONAL_ISSUE.value
            
            # Identify risk factors
            risk_keywords = ["penalty", "fine", "legal action", "reputation", "regulatory"]
            assessment["risk_factors"] = [word for word in risk_keywords if word in transcript]
            
            return json.dumps(assessment)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _formulate_alert_tool(self, assessment_data: str) -> str:
        """Tool for formulating alert messages"""
        try:
            assessment = json.loads(assessment_data)
            
            # Create alert message based on severity and type
            severity = assessment.get("severity", AlertSeverity.LOW.value)
            alert_type = assessment.get("alert_type", AlertType.COMPLIANCE_VIOLATION.value)
            business_impact = assessment.get("business_impact", "minimal")
            
            # Generate appropriate message based on severity
            if severity == AlertSeverity.CRITICAL.value:
                message = f"🚨 CRITICAL: {alert_type.replace('_', ' ').title()} detected. Immediate attention required."
            elif severity == AlertSeverity.HIGH.value:
                message = f"⚠️ HIGH: {alert_type.replace('_', ' ').title()} identified. Review needed."
            elif severity == AlertSeverity.MEDIUM.value:
                message = f"📋 MEDIUM: {alert_type.replace('_', ' ').title()} noted. Monitor closely."
            else:
                message = f"ℹ️ LOW: {alert_type.replace('_', ' ').title()} observed. For awareness."
            
            # Add business impact information
            message += f" Business impact: {business_impact}."
            
            formulation = {
                "message": message,
                "tone": "professional",
                "urgency": severity,
                "clarity_score": 0.9
            }
            
            return json.dumps(formulation)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _plan_actions_tool(self, alert_data: str) -> str:
        """Tool for planning required actions"""
        try:
            data = json.loads(alert_data)
            
            severity = data.get("severity", AlertSeverity.LOW.value)
            alert_type = data.get("alert_type", AlertType.COMPLIANCE_VIOLATION.value)
            
            actions = []
            action_required = False
            
            # Determine actions based on severity and type
            if severity in [AlertSeverity.CRITICAL.value, AlertSeverity.HIGH.value]:
                action_required = True
                actions.extend([
                    "Immediate review of the violation",
                    "Consult with legal/compliance team",
                    "Document the incident",
                    "Assess potential regulatory impact"
                ])
                
                if severity == AlertSeverity.CRITICAL.value:
                    actions.extend([
                        "Notify senior management immediately",
                        "Consider external legal counsel",
                        "Prepare regulatory notification if required"
                    ])
            
            elif severity == AlertSeverity.MEDIUM.value:
                action_required = True
                actions.extend([
                    "Review the compliance concern",
                    "Monitor for similar issues",
                    "Update relevant policies if needed"
                ])
            
            else:  # LOW severity
                actions = ["Monitor for escalation", "Document for future reference"]
            
            # Add type-specific actions
            if alert_type == AlertType.ETHICAL_CONCERN.value:
                actions.append("Review ethical guidelines and training")
            elif alert_type == AlertType.FINANCIAL.value:
                actions.append("Review financial controls and procedures")
            elif alert_type == AlertType.OPERATIONAL_ISSUE.value:
                actions.append("Review operational procedures and safety protocols")
            
            action_plan = {
                "action_required": action_required,
                "actions": actions,
                "priority": severity,
                "timeline": "immediate" if severity in [AlertSeverity.CRITICAL.value, AlertSeverity.HIGH.value] else "within 24 hours"
            }
            
            return json.dumps(action_plan)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def process_violation(self, violation_data: Dict[str, Any]) -> Optional[ComplianceAlert]:
        """Process a compliance violation and generate an alert"""
        
        # Check if we should suppress this alert
        if self._should_suppress_alert(violation_data):
            return None
        
        # Create tasks for the crew
        assessment_task = Task(
            description=f"""
            Assess the following compliance violation:
            Speaker: {violation_data.get('speaker_id', 'Unknown')}
            Time: {violation_data.get('timestamp', 'Unknown')}
            Content: "{violation_data.get('transcript_segment', '')}"
            Confidence: {violation_data.get('confidence_score', 0.0)}
            
            Determine severity level, alert type, and business impact.
            """,
            agent=self.alert_assessor,
            expected_output="JSON with violation assessment"
        )
        
        formulation_task = Task(
            description=f"""
            Based on the assessment, formulate a clear alert message suitable for board members.
            Ensure the message is professional, clear, and actionable.
            """,
            agent=self.alert_formulator,
            expected_output="JSON with alert formulation"
        )
        
        action_task = Task(
            description=f"""
            Determine required actions and next steps for this compliance violation.
            Consider the severity and type when planning actions.
            """,
            agent=self.action_planner,
            expected_output="JSON with action plan"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[self.alert_assessor, self.alert_formulator, self.action_planner],
            tasks=[assessment_task, formulation_task, action_task],
            verbose=True
        )
        
        try:
            result = await crew.kickoff()
            
            # Create the alert
            alert = ComplianceAlert(
                id=f"alert_{self.alert_counter}",
                speaker_id=violation_data.get('speaker_id', 'Unknown'),
                timestamp=violation_data.get('timestamp', datetime.now().isoformat()),
                transcript_segment=violation_data.get('transcript_segment', ''),
                alert_type=AlertType(result.get('alert_type', AlertType.COMPLIANCE_VIOLATION.value)),
                severity=AlertSeverity(result.get('severity', AlertSeverity.LOW.value)),
                message=result.get('message', 'Compliance issue detected'),
                matched_document=violation_data.get('matched_document'),
                confidence_score=violation_data.get('confidence_score', 0.0),
                context=violation_data.get('context'),
                action_required=result.get('action_required', False),
                action_items=result.get('actions', []),
                created_at=datetime.now().isoformat()
            )
            
            # Store the alert
            self.alerts.append(alert)
            self.alert_counter += 1
            
            # Send alert to frontend if callback is provided
            if self.alert_callback:
                await self.alert_callback(alert)
            
            return alert
            
        except Exception as e:
            print(f"Error processing violation: {e}")
            return None
    
    def _should_suppress_alert(self, violation_data: Dict[str, Any]) -> bool:
        """Check if an alert should be suppressed based on various criteria"""
        
        # Check severity threshold
        confidence = violation_data.get('confidence_score', 0.0)
        if confidence < self.severity_thresholds[AlertSeverity.LOW]:
            return True
        
        # Check for duplicates if suppression is enabled
        if self.suppress_duplicates:
            speaker_id = violation_data.get('speaker_id', '')
            transcript = violation_data.get('transcript_segment', '')
            current_time = datetime.now()
            
            # Check recent alerts from the same speaker
            recent_alerts = [
                alert for alert in self.alerts
                if alert.speaker_id == speaker_id and
                (current_time - datetime.fromisoformat(alert.created_at)).seconds < self.duplicate_time_window
            ]
            
            # Check for similar content
            for alert in recent_alerts:
                if self._is_similar_content(transcript, alert.transcript_segment):
                    return True
        
        # Check maximum alerts per speaker
        speaker_id = violation_data.get('speaker_id', '')
        speaker_alert_count = len([alert for alert in self.alerts if alert.speaker_id == speaker_id])
        if speaker_alert_count >= self.max_alerts_per_speaker:
            return True
        
        return False
    
    def _is_similar_content(self, content1: str, content2: str, threshold: float = 0.8) -> bool:
        """Check if two content pieces are similar"""
        # Simple similarity check - in production, use more sophisticated NLP
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union)
        return similarity >= threshold
    
    def get_alerts(self, 
                   severity_filter: Optional[AlertSeverity] = None,
                   speaker_filter: Optional[str] = None,
                   time_range_minutes: Optional[int] = None) -> List[ComplianceAlert]:
        """Get filtered alerts"""
        filtered_alerts = self.alerts.copy()
        
        # Apply severity filter
        if severity_filter:
            filtered_alerts = [alert for alert in filtered_alerts if alert.severity == severity_filter]
        
        # Apply speaker filter
        if speaker_filter:
            filtered_alerts = [alert for alert in filtered_alerts if alert.speaker_id == speaker_filter]
        
        # Apply time range filter
        if time_range_minutes:
            cutoff_time = datetime.now().timestamp() - (time_range_minutes * 60)
            filtered_alerts = [
                alert for alert in filtered_alerts
                if datetime.fromisoformat(alert.created_at).timestamp() > cutoff_time
            ]
        
        return filtered_alerts
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now().isoformat()
                return True
        return False
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get statistics about alerts"""
        total_alerts = len(self.alerts)
        severity_counts = {severity.value: 0 for severity in AlertSeverity}
        type_counts = {alert_type.value: 0 for alert_type in AlertType}
        
        for alert in self.alerts:
            severity_counts[alert.severity.value] += 1
            type_counts[alert.alert_type.value] += 1
        
        return {
            "total_alerts": total_alerts,
            "severity_distribution": severity_counts,
            "type_distribution": type_counts,
            "acknowledged_count": len([alert for alert in self.alerts if alert.acknowledged]),
            "pending_count": len([alert for alert in self.alerts if not alert.acknowledged])
        } 