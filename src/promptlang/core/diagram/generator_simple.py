from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Any
from enum import Enum
import logging

from .catalog import DiagramType
from .analyzer import ProjectContext

logger = logging.getLogger(__name__)

class DiagramFormat(Enum):
    """Output formats for diagrams"""
    SVG = "svg"
    PNG = "png"
    PDF = "pdf"

class DiagramTool(Enum):
    """Supported diagram generation tools"""
    PLANTUML = "plantuml"
    MERMAID = "mermaid"

@dataclass
class GeneratedDiagram:
    """Represents a generated diagram"""
    diagram_type: DiagramType
    tool: DiagramTool
    format: DiagramFormat
    content: str  # Base64 encoded content
    source_code: str  # Original source code
    metadata: Dict[str, Any] = field(default_factory=dict)
    generation_time: float = 0.0
    file_size: int = 0
    success: bool = True
    error_message: str = ""

class SimpleDiagramGenerator:
    """Simple template-based diagram generator"""
    
    def __init__(self):
        self.templates = {
            "system_context_plantuml": self._system_context_template(),
            "system_context_mermaid": self._system_context_mermaid_template(),
            "basic_flowchart_plantuml": self._basic_flowchart_plantuml_template(),
            "basic_flowchart_mermaid": self._basic_flowchart_template(),
            "architecture_mermaid": self._architecture_mermaid_template(),
            "sequence_mermaid": self._sequence_mermaid_template(),
            "business_model_canvas_mermaid": self._business_model_canvas_template(),
            "use_case_mermaid": self._use_case_template(),
            "system_landscape_mermaid": self._system_landscape_template(),
            "threat_model_mermaid": self._threat_model_template(),
            "swimlane_mermaid": self._swimlane_template(),
            "compliance_matrix_mermaid": self._compliance_matrix_template(),
            "c4_l1_context_mermaid": self._c4_context_template(),
            "c4_l2_container_mermaid": self._c4_container_template(),
            "c4_l3_component_mermaid": self._c4_component_template(),
            "c4_l4_code_mermaid": self._c4_code_template(),
            "hld_mermaid": self._hld_template(),
            "lld_mermaid": self._lld_template(),
            "user_flow_mermaid": self._user_flow_template(),
            "uml_class_mermaid": self._uml_class_template(),
            "uml_sequence_mermaid": self._uml_sequence_template(),
        }
    
    def get_supported_tools(self) -> List[DiagramTool]:
        """Get list of supported diagram tools"""
        return [DiagramTool.PLANTUML, DiagramTool.MERMAID]
    
    def get_supported_formats(self) -> List[DiagramFormat]:
        """Get list of supported output formats"""
        return [DiagramFormat.SVG, DiagramFormat.PNG, DiagramFormat.PDF]
    
    def _system_context_template(self) -> str:
        """Generate System Context diagram template"""
        return """@startuml
!theme plain
skinparam monochrome true
skinparam shadowing false

title System Context Diagram
{project_name}

actor "User" as user
rectangle "{project_name}" as system {
}

user --> system : Uses
@enduml"""
    
    def _basic_flowchart_template(self) -> str:
        """Generate basic flowchart template using Mermaid syntax"""
        return """graph TD
    A[Start] --> B{Process Data}
    B -->|Yes| C[Execute]
    B -->|No| D[End]
    C --> D
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px"""
    
    def _system_context_mermaid_template(self) -> str:
        """Generate System Context diagram using Mermaid syntax"""
        return """graph TB
    subgraph "{project_name} System"
        A[Core Application]
        B[Database]
        C[API Gateway]
    end
    
    U[User] --> C
    C --> A
    A --> B
    
    style U fill:#f9f,stroke:#333,stroke-width:2px
    style A fill:#bbf,stroke:#333,stroke-width:2px"""
    
    def _basic_flowchart_plantuml_template(self) -> str:
        """Generate basic flowchart template using PlantUML syntax"""
        return """@startuml
!theme plain
skinparam monochrome true

title Basic Flowchart

start
:Initialize;
if (Condition?) then (yes)
  :Process Data;
else (no)
  :End Process;
endif
stop

@enduml"""
    
    def _architecture_mermaid_template(self) -> str:
        """Generate architecture diagram using Mermaid syntax"""
        return """graph TB
    subgraph "Frontend Layer"
        FE[React App]
        UI[UI Components]
    end
    
    subgraph "Backend Layer"
        API[REST API]
        AUTH[Authentication Service]
        BIZ[Business Logic]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL)]
        CACHE[(Redis Cache)]
    end
    
    FE --> API
    UI --> API
    API --> AUTH
    API --> BIZ
    BIZ --> DB
    AUTH --> CACHE
    
    style FE fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style DB fill:#f3e5f5,stroke:#4a148c,stroke-width:2px"""
    
    def _sequence_mermaid_template(self) -> str:
        """Generate sequence diagram using Mermaid syntax"""
        return """sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Database
    
    User->>Frontend: Login Request
    Frontend->>API: POST /auth/login
    API->>Database: Validate Credentials
    Database-->>API: User Data
    API-->>Frontend: JWT Token
    Frontend-->>User: Login Success"""
    
    def _business_model_canvas_template(self) -> str:
        """Generate Business Model Canvas diagram"""
        return """graph TB
    subgraph "Key Partners"
        P1[Partner 1]
        P2[Partner 2]
    end
    
    subgraph "Key Activities"
        A1[Activity 1]
        A2[Activity 2]
    end
    
    subgraph "Key Resources"
        R1[Resource 1]
        R2[Resource 2]
    end
    
    subgraph "Value Propositions"
        V1[Value 1]
        V2[Value 2]
    end
    
    subgraph "Customer Relationships"
        C1[Support]
        C2[Community]
    end
    
    subgraph "Channels"
        CH1[Channel 1]
        CH2[Channel 2]
    end
    
    subgraph "Customer Segments"
        S1[Segment 1]
        S2[Segment 2]
    end
    
    subgraph "Cost Structure"
        CS1[Cost 1]
        CS2[Cost 2]
    end
    
    subgraph "Revenue Streams"
        RS1[Revenue 1]
        RS2[Revenue 2]
    end
    
    P1 --> A1
    A1 --> R1
    R1 --> V1
    V1 --> C1
    C1 --> CH1
    CH1 --> S1
    S1 --> RS1
    RS1 --> CS1"""
    
    def _use_case_template(self) -> str:
        """Generate Use Case diagram"""
        return """graph TD
    User[User] --> UC1[Use Case 1]
    User --> UC2[Use Case 2]
    User --> UC3[Use Case 3]
    
    Admin[Admin] --> UC4[Use Case 4]
    Admin --> UC5[Use Case 5]
    
    System[{project_name}] --> UC1
    System --> UC2
    System --> UC3
    System --> UC4
    System --> UC5
    
    style User fill:#e1f5fe
    style Admin fill:#f3e5f5
    style System fill:#e8f5e8"""
    
    def _system_landscape_template(self) -> str:
        """Generate System Landscape diagram"""
        return """graph TB
    subgraph "External Systems"
        ES1[External System 1]
        ES2[External System 2]
    end
    
    subgraph "Security Layer"
        SL[Security Gateway]
        FW[Firewall]
    end
    
    subgraph "Application Layer"
        APP1[Application 1]
        APP2[Application 2]
        APP3[Application 3]
    end
    
    subgraph "Data Layer"
        DB1[(Database 1)]
        DB2[(Database 2)]
        CACHE[(Cache)]
    end
    
    ES1 --> SL
    ES2 --> SL
    SL --> FW
    FW --> APP1
    FW --> APP2
    FW --> APP3
    APP1 --> DB1
    APP2 --> DB2
    APP3 --> CACHE"""
    
    def _threat_model_template(self) -> str:
        """Generate Threat Model diagram"""
        return """graph TD
    subgraph "Threat Sources"
        TS1[External Attacker]
        TS2[Insider Threat]
        TS3[Malicious Code]
    end
    
    subgraph "Attack Vectors"
        AV1[Network Attack]
        AV2[Social Engineering]
        AV3[Physical Access]
    end
    
    subgraph "Vulnerabilities"
        VUL1[Software Bug]
        VUL2[Weak Password]
        VUL3[Misconfiguration]
    end
    
    subgraph "Controls"
        CTRL1[Firewall]
        CTRL2[Encryption]
        CTRL3[Access Control]
    end
    
    TS1 --> AV1
    TS2 --> AV2
    TS3 --> AV3
    AV1 --> VUL1
    AV2 --> VUL2
    AV3 --> VUL3
    VUL1 --> CTRL1
    VUL2 --> CTRL2
    VUL3 --> CTRL3"""
    
    def _swimlane_template(self) -> str:
        """Generate Swimlane diagram"""
        return """graph TD
    subgraph "User"
        U1[Start Process]
        U2[Submit Request]
        U3[Receive Result]
    end
    
    subgraph "System"
        S1[Validate Request]
        S2[Process Data]
        S3[Generate Response]
    end
    
    subgraph "Database"
        D1[Store Request]
        D2[Query Data]
        D3[Update Records]
    end
    
    U1 --> U2
    U2 --> S1
    S1 --> S2
    S2 --> D1
    D1 --> D2
    D2 --> S3
    S3 --> D3
    D3 --> U3"""
    
    def _compliance_matrix_template(self) -> str:
        """Generate Compliance Matrix diagram"""
        return """graph LR
    subgraph "Regulations"
        GDPR[GDPR]
        HIPAA[HIPAA]
        SOX[Sarbanes-Oxley]
    end
    
    subgraph "Controls"
        C1[Data Protection]
        C2[Access Control]
        C3[Audit Trail]
        C4[Encryption]
    end
    
    subgraph "Status"
        S1[✓ Compliant]
        S2[⚠ Partial]
        S3[✗ Non-Compliant]
    end
    
    GDPR --> C1
    GDPR --> C2
    GDPR --> C4
    HIPAA --> C1
    HIPAA --> C2
    HIPAA --> C3
    SOX --> C2
    SOX --> C3
    SOX --> C4
    
    C1 --> S1
    C2 --> S1
    C3 --> S2
    C4 --> S1"""
    
    def _c4_context_template(self) -> str:
        """Generate C4 Level 1 System Context diagram"""
        return """graph TB
    subgraph "{project_name} System"
        API[API Gateway]
        APP[Application]
        DB[(Database)]
    end
    
    User[User] --> API
    Admin[Admin] --> API
    External[External System] --> API
    
    API --> APP
    APP --> DB
    
    style User fill:#e1f5fe
    style Admin fill:#f3e5f5
    style External fill:#fff3e0"""
    
    def _user_flow_template(self) -> str:
        """Generate User Flow diagram"""
        return """graph TD
    A[User lands on page] --> B{Login Required?}
    B -->|Yes| C[Enter credentials]
    B -->|No| D[Browse content]
    C --> E{Valid credentials?}
    E -->|Yes| F[Access dashboard]
    E -->|No| G[Show error]
    G --> C
    F --> H[View data]
    H --> I[Perform action]
    I --> J[Log out]
    J --> K[User leaves]
    D --> L[Continue browsing]
    L --> K"""
    
    def _c4_container_template(self) -> str:
        """Generate C4 Level 2 Container diagram"""
        return """graph TB
    subgraph "Web Browser"
        UI[Web UI]
    end
    
    subgraph "Application Container"
        API[API Gateway]
        APP1[Service 1]
        APP2[Service 2]
    end
    
    subgraph "Database Container"
        DB1[(Primary DB)]
        DB2[(Cache)]
    end
    
    UI --> API
    API --> APP1
    API --> APP2
    APP1 --> DB1
    APP2 --> DB2
    APP2 --> DB1"""
    
    def _c4_component_template(self) -> str:
        """Generate C4 Level 3 Component diagram"""
        return """graph TB
    subgraph "WebApp"
        UI[React Components]
        Router[Router]
    end
    
    subgraph "API"
        Controller[Controller]
        Service[Business Logic]
        Repository[Data Access]
    end
    
    subgraph "Database"
        Tables[Tables]
        Indexes[Indexes]
    end
    
    UI --> Router
    Router --> Controller
    Controller --> Service
    Service --> Repository
    Repository --> Tables
    Repository --> Indexes"""
    
    def _c4_code_template(self) -> str:
        """Generate C4 Level 4 Code diagram"""
        return """graph LR
    subgraph "Frontend Code"
        TS[TypeScript]
        JSX[React JSX]
        CSS[CSS Styles]
    end
    
    subgraph "Backend Code"
        PY[Python]
        SQL[SQL Queries]
        CONFIG[Config Files]
    end
    
    subgraph "Infrastructure"
        DOCKER[Dockerfile]
        K8S[Kubernetes YAML]
    end
    
    TS --> JSX
    JSX --> CSS
    PY --> SQL
    PY --> CONFIG
    DOCKER --> K8S"""
    
    def _hld_template(self) -> str:
        """Generate High-Level Design diagram"""
        return """graph TB
    subgraph "Presentation Layer"
        UI[User Interface]
        API_GW[API Gateway]
    end
    
    subgraph "Business Logic Layer"
        AUTH[Authentication Service]
        BUSINESS[Business Service]
        WORKFLOW[Workflow Engine]
    end
    
    subgraph "Data Layer"
        DB[(Database)]
        CACHE[(Cache)]
        QUEUE[Message Queue]
    end
    
    UI --> API_GW
    API_GW --> AUTH
    API_GW --> BUSINESS
    AUTH --> DB
    BUSINESS --> DB
    BUSINESS --> CACHE
    WORKFLOW --> QUEUE"""
    
    def _lld_template(self) -> str:
        """Generate Low-Level Design diagram"""
        return """graph TB
    subgraph "Controllers"
        USER_CTRL[UserController]
        AUTH_CTRL[AuthController]
    end
    
    subgraph "Services"
        USER_SVC[UserService]
        AUTH_SVC[AuthService]
    end
    
    subgraph "Repositories"
        USER_REPO[UserRepository]
        AUTH_REPO[AuthRepository]
    end
    
    subgraph "Models"
        USER_MODEL[UserModel]
        AUTH_MODEL[AuthModel]
    end
    
    USER_CTRL --> USER_SVC
    AUTH_CTRL --> AUTH_SVC
    USER_SVC --> USER_REPO
    AUTH_SVC --> AUTH_REPO
    USER_REPO --> USER_MODEL
    AUTH_REPO --> AUTH_MODEL"""
    
    def _uml_class_template(self) -> str:
        """Generate UML Class diagram"""
        return """classDiagram
    class User {
        +id: String
        +name: String
        +email: String
        +login()
        +logout()
    }
    
    class Product {
        +id: String
        +name: String
        +price: Float
        +getDetails()
        +updatePrice()
    }
    
    class Order {
        +id: String
        +userId: String
        +productId: String
        +quantity: Integer
        +create()
        +cancel()
    }
    
    User "1" -- "*" Order : places
    Order "*" -- "1" Product : contains"""
    
    def _uml_sequence_template(self) -> str:
        """Generate UML Sequence diagram"""
        return """sequenceDiagram
    participant User
    participant UI
    participant Controller
    participant Service
    participant Database
    
    User->>UI: Login Request
    UI->>Controller: Submit Credentials
    Controller->>Service: Validate User
    Service->>Database: Query User
    Database-->>Service: User Data
    Service-->>Controller: Validation Result
    Controller-->>UI: Login Response
    UI-->>User: Show Dashboard"""
    
    def generate_diagram(self, diagram_type, context, tool=None, format=DiagramFormat.SVG):
        """Generate a diagram using specified tool and format"""
        
        # Select tool
        if not tool:
            if "plantuml" in diagram_type.id.lower():
                tool = DiagramTool.PLANTUML
            else:
                tool = DiagramTool.MERMAID
        elif isinstance(tool, str):
            # Convert string to enum
            if tool.lower() == "plantuml":
                tool = DiagramTool.PLANTUML
            elif tool.lower() == "mermaid":
                tool = DiagramTool.MERMAID
            else:
                tool = DiagramTool.MERMAID
        
        # Get template
        template_key = f"{diagram_type.id}_{tool.value}"
        template = self.templates.get(template_key)
        
        if template:
            logger.info(f"Using template for {diagram_type.name}")
            source_code = template.format(project_name=context.project_name)
        else:
            # Basic fallback
            logger.info(f"Using basic template for {diagram_type.name}")
            if tool == DiagramTool.PLANTUML:
                source_code = self._system_context_template().format(project_name=context.project_name)
            else:
                source_code = self._basic_flowchart_template()
        
        # Create simple result
        return GeneratedDiagram(
            diagram_type=diagram_type,
            tool=tool,
            format=format,
            content=source_code,
            source_code=source_code,
            metadata={
                "template_used": template is not None,
                "generation_time": 0.1,
                "file_size": len(source_code.encode()) if isinstance(source_code, str) else 0
            },
            generation_time=0.1,
            file_size=len(source_code.encode()) if isinstance(source_code, str) else 0,
            success=True,
            error_message=""
        )
    
    def generate_batch(self, diagram_types, context, preferred_tool=None):
        """Generate multiple diagrams"""
        generated = []
        for diagram_type in diagram_types:
            try:
                diagram = self.generate_diagram(diagram_type, context, preferred_tool)
                generated.append(diagram)
            except Exception as e:
                logger.error(f"Failed to generate {diagram_type.name}: {e}")
                # Create a failed diagram
                failed_diagram = GeneratedDiagram(
                    diagram_type=diagram_type,
                    tool=preferred_tool or DiagramTool.MERMAID,
                    format=DiagramFormat.SVG,
                    content="",
                    source_code="",
                    metadata={"error": str(e)},
                    generation_time=0.0,
                    file_size=0,
                    success=False,
                    error_message=str(e)
                )
                generated.append(failed_diagram)
        return generated
    
    def export_diagrams(self, diagrams, export_directory):
        """Export diagrams to files"""
        import os
        os.makedirs(export_directory, exist_ok=True)
        
        exported_files = []
        for diagram in diagrams:
            if diagram.success:
                filename = f"{diagram.diagram_type.id}.{diagram.format.value}"
                filepath = os.path.join(export_directory, filename)
                
                with open(filepath, 'w') as f:
                    f.write(diagram.content)
                
                exported_files.append(filepath)
        
        return exported_files
