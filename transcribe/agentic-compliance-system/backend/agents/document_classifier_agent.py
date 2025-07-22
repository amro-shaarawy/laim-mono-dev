from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any, Optional
import json
from pydantic import BaseModel
from datetime import datetime

class DocumentCategory(BaseModel):
    """Model for document classification results"""
    document_title: str
    category: str
    subcategory: Optional[str] = None
    confidence: float
    keywords: List[str]
    description: str
    added_date: str

class DocumentClassifierAgent:
    """Document classification agent using CrewAI"""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            openai_api_key=openai_api_key,
            model="gpt-4o-mini",
            temperature=0.1
        )
        
        # Create CrewAI agents
        self._create_agents()
        
        # Define compliance categories and their characteristics
        self.compliance_categories = {
            "esg": {
                "description": "Environmental, Social, and Governance regulations",
                "subcategories": ["environmental", "social", "governance", "sustainability"],
                "keywords": ["environmental", "social", "governance", "sustainability", "carbon", "emissions", "diversity", "inclusion", "climate", "green", "renewable", "stakeholder", "corporate responsibility"]
            },
            "financial": {
                "description": "Financial regulations and accounting standards",
                "subcategories": ["accounting", "audit", "tax", "reporting", "disclosure"],
                "keywords": ["financial", "accounting", "audit", "revenue", "expenses", "profit", "loss", "tax", "balance sheet", "income statement", "cash flow", "GAAP", "IFRS", "SEC", "filing"]
            },
            "legal": {
                "description": "Legal compliance and regulatory requirements",
                "subcategories": ["contracts", "liability", "intellectual property", "employment", "data protection"],
                "keywords": ["legal", "compliance", "regulation", "law", "contract", "liability", "risk", "statute", "ordinance", "mandate", "requirement", "obligation"]
            },
            "ethical": {
                "description": "Ethical standards and conduct guidelines",
                "subcategories": ["conflict of interest", "bribery", "corruption", "whistleblower", "code of conduct"],
                "keywords": ["ethical", "conflict", "interest", "bribery", "corruption", "whistleblower", "integrity", "honesty", "fairness", "transparency", "accountability"]
            },
            "operational": {
                "description": "Operational safety and quality standards",
                "subcategories": ["safety", "security", "quality", "procedures", "standards"],
                "keywords": ["operational", "safety", "security", "quality", "standards", "procedures", "protocol", "guideline", "best practice", "workplace", "health", "safety"]
            },
            "industry_specific": {
                "description": "Industry-specific regulations and standards",
                "subcategories": ["healthcare", "finance", "technology", "manufacturing", "energy"],
                "keywords": ["industry", "sector", "specific", "healthcare", "finance", "technology", "manufacturing", "energy", "pharmaceutical", "banking", "insurance"]
            }
        }
    
    def _create_agents(self):
        """Create the CrewAI agents for document classification"""
        
        # Document Analysis Agent
        self.document_analyzer = Agent(
            role="Document Content Analyzer",
            goal="Analyze document content to identify key themes, topics, and regulatory areas",
            backstory="""You are an expert in document analysis and content classification. 
            You specialize in understanding regulatory documents, legal texts, and compliance materials. 
            You can quickly identify the main themes and categorize documents based on their content.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self._analyze_document_content_tool]
        )
        
        # Classification Agent
        self.classifier = Agent(
            role="Document Classifier",
            goal="Classify documents into appropriate compliance categories with high accuracy",
            backstory="""You are an expert in regulatory compliance and document classification. 
            You understand the nuances between different types of compliance requirements and can 
            accurately categorize documents based on their content and purpose.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self._classify_document_tool]
        )
        
        # Metadata Extractor Agent
        self.metadata_extractor = Agent(
            role="Metadata Extractor",
            goal="Extract relevant metadata and keywords from documents for better searchability",
            backstory="""You are an expert in information extraction and metadata analysis. 
            You can identify key terms, concepts, and important information from documents 
            that will help with future searches and compliance monitoring.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self._extract_metadata_tool]
        )
    
    def _analyze_document_content_tool(self, document_content: str, document_title: str) -> str:
        """Tool for analyzing document content and identifying key themes"""
        try:
            # Analyze the document content
            analysis = {
                "title": document_title,
                "content_length": len(document_content),
                "key_themes": [],
                "regulatory_areas": [],
                "document_type": "unknown",
                "summary": ""
            }
            
            # Simple keyword-based analysis
            content_lower = document_content.lower()
            
            # Check for document type indicators
            if any(word in content_lower for word in ["regulation", "regulatory", "compliance"]):
                analysis["document_type"] = "regulation"
            elif any(word in content_lower for word in ["policy", "procedure", "guideline"]):
                analysis["document_type"] = "policy"
            elif any(word in content_lower for word in ["law", "statute", "act"]):
                analysis["document_type"] = "law"
            elif any(word in content_lower for word in ["standard", "requirement", "specification"]):
                analysis["document_type"] = "standard"
            
            # Identify key themes based on categories
            for category, info in self.compliance_categories.items():
                keyword_matches = [keyword for keyword in info["keywords"] if keyword in content_lower]
                if keyword_matches:
                    analysis["key_themes"].append(category)
                    analysis["regulatory_areas"].extend(keyword_matches)
            
            # Generate a brief summary
            analysis["summary"] = f"Document appears to be a {analysis['document_type']} related to {', '.join(analysis['key_themes'][:3]) if analysis['key_themes'] else 'general compliance'}"
            
            return json.dumps(analysis)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _classify_document_tool(self, analysis_data: str) -> str:
        """Tool for classifying documents into compliance categories"""
        try:
            analysis = json.loads(analysis_data)
            
            classification = {
                "primary_category": "general",
                "subcategory": None,
                "confidence": 0.0,
                "alternative_categories": [],
                "reasoning": ""
            }
            
            # Determine primary category based on key themes
            themes = analysis.get("key_themes", [])
            if themes:
                # Use the most prominent theme as primary category
                classification["primary_category"] = themes[0]
                classification["confidence"] = 0.8
                
                # Add other themes as alternatives
                classification["alternative_categories"] = themes[1:3]
                
                # Determine subcategory
                category_info = self.compliance_categories.get(themes[0], {})
                subcategories = category_info.get("subcategories", [])
                
                # Simple subcategory assignment (could be enhanced with more sophisticated logic)
                if subcategories:
                    classification["subcategory"] = subcategories[0]
                
                classification["reasoning"] = f"Document classified as {themes[0]} based on presence of key themes: {', '.join(themes)}"
            else:
                classification["reasoning"] = "No specific compliance themes identified, classified as general"
            
            return json.dumps(classification)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _extract_metadata_tool(self, document_content: str, classification_data: str) -> str:
        """Tool for extracting metadata and keywords from documents"""
        try:
            classification = json.loads(classification_data)
            
            metadata = {
                "keywords": [],
                "entities": [],
                "important_phrases": [],
                "compliance_indicators": [],
                "risk_level": "low"
            }
            
            # Extract keywords based on category
            category = classification.get("primary_category", "general")
            category_info = self.compliance_categories.get(category, {})
            
            # Add category-specific keywords
            content_lower = document_content.lower()
            for keyword in category_info.get("keywords", []):
                if keyword in content_lower:
                    metadata["keywords"].append(keyword)
            
            # Identify important phrases (simple approach - could be enhanced with NLP)
            sentences = document_content.split('.')
            important_phrases = []
            for sentence in sentences[:10]:  # Look at first 10 sentences
                if any(keyword in sentence.lower() for keyword in ["must", "shall", "required", "prohibited", "violation", "penalty"]):
                    important_phrases.append(sentence.strip())
            
            metadata["important_phrases"] = important_phrases[:5]  # Limit to 5 phrases
            
            # Determine risk level based on content
            high_risk_words = ["penalty", "violation", "prohibited", "illegal", "criminal", "fine"]
            medium_risk_words = ["required", "must", "shall", "compliance", "regulation"]
            
            if any(word in content_lower for word in high_risk_words):
                metadata["risk_level"] = "high"
            elif any(word in content_lower for word in medium_risk_words):
                metadata["risk_level"] = "medium"
            
            return json.dumps(metadata)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def classify_document(self, document_content: str, document_title: str) -> DocumentCategory:
        """Classify a document using the CrewAI agents"""
        
        # Create tasks for the crew
        analysis_task = Task(
            description=f"""
            Analyze the following document for classification:
            Title: {document_title}
            Content: {document_content[:1000]}...
            
            Identify key themes, regulatory areas, and document type.
            """,
            agent=self.document_analyzer,
            expected_output="JSON with document analysis results"
        )
        
        classification_task = Task(
            description=f"""
            Based on the analysis, classify the document into appropriate compliance categories.
            Consider the primary category, subcategory, and confidence level.
            """,
            agent=self.classifier,
            expected_output="JSON with classification results"
        )
        
        metadata_task = Task(
            description=f"""
            Extract relevant metadata, keywords, and important phrases from the document.
            Identify compliance indicators and assess risk level.
            """,
            agent=self.metadata_extractor,
            expected_output="JSON with metadata extraction results"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[self.document_analyzer, self.classifier, self.metadata_extractor],
            tasks=[analysis_task, classification_task, metadata_task],
            verbose=True
        )
        
        try:
            result = await crew.kickoff()
            
            # Parse the result and create DocumentCategory object
            # This is a simplified parsing - you might need to adjust based on actual output format
            category = DocumentCategory(
                document_title=document_title,
                category=result.get("primary_category", "general"),
                subcategory=result.get("subcategory"),
                confidence=result.get("confidence", 0.0),
                keywords=result.get("keywords", []),
                description=result.get("reasoning", "Document classified"),
                added_date=datetime.now().isoformat()
            )
            
            return category
            
        except Exception as e:
            print(f"Error in document classification: {e}")
            # Return a default category
            return DocumentCategory(
                document_title=document_title,
                category="general",
                confidence=0.0,
                keywords=[],
                description=f"Classification error: {str(e)}",
                added_date=datetime.now().isoformat()
            )
    
    def get_category_info(self, category: str) -> Dict[str, Any]:
        """Get information about a specific compliance category"""
        return self.compliance_categories.get(category, {})
    
    def list_categories(self) -> List[str]:
        """List all available compliance categories"""
        return list(self.compliance_categories.keys())
    
    def validate_category(self, category: str) -> bool:
        """Validate if a category exists"""
        return category in self.compliance_categories 