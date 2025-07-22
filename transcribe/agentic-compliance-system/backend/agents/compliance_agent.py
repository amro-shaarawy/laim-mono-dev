from crewai import Agent, Task, Crew
from crewai.llms import Gemini
import pinecone
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import asyncio
from pydantic import BaseModel
import google.generativeai as genai

class ComplianceViolation(BaseModel):
    """Model for compliance violation alerts"""
    speaker_id: str
    timestamp: str
    transcript_segment: str
    violation_type: str
    severity: str  # "low", "medium", "high", "critical"
    matched_document: Optional[str] = None
    confidence_score: float
    context: Optional[str] = None

class ComplianceAgent:
    """Real-time compliance monitoring agent using CrewAI"""
    
    def __init__(self, pinecone_api_key: str, pinecone_index_name: str, gemini_api_key: str):
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_index_name = pinecone_index_name
        self.gemini_api_key = gemini_api_key
        
        # Initialize Pinecone
        pinecone.init(api_key=pinecone_api_key, environment="gcp-starter")
        self.index = pinecone.Index(pinecone_index_name)
        
        # Initialize Gemini
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize LLM for CrewAI
        self.llm = Gemini(
            api_key=gemini_api_key,
            model="gemini-1.5-flash",
            temperature=0.1
        )
        
        # Create CrewAI agents
        self._create_agents()
        
        # Compliance categories and their keywords
        self.compliance_categories = {
            "esg": ["environmental", "social", "governance", "sustainability", "carbon", "emissions", "diversity", "inclusion"],
            "financial": ["financial", "accounting", "audit", "revenue", "expenses", "profit", "loss", "tax"],
            "legal": ["legal", "compliance", "regulation", "law", "contract", "liability", "risk"],
            "ethical": ["ethical", "conflict", "interest", "bribery", "corruption", "whistleblower"],
            "operational": ["operational", "safety", "security", "quality", "standards", "procedures"]
        }
    
    def _create_agents(self):
        """Create the CrewAI agents for compliance monitoring"""
        
        # Compliance Analysis Agent
        self.compliance_analyst = Agent(
            role="Compliance Analyst",
            goal="Analyze transcript segments for potential compliance violations by comparing against regulatory documents",
            backstory="""You are an expert compliance analyst with deep knowledge of ESG, financial, legal, and ethical regulations. 
            You specialize in identifying potential violations in real-time conversations by matching content against stored regulatory documents.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self._analyze_compliance_tool]
        )
        
        # Alert Generation Agent
        self.alert_generator = Agent(
            role="Alert Generator",
            goal="Generate clear, actionable compliance alerts with appropriate severity levels",
            backstory="""You are an expert in risk communication and alert generation. You create clear, 
            actionable alerts that help board members understand compliance risks without causing unnecessary alarm.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self._generate_alert_tool]
        )
        
        # Context Analysis Agent
        self.context_analyzer = Agent(
            role="Context Analyzer",
            goal="Analyze the broader context of potential violations to determine severity and relevance",
            backstory="""You are an expert in understanding business context and determining the real-world 
            implications of potential compliance issues. You help distinguish between minor infractions and serious violations.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self._analyze_context_tool]
        )
    
    def _analyze_compliance_tool(self, transcript_segment: str, speaker_id: str, timestamp: str) -> str:
        """Tool for analyzing compliance in transcript segments"""
        try:
            # Search for relevant documents in Pinecone
            # Get embeddings for the transcript segment
            transcript_embedding = self._get_embedding(transcript_segment)
            
            # Query Pinecone
            query_response = self.index.query(
                vector=transcript_embedding,
                top_k=5,
                include_metadata=True
            )
            
            # Filter documents by relevance threshold
            relevant_docs = []
            for match in query_response.matches:
                if match.score > 0.7:  # Adjust threshold as needed
                    relevant_docs.append({
                        "content": match.metadata.get("content", ""),
                        "title": match.metadata.get("title", "Unknown"),
                        "score": match.score
                    })
            
            if not relevant_docs:
                return json.dumps({
                    "violation_detected": False,
                    "reason": "No relevant regulatory documents found"
                })
            
            # Analyze each relevant document
            violations = []
            for doc in relevant_docs:
                analysis = self._analyze_document_compliance(
                    transcript_segment, doc["content"], doc["score"]
                )
                if analysis["is_violation"]:
                    analysis["document_title"] = doc["title"]
                    violations.append(analysis)
            
            return json.dumps({
                "violation_detected": len(violations) > 0,
                "violations": violations,
                "speaker_id": speaker_id,
                "timestamp": timestamp
            })
            
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "violation_detected": False
            })
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using Gemini"""
        try:
            embedding_model = genai.GenerativeModel('embedding-001')
            result = embedding_model.embed_content(text)
            return result.embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return a dummy embedding if there's an error
            return [0.0] * 768
    
    def _generate_alert_tool(self, violation_data: str) -> str:
        """Tool for generating formatted alerts"""
        try:
            data = json.loads(violation_data)
            
            if not data.get("violation_detected", False):
                return json.dumps({"alert": None})
            
            violations = data.get("violations", [])
            alerts = []
            
            for violation in violations:
                alert = {
                    "speaker_id": data.get("speaker_id"),
                    "timestamp": data.get("timestamp"),
                    "severity": violation.get("severity", "medium"),
                    "violation_type": violation.get("type", "compliance"),
                    "message": violation.get("description", "Potential compliance issue detected"),
                    "confidence": violation.get("confidence", 0.0),
                    "matched_document": violation.get("document_title", "Unknown"),
                    "context": violation.get("context", "")
                }
                alerts.append(alert)
            
            return json.dumps({"alerts": alerts})
            
        except Exception as e:
            return json.dumps({"error": str(e), "alert": None})
    
    def _analyze_context_tool(self, transcript_segment: str, violation_type: str) -> str:
        """Tool for analyzing context and determining severity"""
        try:
            # Analyze the context to determine severity
            context_analysis = {
                "severity": "low",
                "context": "",
                "business_impact": "minimal"
            }
            
            # Simple keyword-based severity analysis
            high_severity_keywords = ["fraud", "bribery", "corruption", "illegal", "criminal", "violation"]
            medium_severity_keywords = ["risk", "concern", "issue", "problem", "non-compliance"]
            
            segment_lower = transcript_segment.lower()
            
            if any(keyword in segment_lower for keyword in high_severity_keywords):
                context_analysis["severity"] = "high"
                context_analysis["business_impact"] = "significant"
            elif any(keyword in segment_lower for keyword in medium_severity_keywords):
                context_analysis["severity"] = "medium"
                context_analysis["business_impact"] = "moderate"
            
            context_analysis["context"] = f"Analysis of '{transcript_segment}' for {violation_type} compliance"
            
            return json.dumps(context_analysis)
            
        except Exception as e:
            return json.dumps({"error": str(e), "severity": "low"})
    
    def _analyze_document_compliance(self, transcript: str, document_content: str, similarity_score: float) -> Dict[str, Any]:
        """Analyze compliance between transcript and document using Gemini"""
        try:
            prompt = f"""
            Analyze the following transcript segment against the regulatory document content:
            
            Transcript: "{transcript}"
            Document: "{document_content[:500]}..."
            Similarity Score: {similarity_score}
            
            Determine if this represents a potential compliance violation. Consider:
            1. Does the transcript content contradict or violate the document's requirements?
            2. What is the severity level (low/medium/high/critical)?
            3. What type of compliance issue is this?
            
            Return a JSON response with:
            - is_violation: boolean
            - type: string (esg/financial/legal/ethical/operational)
            - severity: string (low/medium/high/critical)
            - description: string
            - confidence: float (0-1)
            """
            
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text
            
            # Try to parse JSON from response
            try:
                # Extract JSON from response if it's wrapped in markdown
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                else:
                    json_str = response_text.strip()
                
                result = json.loads(json_str)
                return result
            except json.JSONDecodeError:
                # Fallback to simple analysis
                return {
                    "is_violation": similarity_score > 0.8,
                    "type": "compliance",
                    "severity": "medium" if similarity_score > 0.8 else "low",
                    "description": f"Potential compliance issue with similarity score {similarity_score:.2f}",
                    "confidence": similarity_score
                }
                
        except Exception as e:
            return {
                "is_violation": False,
                "type": "unknown",
                "severity": "low",
                "description": f"Analysis error: {str(e)}",
                "confidence": 0.0
            }
    
    async def process_transcript_segment(self, transcript: str, speaker_id: str, timestamp: str) -> List[ComplianceViolation]:
        """Process a transcript segment for compliance violations"""
        
        # Create tasks for the crew
        analysis_task = Task(
            description=f"""
            Analyze the following transcript segment for compliance violations:
            Speaker: {speaker_id}
            Time: {timestamp}
            Content: "{transcript}"
            
            Search the vector database for relevant regulatory documents and determine if there are any compliance issues.
            """,
            agent=self.compliance_analyst,
            expected_output="JSON with violation analysis results"
        )
        
        context_task = Task(
            description=f"""
            If violations are detected, analyze the context and determine severity levels.
            Consider business impact and real-world implications.
            """,
            agent=self.context_analyzer,
            expected_output="JSON with context analysis and severity assessment"
        )
        
        alert_task = Task(
            description=f"""
            Generate clear, actionable alerts for any detected violations.
            Include speaker ID, timestamp, severity, and specific violation details.
            """,
            agent=self.alert_generator,
            expected_output="JSON with formatted alerts"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[self.compliance_analyst, self.context_analyzer, self.alert_generator],
            tasks=[analysis_task, context_task, alert_task],
            verbose=True
        )
        
        try:
            result = await crew.kickoff()
            
            # Parse the result and convert to ComplianceViolation objects
            violations = []
            
            # Extract alerts from the result
            # This is a simplified parsing - you might need to adjust based on actual output format
            if "alerts" in result:
                for alert_data in result["alerts"]:
                    violation = ComplianceViolation(
                        speaker_id=alert_data.get("speaker_id", speaker_id),
                        timestamp=alert_data.get("timestamp", timestamp),
                        transcript_segment=transcript,
                        violation_type=alert_data.get("violation_type", "compliance"),
                        severity=alert_data.get("severity", "medium"),
                        matched_document=alert_data.get("matched_document"),
                        confidence_score=alert_data.get("confidence", 0.0),
                        context=alert_data.get("context")
                    )
                    violations.append(violation)
            
            return violations
            
        except Exception as e:
            print(f"Error in compliance processing: {e}")
            return []
    
    def add_document_to_database(self, document_content: str, document_title: str, category: str = "general"):
        """Add a new regulatory document to the vector database"""
        try:
            # Get embedding for the document
            embedding = self._get_embedding(document_content)
            
            # Prepare metadata
            metadata = {
                "title": document_title,
                "content": document_content,
                "category": category,
                "added_date": datetime.now().isoformat()
            }
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[{
                    "id": f"doc_{datetime.now().timestamp()}",
                    "values": embedding,
                    "metadata": metadata
                }]
            )
            
            return True
        except Exception as e:
            print(f"Error adding document to database: {e}")
            return False
    
    def get_compliance_statistics(self) -> Dict[str, Any]:
        """Get statistics about the compliance monitoring system"""
        try:
            # Get index stats from Pinecone
            stats = self.index.describe_index_stats()
            
            return {
                "total_documents": stats.get("total_vector_count", 0),
                "index_dimension": stats.get("dimension", 0),
                "index_name": self.pinecone_index_name,
                "categories": self.compliance_categories.keys()
            }
        except Exception as e:
            return {"error": str(e)} 