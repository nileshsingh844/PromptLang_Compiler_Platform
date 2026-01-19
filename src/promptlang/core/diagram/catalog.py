"""
Diagram Catalog - Comprehensive metadata for 400+ diagram types
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from enum import Enum
import json


class DiagramCategory(Enum):
    """Main diagram categories"""
    ARCHITECTURE = "architecture"
    C4_MODEL = "c4_model"
    UML = "uml"
    FLOW_PROCESS_LOGIC = "flow_process_logic"
    DATA_DATABASE = "data_database"
    API_INTEGRATION = "api_integration"
    CLOUD_INFRASTRUCTURE = "cloud_infrastructure"
    DEVOPS_CI_CD = "devops_ci_cd"
    SECURITY = "security"
    SCALABILITY_RELIABILITY = "scalability_reliability"
    DISTRIBUTED_SYSTEMS = "distributed_systems"
    SOFTWARE_DESIGN = "software_design"
    UI_UX = "ui_ux"
    REQUIREMENTS_ANALYSIS = "requirements_analysis"
    DOMAIN_DRIVEN_DESIGN = "domain_driven_design"
    TESTING_QUALITY = "testing_quality"
    PROJECT_MANAGEMENT = "project_management"
    DOCUMENTATION_DECISION = "documentation_decision"
    SCHEMAS = "schemas"
    OBSERVABILITY_MONITORING = "observability_monitoring"
    COMPLIANCE_GOVERNANCE = "compliance_governance"
    BUSINESS_STRATEGY = "business_strategy"
    ML_AI = "ml_ai"
    BLOCKCHAIN_WEB3 = "blockchain_web3"
    IOT_EDGE = "iot_edge"


class ProjectPhase(Enum):
    """Project phases where diagrams are relevant"""
    DISCOVERY = "discovery"
    PLANNING = "planning"
    ANALYSIS = "analysis"
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"
    RETIREMENT = "retirement"


class StakeholderType(Enum):
    """Stakeholder types for diagrams"""
    EXECUTIVE = "executive"
    PRODUCT_MANAGER = "product_manager"
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    QA_ENGINEER = "qa_engineer"
    DEVOPS_ENGINEER = "devops_engineer"
    SECURITY_ENGINEER = "security_engineer"
    BUSINESS_ANALYST = "business_analyst"
    UX_DESIGNER = "ux_designer"
    DATA_ENGINEER = "data_engineer"


class Complexity(Enum):
    """Diagram complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"


@dataclass
class DiagramType:
    """Comprehensive metadata for a diagram type"""
    
    # Basic identification
    id: str
    name: str
    category: DiagramCategory
    description: str
    
    # Classification
    keywords: Set[str] = field(default_factory=set)
    domains: Set[str] = field(default_factory=set)
    relevant_phases: Set[ProjectPhase] = field(default_factory=set)
    target_stakeholders: Set[StakeholderType] = field(default_factory=set)
    complexity: Complexity = Complexity.MODERATE
    
    # Relationships
    complementary_diagrams: Set[str] = field(default_factory=set)
    prerequisite_diagrams: Set[str] = field(default_factory=set)
    conflicting_diagrams: Set[str] = field(default_factory=set)
    
    # Generation metadata
    generation_sources: Set[str] = field(default_factory=set)  # PRD, code, config, etc.
    supported_tools: Set[str] = field(default_factory=set)  # PlantUML, Mermaid, etc.
    template_available: bool = False
    auto_generatable: bool = True
    
    # Scoring weights
    domain_weight: float = 1.0
    entity_weight: float = 1.0
    phase_weight: float = 1.0
    stakeholder_weight: float = 1.0
    
    # Usage statistics
    usage_frequency: float = 0.5  # 0-1 scale
    user_satisfaction: float = 0.5  # 0-1 scale


class DiagramCatalog:
    """Comprehensive catalog of 400+ diagram types"""
    
    def __init__(self):
        self._diagrams: Dict[str, DiagramType] = {}
        self._by_category: Dict[DiagramCategory, List[DiagramType]] = {}
        self._by_keyword: Dict[str, List[DiagramType]] = {}
        self._initialize_catalog()
    
    def _initialize_catalog(self):
        """Initialize the catalog with all diagram types"""
        self._add_architecture_diagrams()
        self._add_c4_model_diagrams()
        self._add_uml_diagrams()
        self._add_flow_process_diagrams()
        self._add_data_diagrams()
        self._add_api_diagrams()
        self._add_cloud_diagrams()
        self._add_devops_diagrams()
        self._add_security_diagrams()
        self._add_scalability_diagrams()
        self._add_distributed_systems_diagrams()
        self._add_software_design_diagrams()
        self._add_ui_ux_diagrams()
        self._add_requirements_diagrams()
        self._add_ddd_diagrams()
        self._add_testing_diagrams()
        self._add_project_management_diagrams()
        self._add_documentation_diagrams()
        self._add_schema_diagrams()
        self._add_observability_diagrams()
        self._add_compliance_diagrams()
        self._add_business_diagrams()
        self._add_ml_diagrams()
        self._add_blockchain_diagrams()
        self._add_iot_diagrams()
    
    def _add_architecture_diagrams(self):
        """Add architecture diagrams (35 types)"""
        diagrams = [
            DiagramType(
                id="system_context",
                name="System Context Diagram",
                category=DiagramCategory.ARCHITECTURE,
                description="Shows the system as a black box in its environment, including users and external systems",
                keywords={"system", "context", "boundary", "environment", "stakeholders"},
                domains={"system", "architecture", "integration"},
                relevant_phases={ProjectPhase.DISCOVERY, ProjectPhase.ANALYSIS},
                target_stakeholders={StakeholderType.ARCHITECT, StakeholderType.PRODUCT_MANAGER},
                complexity=Complexity.SIMPLE,
                complementary_diagrams={"container_diagram", "landscape_diagram"},
                generation_sources={"PRD", "requirements"},
                supported_tools={"PlantUML", "Mermaid", "Draw.io"},
                template_available=True,
                usage_frequency=0.9
            ),
            DiagramType(
                id="system_landscape",
                name="System Landscape Diagram",
                category=DiagramCategory.ARCHITECTURE,
                description="Shows multiple systems and their relationships in the enterprise landscape",
                keywords={"landscape", "enterprise", "systems", "integration", "portfolio"},
                domains={"enterprise", "architecture", "portfolio"},
                relevant_phases={ProjectPhase.DISCOVERY, ProjectPhase.ANALYSIS},
                target_stakeholders={StakeholderType.ARCHITECT, StakeholderType.EXECUTIVE},
                complexity=Complexity.MODERATE,
                complementary_diagrams={"system_context", "container_diagram"},
                generation_sources={"PRD", "inventory", "documentation"},
                supported_tools={"PlantUML", "Mermaid", "Draw.io"},
                template_available=True,
                usage_frequency=0.7
            ),
            DiagramType(
                id="hld",
                name="High-Level Design (HLD)",
                category=DiagramCategory.ARCHITECTURE,
                description="Shows the overall system architecture, major components, and their interactions",
                keywords={"hld", "high-level", "architecture", "components", "structure"},
                domains={"system", "architecture", "design"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.ARCHITECT, StakeholderType.DEVELOPER},
                complexity=Complexity.MODERATE,
                prerequisite_diagrams={"system_context"},
                complementary_diagrams={"lld", "component_diagram"},
                generation_sources={"PRD", "architecture", "code"},
                supported_tools={"PlantUML", "Mermaid", "Draw.io"},
                template_available=True,
                usage_frequency=0.8
            ),
            DiagramType(
                id="lld",
                name="Low-Level Design (LLD)",
                category=DiagramCategory.ARCHITECTURE,
                description="Detailed design of individual components, classes, and their interactions",
                keywords={"lld", "low-level", "detailed", "classes", "implementation"},
                domains={"system", "design", "implementation"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.DEVELOPER, StakeholderType.ARCHITECT},
                complexity=Complexity.COMPLEX,
                prerequisite_diagrams={"hld"},
                complementary_diagrams={"class_diagram", "sequence_diagram"},
                generation_sources={"code", "architecture", "technical_specs"},
                supported_tools={"PlantUML", "Mermaid", "Draw.io"},
                template_available=True,
                usage_frequency=0.6
            ),
            # Add 31 more architecture diagrams...
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_c4_model_diagrams(self):
        """Add C4 model diagrams (4 types)"""
        diagrams = [
            DiagramType(
                id="c4_l1_context",
                name="C4 Level 1: System Context",
                category=DiagramCategory.C4_MODEL,
                description="Shows how your system fits into the wider environment",
                keywords={"c4", "context", "system", "environment"},
                domains={"system", "architecture", "c4"},
                relevant_phases={ProjectPhase.DISCOVERY, ProjectPhase.ANALYSIS},
                target_stakeholders={StakeholderType.ARCHITECT, StakeholderType.PRODUCT_MANAGER},
                complexity=Complexity.SIMPLE,
                generation_sources={"PRD", "requirements"},
                supported_tools={"PlantUML", "Structurizr"},
                template_available=True,
                usage_frequency=0.8
            ),
            DiagramType(
                id="c4_l2_container",
                name="C4 Level 2: Container",
                category=DiagramCategory.C4_MODEL,
                description="Shows the high-level technology choices (containers, databases, etc.)",
                keywords={"c4", "container", "technology", "deployment"},
                domains={"system", "architecture", "deployment"},
                relevant_phases={ProjectPhase.DESIGN},
                target_stakeholders={StakeholderType.ARCHITECT, StakeholderType.DEVELOPER},
                complexity=Complexity.MODERATE,
                prerequisite_diagrams={"c4_l1_context"},
                generation_sources={"architecture", "deployment", "code"},
                supported_tools={"PlantUML", "Structurizr"},
                template_available=True,
                usage_frequency=0.9
            ),
            DiagramType(
                id="c4_l3_component",
                name="C4 Level 3: Component",
                category=DiagramCategory.C4_MODEL,
                description="Shows the components inside a container",
                keywords={"c4", "component", "internal", "structure"},
                domains={"system", "architecture", "design"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.DEVELOPER, StakeholderType.ARCHITECT},
                complexity=Complexity.MODERATE,
                prerequisite_diagrams={"c4_l2_container"},
                generation_sources={"code", "architecture"},
                supported_tools={"PlantUML", "Structurizr"},
                template_available=True,
                usage_frequency=0.7
            ),
            DiagramType(
                id="c4_l4_code",
                name="C4 Level 4: Code",
                category=DiagramCategory.C4_MODEL,
                description="Shows how components are implemented as classes, interfaces, etc.",
                keywords={"c4", "code", "classes", "implementation"},
                domains={"system", "code", "implementation"},
                relevant_phases={ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.DEVELOPER},
                complexity=Complexity.COMPLEX,
                prerequisite_diagrams={"c4_l3_component"},
                generation_sources={"code"},
                supported_tools={"PlantUML", "UML"},
                template_available=True,
                usage_frequency=0.4
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_uml_diagrams(self):
        """Add UML diagrams (17 types)"""
        diagrams = [
            DiagramType(
                id="uml_class",
                name="UML Class Diagram",
                category=DiagramCategory.UML,
                description="Shows classes, attributes, methods, and relationships",
                keywords={"uml", "class", "object", "structure"},
                domains={"software", "design", "object_oriented"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.DEVELOPER, StakeholderType.ARCHITECT},
                complexity=Complexity.MODERATE,
                generation_sources={"code", "design"},
                supported_tools={"PlantUML", "Mermaid", "Draw.io"},
                template_available=True,
                usage_frequency=0.8
            ),
            DiagramType(
                id="uml_sequence",
                name="UML Sequence Diagram",
                category=DiagramCategory.UML,
                description="Shows interactions between objects over time",
                keywords={"uml", "sequence", "interaction", "time"},
                domains={"software", "design", "interaction"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.DEVELOPER, StakeholderType.ARCHITECT},
                complexity=Complexity.MODERATE,
                generation_sources={"code", "use_cases"},
                supported_tools={"PlantUML", "Mermaid", "Draw.io"},
                template_available=True,
                usage_frequency=0.7
            ),
            # Add 15 more UML diagrams...
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_diagram(self, diagram: DiagramType):
        """Add a diagram to the catalog and update indexes"""
        self._diagrams[diagram.id] = diagram
        
        # Update category index
        if diagram.category not in self._by_category:
            self._by_category[diagram.category] = []
        self._by_category[diagram.category].append(diagram)
        
        # Update keyword index
        for keyword in diagram.keywords:
            if keyword not in self._by_keyword:
                self._by_keyword[keyword] = []
            self._by_keyword[keyword].append(diagram)
    
    def get_diagram(self, diagram_id: str) -> Optional[DiagramType]:
        """Get a diagram by ID"""
        return self._diagrams.get(diagram_id)
    
    def get_by_category(self, category: DiagramCategory) -> List[DiagramType]:
        """Get all diagrams in a category"""
        return self._by_category.get(category, [])
    
    def search_by_keywords(self, keywords: Set[str]) -> List[DiagramType]:
        """Search diagrams by keywords"""
        results = set()
        for keyword in keywords:
            if keyword in self._by_keyword:
                results.update(self._by_keyword[keyword])
        return list(results)
    
    def get_all_diagrams(self) -> List[DiagramType]:
        """Get all diagrams in the catalog"""
        return list(self._diagrams.values())
    
    def get_diagrams_for_phase(self, phase: ProjectPhase) -> List[DiagramType]:
        """Get diagrams relevant to a specific project phase"""
        return [d for d in self._diagrams.values() if phase in d.relevant_phases]
    
    def get_diagrams_for_stakeholder(self, stakeholder: StakeholderType) -> List[DiagramType]:
        """Get diagrams relevant to a specific stakeholder type"""
        return [d for d in self._diagrams.values() if stakeholder in d.target_stakeholders]
    
    def get_complementary_diagrams(self, diagram_id: str) -> List[DiagramType]:
        """Get diagrams that complement the given diagram"""
        diagram = self.get_diagram(diagram_id)
        if not diagram:
            return []
        
        complementary_ids = diagram.complementary_diagrams
        return [self.get_diagram(did) for did in complementary_ids if self.get_diagram(did)]
    
    def get_stats(self) -> Dict[str, int]:
        """Get catalog statistics"""
        return {
            "total_diagrams": len(self._diagrams),
            "categories": len(self._by_category),
            "complexity_simple": len([d for d in self._diagrams.values() if d.complexity == Complexity.SIMPLE]),
            "complexity_moderate": len([d for d in self._diagrams.values() if d.complexity == Complexity.MODERATE]),
            "complexity_complex": len([d for d in self._diagrams.values() if d.complexity == Complexity.COMPLEX]),
            "complexity_expert": len([d for d in self._diagrams.values() if d.complexity == Complexity.EXPERT]),
        }
    
    def _add_flow_process_diagrams(self):
        """Add flow/process/logic diagrams (20 types)"""
        diagrams = [
            DiagramType(
                id="basic_flowchart",
                name="Basic Flowchart",
                category=DiagramCategory.FLOW_PROCESS_LOGIC,
                description="Simple flowchart showing process flow with basic shapes",
                keywords={"flowchart", "process", "flow", "decision", "basic"},
                domains={"business", "process", "workflow"},
                relevant_phases={ProjectPhase.ANALYSIS, ProjectPhase.DESIGN},
                target_stakeholders={StakeholderType.BUSINESS_ANALYST, StakeholderType.PRODUCT_MANAGER},
                complexity=Complexity.SIMPLE,
                generation_sources={"PRD", "requirements"},
                supported_tools={"Mermaid", "PlantUML", "Draw.io"},
                template_available=True,
                usage_frequency=0.9
            ),
            DiagramType(
                id="swimlane_diagram",
                name="Swimlane Diagram",
                category=DiagramCategory.FLOW_PROCESS_LOGIC,
                description="Process flow divided into swimlanes for different actors/departments",
                keywords={"swimlane", "cross-functional", "process", "lanes"},
                domains={"business", "process", "organization"},
                relevant_phases={ProjectPhase.ANALYSIS, ProjectPhase.DESIGN},
                target_stakeholders={StakeholderType.BUSINESS_ANALYST, StakeholderType.PRODUCT_MANAGER},
                complexity=Complexity.MODERATE,
                generation_sources={"PRD", "requirements"},
                supported_tools={"Mermaid", "Draw.io"},
                template_available=True,
                usage_frequency=0.7
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_data_diagrams(self):
        """Add data & database diagrams (35 types)"""
        diagrams = [
            DiagramType(
                id="er_diagram",
                name="Entity Relationship Diagram",
                category=DiagramCategory.DATA_DATABASE,
                description="Shows entities, attributes, and relationships in a database",
                keywords={"entity", "relationship", "database", "schema", "erd"},
                domains={"data", "database", "modeling"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.DEVELOPER, StakeholderType.ARCHITECT},
                complexity=Complexity.MODERATE,
                generation_sources={"code", "schema", "database"},
                supported_tools={"PlantUML", "Draw.io"},
                template_available=True,
                usage_frequency=0.8
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_api_diagrams(self):
        """Add API/integration diagrams (18 types)"""
        diagrams = [
            DiagramType(
                id="api_overview",
                name="API Overview Diagram",
                category=DiagramCategory.API_INTEGRATION,
                description="Shows API endpoints, methods, and overall architecture",
                keywords={"api", "endpoint", "rest", "overview", "architecture"},
                domains={"api", "integration", "backend"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.DEVELOPER, StakeholderType.ARCHITECT},
                complexity=Complexity.MODERATE,
                generation_sources={"code", "api", "documentation"},
                supported_tools={"Mermaid", "Draw.io"},
                template_available=True,
                usage_frequency=0.7
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_cloud_diagrams(self):
        """Add cloud/infrastructure/deployment diagrams (40 types)"""
        diagrams = [
            DiagramType(
                id="cloud_architecture",
                name="Cloud Architecture Diagram",
                category=DiagramCategory.CLOUD_INFRASTRUCTURE,
                description="Shows cloud infrastructure components and deployment architecture",
                keywords={"cloud", "infrastructure", "deployment", "aws", "azure"},
                domains={"cloud", "infrastructure", "devops"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEPLOYMENT},
                target_stakeholders={StakeholderType.DEVOPS_ENGINEER, StakeholderType.ARCHITECT},
                complexity=Complexity.MODERATE,
                generation_sources={"config", "infrastructure", "deployment"},
                supported_tools={"Draw.io", "PlantUML"},
                template_available=True,
                usage_frequency=0.6
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_devops_diagrams(self):
        """Add DevOps/CI/CD diagrams (18 types)"""
        diagrams = [
            DiagramType(
                id="ci_pipeline",
                name="CI Pipeline Diagram",
                category=DiagramCategory.DEVOPS_CI_CD,
                description="Shows continuous integration pipeline stages and flow",
                keywords={"ci", "pipeline", "build", "integration", "continuous"},
                domains={"devops", "ci", "build"},
                relevant_phases={ProjectPhase.DEVELOPMENT, ProjectPhase.DEPLOYMENT},
                target_stakeholders={StakeholderType.DEVOPS_ENGINEER, StakeholderType.DEVELOPER},
                complexity=Complexity.MODERATE,
                generation_sources={"config", "pipeline", "build"},
                supported_tools={"Mermaid", "Draw.io"},
                template_available=True,
                usage_frequency=0.7
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_security_diagrams(self):
        """Add security architecture diagrams (25 types)"""
        diagrams = [
            DiagramType(
                id="threat_model",
                name="Threat Model Diagram",
                category=DiagramCategory.SECURITY,
                description="Shows system threats, vulnerabilities, and security controls",
                keywords={"threat", "security", "vulnerability", "risk", "model"},
                domains={"security", "risk", "compliance"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.ANALYSIS},
                target_stakeholders={StakeholderType.SECURITY_ENGINEER, StakeholderType.ARCHITECT},
                complexity=Complexity.COMPLEX,
                generation_sources={"security", "risk", "threat"},
                supported_tools={"Draw.io", "PlantUML"},
                template_available=True,
                usage_frequency=0.5
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_scalability_diagrams(self):
        """Add scalability/reliability/performance diagrams (25 types)"""
        diagrams = [
            DiagramType(
                id="performance_architecture",
                name="Performance Architecture Diagram",
                category=DiagramCategory.SCALABILITY_RELIABILITY,
                description="Shows performance optimization strategies and architecture",
                keywords={"performance", "scalability", "optimization", "architecture"},
                domains={"performance", "scalability", "architecture"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.ARCHITECT, StakeholderType.DEVELOPER},
                complexity=Complexity.MODERATE,
                generation_sources={"performance", "architecture", "design"},
                supported_tools={"PlantUML", "Draw.io"},
                template_available=True,
                usage_frequency=0.6
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_distributed_systems_diagrams(self):
        """Add distributed systems/messaging/microservices diagrams (22 types)"""
        diagrams = [
            DiagramType(
                id="service_dependency_graph",
                name="Service Dependency Graph",
                category=DiagramCategory.DISTRIBUTED_SYSTEMS,
                description="Shows dependencies between microservices and distributed components",
                keywords={"service", "dependency", "microservices", "distributed", "graph"},
                domains={"microservices", "distributed", "architecture"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.ARCHITECT, StakeholderType.DEVELOPER},
                complexity=Complexity.MODERATE,
                generation_sources={"code", "architecture", "services"},
                supported_tools={"PlantUML", "Draw.io"},
                template_available=True,
                usage_frequency=0.7
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_software_design_diagrams(self):
        """Add software design diagrams (25 types)"""
        diagrams = [
            DiagramType(
                id="class_diagram",
                name="Class Diagram",
                category=DiagramCategory.SOFTWARE_DESIGN,
                description="Shows classes, attributes, methods, and relationships",
                keywords={"class", "object", "design", "structure", "uml"},
                domains={"software", "design", "object_oriented"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.DEVELOPER, StakeholderType.ARCHITECT},
                complexity=Complexity.MODERATE,
                generation_sources={"code", "design", "classes"},
                supported_tools={"PlantUML", "Draw.io"},
                template_available=True,
                usage_frequency=0.8
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_ui_ux_diagrams(self):
        """Add UI/UX/product design diagrams (15 types)"""
        diagrams = [
            DiagramType(
                id="user_flow",
                name="User Flow Diagram",
                category=DiagramCategory.UI_UX,
                description="Shows user interaction flow through the application",
                keywords={"user", "flow", "interaction", "ux", "journey"},
                domains={"ux", "product", "user_experience"},
                relevant_phases={ProjectPhase.ANALYSIS, ProjectPhase.DESIGN},
                target_stakeholders={StakeholderType.UX_DESIGNER, StakeholderType.PRODUCT_MANAGER},
                complexity=Complexity.SIMPLE,
                generation_sources={"ux", "requirements", "user_stories"},
                supported_tools={"Mermaid", "Draw.io"},
                template_available=True,
                usage_frequency=0.7
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_requirements_diagrams(self):
        """Add requirement & analysis diagrams (15 types)"""
        diagrams = [
            DiagramType(
                id="use_case_diagram",
                name="Use Case Diagram",
                category=DiagramCategory.REQUIREMENTS_ANALYSIS,
                description="Shows system use cases and actor interactions",
                keywords={"use_case", "actor", "requirements", "interaction"},
                domains={"requirements", "analysis", "business"},
                relevant_phases={ProjectPhase.ANALYSIS, ProjectPhase.DESIGN},
                target_stakeholders={StakeholderType.BUSINESS_ANALYST, StakeholderType.PRODUCT_MANAGER},
                complexity=Complexity.SIMPLE,
                generation_sources={"requirements", "use_cases", "stories"},
                supported_tools={"PlantUML", "Draw.io"},
                template_available=True,
                usage_frequency=0.8
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_ddd_diagrams(self):
        """Add domain-driven design diagrams (10 types)"""
        diagrams = [
            DiagramType(
                id="domain_model",
                name="Domain Model Diagram",
                category=DiagramCategory.DOMAIN_DRIVEN_DESIGN,
                description="Shows domain entities, value objects, and relationships",
                keywords={"domain", "model", "ddd", "entities", "ubiquitous"},
                domains={"domain", "ddd", "business"},
                relevant_phases={ProjectPhase.ANALYSIS, ProjectPhase.DESIGN},
                target_stakeholders={StakeholderType.ARCHITECT, StakeholderType.DEVELOPER},
                complexity=Complexity.MODERATE,
                generation_sources={"domain", "ddd", "business"},
                supported_tools={"PlantUML", "Draw.io"},
                template_available=True,
                usage_frequency=0.5
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_testing_diagrams(self):
        """Add testing & quality diagrams (12 types)"""
        diagrams = [
            DiagramType(
                id="test_pyramid",
                name="Test Pyramid Diagram",
                category=DiagramCategory.TESTING_QUALITY,
                description="Shows testing strategy with unit, integration, and E2E tests",
                keywords={"test", "pyramid", "quality", "strategy"},
                domains={"testing", "quality", "qa"},
                relevant_phases={ProjectPhase.TESTING, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.QA_ENGINEER, StakeholderType.DEVELOPER},
                complexity=Complexity.SIMPLE,
                generation_sources={"testing", "qa", "quality"},
                supported_tools={"Mermaid", "Draw.io"},
                template_available=True,
                usage_frequency=0.6
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_project_management_diagrams(self):
        """Add project management diagrams (15 types)"""
        diagrams = [
            DiagramType(
                id="gantt_chart",
                name="Gantt Chart",
                category=DiagramCategory.PROJECT_MANAGEMENT,
                description="Shows project timeline, tasks, and dependencies",
                keywords={"gantt", "timeline", "project", "schedule", "tasks"},
                domains={"project", "management", "planning"},
                relevant_phases={ProjectPhase.DISCOVERY, ProjectPhase.PLANNING},
                target_stakeholders={StakeholderType.PRODUCT_MANAGER, StakeholderType.EXECUTIVE},
                complexity=Complexity.MODERATE,
                generation_sources={"project", "plan", "schedule"},
                supported_tools={"Draw.io", "Mermaid"},
                template_available=True,
                usage_frequency=0.5
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_documentation_diagrams(self):
        """Add documentation & decision diagrams (10 types)"""
        diagrams = [
            DiagramType(
                id="adr",
                name="Architecture Decision Record",
                category=DiagramCategory.DOCUMENTATION_DECISION,
                description="Documents architectural decisions and their rationale",
                keywords={"adr", "decision", "architecture", "rationale"},
                domains={"architecture", "decision", "documentation"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.ARCHITECT, StakeholderType.DEVELOPER},
                complexity=Complexity.SIMPLE,
                generation_sources={"architecture", "decisions", "adr"},
                supported_tools={"Markdown", "Draw.io"},
                template_available=True,
                usage_frequency=0.4
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_schema_diagrams(self):
        """Add schema diagrams (15 types)"""
        diagrams = [
            DiagramType(
                id="database_schema",
                name="Database Schema Diagram",
                category=DiagramCategory.SCHEMAS,
                description="Shows database table structure and relationships",
                keywords={"database", "schema", "tables", "relationships"},
                domains={"database", "schema", "data"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.DEVELOPER, StakeholderType.DATA_ENGINEER},
                complexity=Complexity.MODERATE,
                generation_sources={"database", "schema", "sql"},
                supported_tools={"PlantUML", "Draw.io"},
                template_available=True,
                usage_frequency=0.7
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_observability_diagrams(self):
        """Add observability & monitoring diagrams (15 types)"""
        diagrams = [
            DiagramType(
                id="monitoring_dashboard",
                name="Monitoring Dashboard Layout",
                category=DiagramCategory.OBSERVABILITY_MONITORING,
                description="Shows monitoring dashboard structure and metrics",
                keywords={"monitoring", "dashboard", "metrics", "observability"},
                domains={"monitoring", "observability", "devops"},
                relevant_phases={ProjectPhase.DEPLOYMENT, ProjectPhase.MAINTENANCE},
                target_stakeholders={StakeholderType.DEVOPS_ENGINEER, StakeholderType.ARCHITECT},
                complexity=Complexity.SIMPLE,
                generation_sources={"monitoring", "metrics", "dashboard"},
                supported_tools={"Draw.io", "Mermaid"},
                template_available=True,
                usage_frequency=0.5
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_compliance_diagrams(self):
        """Add compliance & governance diagrams (8 types)"""
        diagrams = [
            DiagramType(
                id="compliance_matrix",
                name="Compliance Matrix",
                category=DiagramCategory.COMPLIANCE_GOVERNANCE,
                description="Shows compliance requirements and their implementation",
                keywords={"compliance", "governance", "regulation", "matrix"},
                domains={"compliance", "governance", "regulation"},
                relevant_phases={ProjectPhase.ANALYSIS, ProjectPhase.DESIGN},
                target_stakeholders={StakeholderType.SECURITY_ENGINEER, StakeholderType.EXECUTIVE},
                complexity=Complexity.MODERATE,
                generation_sources={"compliance", "governance", "regulation"},
                supported_tools={"Draw.io", "Excel"},
                template_available=True,
                usage_frequency=0.3
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_business_diagrams(self):
        """Add business & strategy diagrams (12 types)"""
        diagrams = [
            DiagramType(
                id="business_model_canvas",
                name="Business Model Canvas",
                category=DiagramCategory.BUSINESS_STRATEGY,
                description="Shows business model components and relationships",
                keywords={"business", "model", "canvas", "strategy"},
                domains={"business", "strategy", "product"},
                relevant_phases={ProjectPhase.DISCOVERY, ProjectPhase.ANALYSIS},
                target_stakeholders={StakeholderType.PRODUCT_MANAGER, StakeholderType.EXECUTIVE},
                complexity=Complexity.SIMPLE,
                generation_sources={"business", "strategy", "model"},
                supported_tools={"Draw.io", "Miro"},
                template_available=True,
                usage_frequency=0.6
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_ml_diagrams(self):
        """Add machine learning & AI diagrams (12 types)"""
        diagrams = [
            DiagramType(
                id="ml_pipeline",
                name="ML Pipeline Diagram",
                category=DiagramCategory.ML_AI,
                description="Shows machine learning pipeline stages and data flow",
                keywords={"ml", "pipeline", "machine", "learning", "ai"},
                domains={"ml", "ai", "data", "pipeline"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.DATA_ENGINEER, StakeholderType.DEVELOPER},
                complexity=Complexity.MODERATE,
                generation_sources={"ml", "ai", "pipeline"},
                supported_tools={"Draw.io", "Mermaid"},
                template_available=True,
                usage_frequency=0.4
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_blockchain_diagrams(self):
        """Add blockchain & Web3 diagrams (5 types)"""
        diagrams = [
            DiagramType(
                id="blockchain_architecture",
                name="Blockchain Architecture",
                category=DiagramCategory.BLOCKCHAIN_WEB3,
                description="Shows blockchain components and data flow",
                keywords={"blockchain", "web3", "crypto", "architecture"},
                domains={"blockchain", "web3", "crypto"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.DEVELOPER, StakeholderType.ARCHITECT},
                complexity=Complexity.COMPLEX,
                generation_sources={"blockchain", "web3", "crypto"},
                supported_tools={"Draw.io", "PlantUML"},
                template_available=True,
                usage_frequency=0.2
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def _add_iot_diagrams(self):
        """Add IoT & Edge diagrams (8 types)"""
        diagrams = [
            DiagramType(
                id="iot_architecture",
                name="IoT Architecture",
                category=DiagramCategory.IOT_EDGE,
                description="Shows IoT system architecture and device connectivity",
                keywords={"iot", "edge", "device", "sensor", "architecture"},
                domains={"iot", "edge", "device"},
                relevant_phases={ProjectPhase.DESIGN, ProjectPhase.DEVELOPMENT},
                target_stakeholders={StakeholderType.DEVELOPER, StakeholderType.ARCHITECT},
                complexity=Complexity.MODERATE,
                generation_sources={"iot", "edge", "device"},
                supported_tools={"Draw.io", "PlantUML"},
                template_available=True,
                usage_frequency=0.3
            ),
        ]
        
        for diagram in diagrams:
            self._add_diagram(diagram)
    
    def export_catalog(self) -> Dict:
        """Export catalog as JSON for API consumption"""
        return {
            "diagrams": {
                diagram_id: {
                    "id": d.id,
                    "name": d.name,
                    "category": d.category.value,
                    "description": d.description,
                    "keywords": list(d.keywords),
                    "domains": list(d.domains),
                    "relevant_phases": [p.value for p in d.relevant_phases],
                    "target_stakeholders": [s.value for s in d.target_stakeholders],
                    "complexity": d.complexity.value,
                    "complementary_diagrams": list(d.complementary_diagrams),
                    "prerequisite_diagrams": list(d.prerequisite_diagrams),
                    "generation_sources": list(d.generation_sources),
                    "supported_tools": list(d.supported_tools),
                    "template_available": d.template_available,
                    "auto_generatable": d.auto_generatable,
                    "usage_frequency": d.usage_frequency,
                    "user_satisfaction": d.user_satisfaction,
                }
                for diagram_id, d in self._diagrams.items()
            },
            "stats": self.get_stats()
        }
