"""
Project Analyzer - Extract context from PRD/codebase for diagram relevance
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any, Tuple
from enum import Enum
import re
import json
from pathlib import Path
import logging

from .catalog import ProjectPhase, StakeholderType, DiagramCategory

logger = logging.getLogger(__name__)


class ProjectType(Enum):
    """Types of projects"""
    WEB_APPLICATION = "web_application"
    MOBILE_APPLICATION = "mobile_application"
    DESKTOP_APPLICATION = "desktop_application"
    API_SERVICE = "api_service"
    MICROSERVICES = "microservices"
    DATA_PIPELINE = "data_pipeline"
    MACHINE_LEARNING = "machine_learning"
    IOT_SYSTEM = "iot_system"
    BLOCKCHAIN = "blockchain"
    ENTERPRISE_SYSTEM = "enterprise_system"
    EMBEDDED_SYSTEM = "embedded_system"
    GAME = "game"
    LIBRARY_FRAMEWORK = "library_framework"
    DEVOPS_TOOL = "devops_tool"


class ArchitecturePattern(Enum):
    """Common architecture patterns"""
    MONOLITH = "monolith"
    MODULAR_MONOLITH = "modular_monolith"
    MICROSERVICES = "microservices"
    SOA = "soa"
    EVENT_DRIVEN = "event_driven"
    SERVERLESS = "serverless"
    CLIENT_SERVER = "client_server"
    PEER_TO_PEER = "peer_to_peer"
    LAYERED = "layered"
    HEXAGONAL = "hexagonal"
    CLEAN_ARCHITECTURE = "clean_architecture"
    ONION = "onion"
    MVC = "mvc"
    MVVM = "mvvm"
    MVP = "mvp"


@dataclass
class TechnologyStack:
    """Technology stack information"""
    languages: Set[str] = field(default_factory=set)
    frameworks: Set[str] = field(default_factory=set)
    databases: Set[str] = field(default_factory=set)
    cloud_providers: Set[str] = field(default_factory=set)
    message_brokers: Set[str] = field(default_factory=set)
    api_protocols: Set[str] = field(default_factory=set)
    authentication: Set[str] = field(default_factory=set)
    testing_frameworks: Set[str] = field(default_factory=set)
    deployment_tools: Set[str] = field(default_factory=set)
    monitoring_tools: Set[str] = field(default_factory=set)


@dataclass
class SystemCharacteristics:
    """System characteristics and quality attributes"""
    scalability_requirements: Set[str] = field(default_factory=set)
    performance_requirements: Set[str] = field(default_factory=set)
    security_requirements: Set[str] = field(default_factory=set)
    availability_requirements: Set[str] = field(default_factory=set)
    compliance_requirements: Set[str] = field(default_factory=set)
    integration_points: Set[str] = field(default_factory=set)
    data_volume: str = "unknown"
    user_count: str = "unknown"
    transaction_volume: str = "unknown"


@dataclass
class ProjectContext:
    """Comprehensive project context extracted from PRD/codebase"""
    
    # Basic project information
    project_name: str = ""
    project_type: Optional[ProjectType] = None
    project_phase: ProjectPhase = ProjectPhase.DESIGN
    description: str = ""
    
    # Stakeholders
    stakeholders: Set[StakeholderType] = field(default_factory=set)
    team_size: str = "unknown"
    organization_size: str = "unknown"
    
    # Technical context
    technology_stack: TechnologyStack = field(default_factory=TechnologyStack)
    architecture_pattern: Optional[ArchitecturePattern] = None
    system_characteristics: SystemCharacteristics = field(default_factory=SystemCharacteristics)
    
    # Domain and entities
    domains: Set[str] = field(default_factory=set)
    entities: Set[str] = field(default_factory=set)
    processes: Set[str] = field(default_factory=set)
    data_flows: Set[str] = field(default_factory=set)
    
    # Requirements
    functional_requirements: List[str] = field(default_factory=list)
    non_functional_requirements: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    
    # External context
    external_systems: Set[str] = field(default_factory=set)
    third_party_integrations: Set[str] = field(default_factory=set)
    regulatory_requirements: Set[str] = field(default_factory=set)
    
    # Project metadata
    estimated_duration: str = "unknown"
    budget_range: str = "unknown"
    risk_level: str = "unknown"
    
    # Source information
    source_files: List[str] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)


class ProjectAnalyzer:
    """Analyzes project documents and codebase to extract context"""
    
    def __init__(self):
        self._language_patterns = self._init_language_patterns()
        self._framework_patterns = self._init_framework_patterns()
        self._architecture_patterns = self._init_architecture_patterns()
        self._requirement_patterns = self._init_requirement_patterns()
    
    def analyze_prd(self, prd_content: str, file_path: str = "") -> ProjectContext:
        """Analyze PRD content to extract project context"""
        context = ProjectContext()
        context.source_files.append(file_path)
        
        # Extract basic information
        context.description = self._extract_description(prd_content)
        context.project_name = self._extract_project_name(prd_content)
        
        # Set default values if extraction fails
        if not context.project_name:
            context.project_name = "Default Project"
        if not context.description:
            context.description = prd_content[:200] + "..." if len(prd_content) > 200 else prd_content
        
        # Extract project type and phase
        context.project_type = self._detect_project_type(prd_content)
        context.project_phase = self._detect_project_phase(prd_content)
        
        # Extract stakeholders
        context.stakeholders = self._extract_stakeholders(prd_content)
        
        # Extract technology stack
        context.technology_stack = self._extract_technology_stack(prd_content)
        
        # Extract architecture pattern
        context.architecture_pattern = self._detect_architecture_pattern(prd_content)
        
        # Extract requirements
        context.functional_requirements = self._extract_functional_requirements(prd_content)
        context.non_functional_requirements = self._extract_non_functional_requirements(prd_content)
        context.constraints = self._extract_constraints(prd_content)
        
        # Extract domains and entities
        context.domains = self._extract_domains(prd_content)
        context.entities = self._extract_entities(prd_content)
        context.processes = self._extract_processes(prd_content)
        
        # Extract system characteristics
        context.system_characteristics = self._extract_system_characteristics(prd_content)
        
        # Extract external context
        context.external_systems = self._extract_external_systems(prd_content)
        context.third_party_integrations = self._extract_integrations(prd_content)
        context.regulatory_requirements = self._extract_regulatory_requirements(prd_content)
        
        # Calculate confidence scores
        context.confidence_scores = self._calculate_confidence_scores(context)
        
        return context
    
    def analyze_codebase(self, codebase_path: str) -> ProjectContext:
        """Analyze codebase to extract project context"""
        context = ProjectContext()
        context.source_files.append(codebase_path)
        
        codebase_path = Path(codebase_path)
        if not codebase_path.exists():
            logger.warning(f"Codebase path does not exist: {codebase_path}")
            return context
        
        # Analyze file structure
        context.technology_stack = self._analyze_technology_stack_from_files(codebase_path)
        
        # Detect architecture pattern from structure
        context.architecture_pattern = self._detect_architecture_from_structure(codebase_path)
        
        # Extract entities from code
        context.entities = self._extract_entities_from_code(codebase_path)
        
        # Extract processes/workflows
        context.processes = self._extract_processes_from_code(codebase_path)
        
        # Detect project type from code
        context.project_type = self._detect_project_type_from_code(codebase_path)
        
        # Calculate confidence scores
        context.confidence_scores = self._calculate_confidence_scores(context)
        
        return context
    
    def analyze_combined(self, prd_content: str, codebase_path: str) -> ProjectContext:
        """Analyze both PRD and codebase for comprehensive context"""
        # Analyze PRD
        prd_context = self.analyze_prd(prd_content, "PRD")
        
        # Analyze codebase
        codebase_context = self.analyze_codebase(codebase_path)
        
        # Merge contexts, prioritizing PRD for business context
        merged_context = self._merge_contexts(prd_context, codebase_context)
        
        return merged_context
    
    def _extract_description(self, content: str) -> str:
        """Extract project description from content"""
        patterns = [
            r"(?i)project\s+(?:description|overview|summary)[:\s]+(.*?)(?:\n\n|\n[A-Z])",
            r"(?i)description[:\s]+(.*?)(?:\n\n|\n[A-Z])",
            r"(?i)overview[:\s]+(.*?)(?:\n\n|\n[A-Z])",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # Fallback to first paragraph
        paragraphs = content.split('\n\n')
        if paragraphs:
            return paragraphs[0].strip()[:500]  # Limit length
        
        return ""
    
    def _extract_project_name(self, content: str) -> str:
        """Extract project name from content"""
        patterns = [
            r"(?i)project\s+name[:\s]+([^\n]+)",
            r"(?i)name[:\s]+([^\n]+)",
            r"(?i)title[:\s]+([^\n]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _detect_project_type(self, content: str) -> Optional[ProjectType]:
        """Detect project type from content"""
        type_keywords = {
            ProjectType.WEB_APPLICATION: ["web application", "website", "web app", "browser", "frontend"],
            ProjectType.MOBILE_APPLICATION: ["mobile app", "ios", "android", "mobile application", "smartphone"],
            ProjectType.DESKTOP_APPLICATION: ["desktop app", "desktop application", "windows", "macos", "linux"],
            ProjectType.API_SERVICE: ["api", "rest", "graphql", "web service", "backend service"],
            ProjectType.MICROSERVICES: ["microservices", "microservice", "service-oriented"],
            ProjectType.DATA_PIPELINE: ["data pipeline", "etl", "data processing", "analytics"],
            ProjectType.MACHINE_LEARNING: ["machine learning", "ml", "ai", "artificial intelligence", "model"],
            ProjectType.IOT_SYSTEM: ["iot", "internet of things", "sensor", "device"],
            ProjectType.BLOCKCHAIN: ["blockchain", "smart contract", "cryptocurrency", "dlt"],
            ProjectType.ENTERPRISE_SYSTEM: ["enterprise", "erp", "crm", "business system"],
        }
        
        content_lower = content.lower()
        scores = {}
        
        for project_type, keywords in type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                scores[project_type] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return None
    
    def _detect_project_phase(self, content: str) -> ProjectPhase:
        """Detect project phase from content"""
        phase_keywords = {
            ProjectPhase.DISCOVERY: ["discovery", "research", "exploration", "feasibility"],
            ProjectPhase.ANALYSIS: ["analysis", "requirements", "specification", "business analysis"],
            ProjectPhase.DESIGN: ["design", "architecture", "planning", "technical design"],
            ProjectPhase.DEVELOPMENT: ["development", "implementation", "coding", "build"],
            ProjectPhase.TESTING: ["testing", "qa", "quality assurance", "validation"],
            ProjectPhase.DEPLOYMENT: ["deployment", "release", "production", "go-live"],
            ProjectPhase.MAINTENANCE: ["maintenance", "support", "operations", "enhancement"],
        }
        
        content_lower = content.lower()
        scores = {}
        
        for phase, keywords in phase_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                scores[phase] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return ProjectPhase.DESIGN  # Default
    
    def _extract_stakeholders(self, content: str) -> Set[StakeholderType]:
        """Extract stakeholders from content"""
        stakeholder_keywords = {
            StakeholderType.EXECUTIVE: ["executive", "ceo", "cto", "management", "leadership"],
            StakeholderType.PRODUCT_MANAGER: ["product manager", "product owner", "pm", "business analyst"],
            StakeholderType.ARCHITECT: ["architect", "solution architect", "technical architect"],
            StakeholderType.DEVELOPER: ["developer", "engineer", "programmer", "coder"],
            StakeholderType.QA_ENGINEER: ["qa", "quality assurance", "tester", "testing"],
            StakeholderType.DEVOPS_ENGINEER: ["devops", "operations", "sre", "infrastructure"],
            StakeholderType.SECURITY_ENGINEER: ["security", "security engineer", "infosec"],
            StakeholderType.BUSINESS_ANALYST: ["business analyst", "ba", "business"],
            StakeholderType.UX_DESIGNER: ["ux designer", "ui designer", "designer"],
            StakeholderType.DATA_ENGINEER: ["data engineer", "data scientist", "analyst"],
        }
        
        content_lower = content.lower()
        stakeholders = set()
        
        for stakeholder_type, keywords in stakeholder_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                stakeholders.add(stakeholder_type)
        
        return stakeholders
    
    def _extract_technology_stack(self, content: str) -> TechnologyStack:
        """Extract technology stack from content"""
        stack = TechnologyStack()
        content_lower = content.lower()
        
        # Languages
        language_patterns = {
            "python": r"\bpython\b",
            "javascript": r"\bjavascript\b|\bjs\b",
            "typescript": r"\btypescript\b|\bts\b",
            "java": r"\bjava\b",
            "c#": r"\bc#\b|\bcsharp\b",
            "go": r"\bgo\b|\bgolang\b",
            "rust": r"\brust\b",
            "ruby": r"\bruby\b",
            "php": r"\bphp\b",
            "swift": r"\bswift\b",
            "kotlin": r"\bkotlin\b",
            "scala": r"\bscala\b",
            "c++": r"\bc\+\+\b",
            "c": r"\bc\b(?!\+)",
        }
        
        for lang, pattern in language_patterns.items():
            if re.search(pattern, content_lower):
                stack.languages.add(lang)
        
        # Frameworks
        framework_patterns = {
            "react": r"\breact\b",
            "vue": r"\bvue\b",
            "angular": r"\bangular\b",
            "django": r"\bdjango\b",
            "flask": r"\bflask\b",
            "fastapi": r"\bfastapi\b",
            "spring": r"\bspring\b",
            "express": r"\bexpress\b",
            "node": r"\bnode\b|\bnodejs\b",
            "rails": r"\brails\b",
            "laravel": r"\blaravel\b",
            "dotnet": r"\b\.net\b|\bdotnet\b",
            "tensorflow": r"\btensorflow\b",
            "pytorch": r"\bpytorch\b",
        }
        
        for framework, pattern in framework_patterns.items():
            if re.search(pattern, content_lower):
                stack.frameworks.add(framework)
        
        # Databases
        database_patterns = {
            "postgresql": r"\bpostgresql\b|\bpostgres\b",
            "mysql": r"\bmysql\b",
            "mongodb": r"\bmongodb\b|\bmongo\b",
            "redis": r"\bredis\b",
            "cassandra": r"\bcassandra\b",
            "elasticsearch": r"\belasticsearch\b",
            "sqlite": r"\bsqlite\b",
            "oracle": r"\boracle\b",
            "sqlserver": r"\bsql\s*server\b",
        }
        
        for db, pattern in database_patterns.items():
            if re.search(pattern, content_lower):
                stack.databases.add(db)
        
        # Cloud providers
        cloud_patterns = {
            "aws": r"\baws\b|\bamazon\s*web\s*services\b",
            "azure": r"\bazure\b|\bcloud\b",
            "gcp": r"\bgcp\b|\bgoogle\s*cloud\b",
            "heroku": r"\bheroku\b",
            "digitalocean": r"\bdigital\s*ocean\b",
        }
        
        for cloud, pattern in cloud_patterns.items():
            if re.search(pattern, content_lower):
                stack.cloud_providers.add(cloud)
        
        return stack
    
    def _detect_architecture_pattern(self, content: str) -> Optional[ArchitecturePattern]:
        """Detect architecture pattern from content"""
        pattern_keywords = {
            ArchitecturePattern.MONOLITH: ["monolith", "monolithic", "single application"],
            ArchitecturePattern.MODULAR_MONOLITH: ["modular monolith", "modules", "components"],
            ArchitecturePattern.MICROSERVICES: ["microservices", "microservice", "service oriented"],
            ArchitecturePattern.SOA: ["soa", "service oriented architecture"],
            ArchitecturePattern.EVENT_DRIVEN: ["event driven", "event sourcing", "cqrs"],
            ArchitecturePattern.SERVERLESS: ["serverless", "lambda", "functions"],
            ArchitecturePattern.CLIENT_SERVER: ["client server", "client-server"],
            ArchitecturePattern.LAYERED: ["layered", "layers", "n-tier"],
            ArchitecturePattern.HEXAGONAL: ["hexagonal", "ports and adapters"],
            ArchitecturePattern.CLEAN_ARCHITECTURE: ["clean architecture", "clean code"],
            ArchitecturePattern.ONION: ["onion architecture"],
            ArchitecturePattern.MVC: ["mvc", "model view controller"],
            ArchitecturePattern.MVVM: ["mvvm", "model view viewmodel"],
        }
        
        content_lower = content.lower()
        scores = {}
        
        for pattern, keywords in pattern_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                scores[pattern] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return None
    
    def _extract_functional_requirements(self, content: str) -> List[str]:
        """Extract functional requirements from content"""
        requirements = []
        
        # Look for requirement sections
        patterns = [
            r"(?i)functional\s+requirements[:\s]*\n(.*?)(?:\n\n|\n[A-Z])",
            r"(?i)requirements[:\s]*\n(.*?)(?:\n\n|\n[A-Z])",
            r"(?i)features[:\s]*\n(.*?)(?:\n\n|\n[A-Z])",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                req_text = match.group(1).strip()
                # Split by bullet points or numbers
                req_items = re.split(r"[-*•]\s*|\d+\.\s*", req_text)
                requirements.extend([req.strip() for req in req_items if req.strip()])
        
        return requirements
    
    def _extract_non_functional_requirements(self, content: str) -> List[str]:
        """Extract non-functional requirements from content"""
        requirements = []
        
        # Look for NFR sections
        patterns = [
            r"(?i)non[-\s]*functional\s+requirements[:\s]*\n(.*?)(?:\n\n|\n[A-Z])",
            r"(?i)quality\s+attributes[:\s]*\n(.*?)(?:\n\n|\n[A-Z])",
            r"(?i)performance\s+requirements[:\s]*\n(.*?)(?:\n\n|\n[A-Z])",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                req_text = match.group(1).strip()
                # Split by bullet points or numbers
                req_items = re.split(r"[-*•]\s*|\d+\.\s*", req_text)
                requirements.extend([req.strip() for req in req_items if req.strip()])
        
        return requirements
    
    def _extract_constraints(self, content: str) -> List[str]:
        """Extract constraints from content"""
        constraints = []
        
        patterns = [
            r"(?i)constraints[:\s]*\n(.*?)(?:\n\n|\n[A-Z])",
            r"(?i)limitations[:\s]*\n(.*?)(?:\n\n|\n[A-Z])",
            r"(?i)restrictions[:\s]*\n(.*?)(?:\n\n|\n[A-Z])",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                constraint_text = match.group(1).strip()
                constraint_items = re.split(r"[-*•]\s*|\d+\.\s*", constraint_text)
                constraints.extend([c.strip() for c in constraint_items if c.strip()])
        
        return constraints
    
    def _extract_domains(self, content: str) -> Set[str]:
        """Extract business domains from content"""
        domain_keywords = [
            "finance", "banking", "insurance", "healthcare", "retail", "ecommerce",
            "education", "government", "manufacturing", "logistics", "transportation",
            "telecommunications", "media", "entertainment", "social", "gaming",
            "energy", "utilities", "real estate", "legal", "consulting", "hr",
            # Technical domains
            "api", "rest", "web", "software", "application", "system", "database",
            "authentication", "security", "backend", "frontend", "microservices",
            "architecture", "integration", "network", "cloud", "devops"
        ]
        
        content_lower = content.lower()
        domains = set()
        
        for domain in domain_keywords:
            if domain in content_lower:
                domains.add(domain)
        
        return domains
    
    def _extract_entities(self, content: str) -> Set[str]:
        """Extract entities from content"""
        entities = set()
        
        # Look for capitalized words that might be entities
        # This is a simplified approach - could be enhanced with NLP
        words = re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b", content)
        
        # Filter out common non-entity words
        common_words = {"The", "This", "That", "User", "System", "Application", "Project", "Data", "Service"}
        
        for word in words:
            if word not in common_words and len(word) > 3:
                entities.add(word)
        
        return entities
    
    def _extract_processes(self, content: str) -> Set[str]:
        """Extract business processes from content"""
        process_keywords = [
            "registration", "login", "authentication", "authorization", "payment",
            "checkout", "order", "booking", "reservation", "search", "filter",
            "upload", "download", "import", "export", "sync", "backup", "restore",
            "notification", "email", "sms", "report", "analytics", "dashboard"
        ]
        
        content_lower = content.lower()
        processes = set()
        
        for process in process_keywords:
            if process in content_lower:
                processes.add(process)
        
        return processes
    
    def _extract_system_characteristics(self, content: str) -> SystemCharacteristics:
        """Extract system characteristics from content"""
        characteristics = SystemCharacteristics()
        content_lower = content.lower()
        
        # Scalability
        scalability_patterns = [
            r"(?i)scalable|scalability|scale\s*(?:up|down|out)",
            r"(?i)high\s*availability|ha|fault\s*tolerant",
            r"(?i)load\s*balanc|horizontal\s*scal|vertical\s*scal"
        ]
        
        for pattern in scalability_patterns:
            if re.search(pattern, content_lower):
                characteristics.scalability_requirements.add("scalability")
        
        # Performance
        performance_patterns = [
            r"(?i)performance|fast|responsive|low\s*latency",
            r"(?i)high\s*throughput|concurrent|real\s*time",
            r"(?i)\d+\s*(?:users|requests|rps|tps)"
        ]
        
        for pattern in performance_patterns:
            if re.search(pattern, content_lower):
                characteristics.performance_requirements.add("performance")
        
        # Security
        security_patterns = [
            r"(?i)security|secure|authentication|authorization",
            r"(?i)encryption|ssl|tls|https|oauth|jwt",
            r"(?i)compliance|gdpr|hipaa|pci|sox"
        ]
        
        for pattern in security_patterns:
            if re.search(pattern, content_lower):
                characteristics.security_requirements.add("security")
        
        return characteristics
    
    def _extract_external_systems(self, content: str) -> Set[str]:
        """Extract external systems from content"""
        external_patterns = [
            r"(?i)external\s+systems?:\s*([^\n]+)",
            r"(?i)third\s*party\s+systems?:\s*([^\n]+)",
            r"(?i)integrations?:\s*([^\n]+)",
        ]
        
        systems = set()
        content_lower = content.lower()
        
        for pattern in external_patterns:
            match = re.search(pattern, content)
            if match:
                system_text = match.group(1)
                # Split by commas and clean up
                system_list = [s.strip() for s in system_text.split(',')]
                systems.update([s for s in system_list if s])
        
        return systems
    
    def _extract_integrations(self, content: str) -> Set[str]:
        """Extract third-party integrations from content"""
        integration_keywords = [
            "stripe", "paypal", "twilio", "sendgrid", "aws", "azure", "gcp",
            "salesforce", "slack", "github", "jira", "confluence", "google", "facebook",
            "twitter", "linkedin", "mailchimp", "segment", "mixpanel", "analytics"
        ]
        
        content_lower = content.lower()
        integrations = set()
        
        for integration in integration_keywords:
            if integration in content_lower:
                integrations.add(integration)
        
        return integrations
    
    def _extract_regulatory_requirements(self, content: str) -> Set[str]:
        """Extract regulatory requirements from content"""
        regulatory_keywords = [
            "gdpr", "hipaa", "pci", "dss", "sox", "ferpa", "coppa", "ccpa",
            "compliance", "regulation", "audit", "privacy", "data protection"
        ]
        
        content_lower = content.lower()
        regulations = set()
        
        for regulation in regulatory_keywords:
            if regulation in content_lower:
                regulations.add(regulation)
        
        return regulations
    
    def _calculate_confidence_scores(self, context: ProjectContext) -> Dict[str, float]:
        """Calculate confidence scores for extracted information"""
        scores = {}
        
        # Project type confidence
        if context.project_type:
            scores["project_type"] = 0.8
        else:
            scores["project_type"] = 0.0
        
        # Technology stack confidence
        tech_score = 0.0
        if context.technology_stack.languages:
            tech_score += 0.4
        if context.technology_stack.frameworks:
            tech_score += 0.3
        if context.technology_stack.databases:
            tech_score += 0.3
        scores["technology_stack"] = min(tech_score, 1.0)
        
        # Architecture pattern confidence
        if context.architecture_pattern:
            scores["architecture_pattern"] = 0.7
        else:
            scores["architecture_pattern"] = 0.0
        
        # Requirements confidence
        req_score = 0.0
        if context.functional_requirements:
            req_score += 0.5
        if context.non_functional_requirements:
            req_score += 0.5
        scores["requirements"] = min(req_score, 1.0)
        
        # Overall confidence
        scores["overall"] = sum(scores.values()) / len(scores)
        
        return scores
    
    def _merge_contexts(self, prd_context: ProjectContext, codebase_context: ProjectContext) -> ProjectContext:
        """Merge PRD and codebase contexts"""
        merged = ProjectContext()
        
        # Use PRD for business context
        merged.project_name = prd_context.project_name
        merged.description = prd_context.description
        merged.project_type = prd_context.project_type
        merged.project_phase = prd_context.project_phase
        merged.stakeholders = prd_context.stakeholders
        merged.functional_requirements = prd_context.functional_requirements
        merged.non_functional_requirements = prd_context.non_functional_requirements
        merged.constraints = prd_context.constraints
        merged.domains = prd_context.domains
        merged.external_systems = prd_context.external_systems
        merged.regulatory_requirements = prd_context.regulatory_requirements
        
        # Merge technology stacks (prioritize codebase for actual tech)
        merged.technology_stack.languages.update(codebase_context.technology_stack.languages)
        merged.technology_stack.frameworks.update(codebase_context.technology_stack.frameworks)
        merged.technology_stack.databases.update(codebase_context.technology_stack.databases)
        merged.technology_stack.cloud_providers.update(prd_context.technology_stack.cloud_providers)
        
        # Use codebase for actual architecture if detected
        merged.architecture_pattern = codebase_context.architecture_pattern or prd_context.architecture_pattern
        
        # Merge entities and processes
        merged.entities.update(prd_context.entities)
        merged.entities.update(codebase_context.entities)
        merged.processes.update(prd_context.processes)
        merged.processes.update(codebase_context.processes)
        
        # Merge system characteristics
        merged.system_characteristics = prd_context.system_characteristics
        
        # Merge source files
        merged.source_files.extend(prd_context.source_files)
        merged.source_files.extend(codebase_context.source_files)
        
        # Recalculate confidence scores
        merged.confidence_scores = self._calculate_confidence_scores(merged)
        
        return merged
    
    def _init_language_patterns(self) -> Dict[str, str]:
        """Initialize language detection patterns"""
        return {
            "python": r"\.py$|requirements\.txt|setup\.py",
            "javascript": r"\.js$|package\.json|npm",
            "typescript": r"\.ts$|tsconfig\.json|\.d\.ts$",
            "java": r"\.java$|pom\.xml|build\.gradle",
            "c#": r"\.cs$|\.csproj$|\.sln$",
            "go": r"\.go$|go\.mod|go\.sum",
            "rust": r"\.rs$|Cargo\.toml",
            "ruby": r"\.rb$|Gemfile|\.gemspec",
            "php": r"\.php$|composer\.json",
        }
    
    def _init_framework_patterns(self) -> Dict[str, str]:
        """Initialize framework detection patterns"""
        return {
            "react": r"package\.json.*react|src/App\.js|src/App\.tsx",
            "vue": r"package\.json.*vue|\.vue$|vue\.config\.js",
            "angular": r"angular\.json|\.module\.ts|app\.component\.ts",
            "django": r"settings\.py|manage\.py|views\.py",
            "flask": r"app\.py|flask|@app\.route",
            "spring": r"pom\.xml.*spring|@SpringBootApplication|@RestController",
            "express": r"app\.js|express\(\)|require.*express",
        }
    
    def _init_architecture_patterns(self) -> Dict[str, str]:
        """Initialize architecture detection patterns"""
        return {
            "microservices": r"services/|microservice|docker-compose\.yml",
            "monolith": r"src/|app\.|single.*application",
            "mvc": r"controllers/|models/|views/",
            "layered": r"layers/|presentation/|business/|data/",
        }
    
    def _init_requirement_patterns(self) -> Dict[str, str]:
        """Initialize requirement extraction patterns"""
        return {
            "functional": r"(?i)functional.*requirement|feature|capability",
            "non_functional": r"(?i)non.*functional|quality.*attribute|performance",
            "constraint": r"(?i)constraint|limitation|restriction",
        }
    
    def _analyze_technology_stack_from_files(self, codebase_path: Path) -> TechnologyStack:
        """Analyze technology stack from file structure"""
        stack = TechnologyStack()
        
        # This is a simplified implementation
        # In practice, you'd parse package.json, requirements.txt, etc.
        
        for file_path in codebase_path.rglob("*"):
            if file_path.is_file():
                # Check language patterns
                for lang, pattern in self._language_patterns.items():
                    if re.search(pattern, str(file_path)):
                        stack.languages.add(lang)
                
                # Check framework patterns
                for framework, pattern in self._framework_patterns.items():
                    if re.search(pattern, str(file_path)):
                        stack.frameworks.add(framework)
        
        return stack
    
    def _detect_architecture_from_structure(self, codebase_path: Path) -> Optional[ArchitecturePattern]:
        """Detect architecture pattern from file structure"""
        # Simplified detection based on directory structure
        dirs = [d.name for d in codebase_path.iterdir() if d.is_dir()]
        
        if "services" in dirs or "microservices" in dirs:
            return ArchitecturePattern.MICROSERVICES
        elif "controllers" in dirs and "models" in dirs and "views" in dirs:
            return ArchitecturePattern.MVC
        elif "layers" in dirs or "presentation" in dirs:
            return ArchitecturePattern.LAYERED
        elif "src" in dirs:
            return ArchitecturePattern.MONOLITH
        
        return None
    
    def _extract_entities_from_code(self, codebase_path: Path) -> Set[str]:
        """Extract entities from code files"""
        entities = set()
        
        # Simplified entity extraction from class names
        for file_path in codebase_path.rglob("*.py"):
            if file_path.is_file():
                try:
                    content = file_path.read_text()
                    # Look for class definitions
                    class_matches = re.findall(r"class\s+(\w+)", content)
                    entities.update(class_matches)
                except:
                    continue
        
        return entities
    
    def _extract_processes_from_code(self, codebase_path: Path) -> Set[str]:
        """Extract processes from code files"""
        processes = set()
        
        # Look for function names that might represent processes
        for file_path in codebase_path.rglob("*.py"):
            if file_path.is_file():
                try:
                    content = file_path.read_text()
                    # Look for function definitions
                    func_matches = re.findall(r"def\s+(\w+)", content)
                    processes.update(func_matches)
                except:
                    continue
        
        return processes
    
    def _detect_project_type_from_code(self, codebase_path: Path) -> Optional[ProjectType]:
        """Detect project type from code structure"""
        dirs = [d.name for d in codebase_path.iterdir() if d.is_dir()]
        files = [f.name for f in codebase_path.rglob("*") if f.is_file()]
        
        # Check for web application indicators
        if any(f in files for f in ["package.json", "requirements.txt", "pom.xml"]):
            if "src" in dirs and any(f in files for f in ["App.js", "app.py", "Application.java"]):
                return ProjectType.WEB_APPLICATION
        
        # Check for API service indicators
        if "api" in dirs or any("api" in f.lower() for f in files):
            return ProjectType.API_SERVICE
        
        return None
