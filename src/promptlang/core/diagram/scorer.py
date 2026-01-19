"""
Relevance Scoring Algorithm - Scores diagram types based on project context
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from enum import Enum
import logging

from .catalog import DiagramType, DiagramCategory, ProjectPhase, StakeholderType
from .analyzer import ProjectContext, ProjectType, ArchitecturePattern

logger = logging.getLogger(__name__)


class SelectionTier(Enum):
    """Selection tiers for diagram recommendations"""
    MUST_GENERATE = "must_generate"  # >90% relevance
    SHOULD_GENERATE = "should_generate"  # 70-90% relevance
    COULD_GENERATE = "could_generate"  # 50-70% relevance
    OPTIONAL = "optional"  # <50% relevance


@dataclass
class DiagramRecommendation:
    """Recommendation for a specific diagram type"""
    diagram: DiagramType
    relevance_score: float
    selection_tier: SelectionTier
    reasoning: List[str] = field(default_factory=list)
    confidence: float = 0.0
    generation_priority: int = 0
    estimated_effort: str = "medium"
    prerequisites_met: bool = True
    complementary_diagrams: List[str] = field(default_factory=list)


@dataclass
class ScoringWeights:
    """Weights for different scoring factors"""
    domain_match: float = 0.30
    entity_overlap: float = 0.25
    phase_match: float = 0.20
    complementary_bonus: float = 0.15
    stakeholder_match: float = 0.10
    
    # Additional weights
    technology_match: float = 0.05
    complexity_penalty: float = 0.05
    usage_bonus: float = 0.03


class RelevanceScorer:
    """Scores diagram relevance based on project context"""
    
    def __init__(self, weights: Optional[ScoringWeights] = None):
        self.weights = weights or ScoringWeights()
        
        # Domain mappings for better matching
        self._domain_mappings = self._init_domain_mappings()
        
        # Technology mappings
        self._technology_mappings = self._init_technology_mappings()
        
        # Phase importance weights
        self._phase_importance = self._init_phase_importance()
        
        # Stakeholder importance weights
        self._stakeholder_importance = self._init_stakeholder_importance()
    
    def score_diagrams(self, context: ProjectContext, catalog_diagrams: List[DiagramType]) -> List[DiagramRecommendation]:
        """Score all diagrams against the project context"""
        recommendations = []
        
        for diagram in catalog_diagrams:
            recommendation = self._score_single_diagram(diagram, context)
            recommendations.append(recommendation)
        
        # Sort by relevance score
        recommendations.sort(key=lambda r: r.relevance_score, reverse=True)
        
        # Assign generation priorities
        self._assign_priorities(recommendations)
        
        return recommendations
    
    def _score_single_diagram(self, diagram: DiagramType, context: ProjectContext) -> DiagramRecommendation:
        """Score a single diagram against the project context"""
        score = 0.0
        reasoning = []
        
        # Domain matching (30% weight)
        domain_score, domain_reasoning = self._calculate_domain_score(diagram, context)
        score += domain_score * self.weights.domain_match
        reasoning.extend(domain_reasoning)
        
        # Entity overlap (25% weight)
        entity_score, entity_reasoning = self._calculate_entity_score(diagram, context)
        score += entity_score * self.weights.entity_overlap
        reasoning.extend(entity_reasoning)
        
        # Phase matching (20% weight)
        phase_score, phase_reasoning = self._calculate_phase_score(diagram, context)
        score += phase_score * self.weights.phase_match
        reasoning.extend(phase_reasoning)
        
        # Complementary bonus (15% weight)
        complementary_score, complementary_reasoning = self._calculate_complementary_score(diagram, context)
        score += complementary_score * self.weights.complementary_bonus
        reasoning.extend(complementary_reasoning)
        
        # Stakeholder matching (10% weight)
        stakeholder_score, stakeholder_reasoning = self._calculate_stakeholder_score(diagram, context)
        score += stakeholder_score * self.weights.stakeholder_match
        reasoning.extend(stakeholder_reasoning)
        
        # Technology matching (5% weight)
        tech_score, tech_reasoning = self._calculate_technology_score(diagram, context)
        score += tech_score * self.weights.technology_match
        reasoning.extend(tech_reasoning)
        
        # Complexity penalty (5% weight)
        complexity_penalty, complexity_reasoning = self._calculate_complexity_penalty(diagram, context)
        score -= complexity_penalty * self.weights.complexity_penalty
        reasoning.extend(complexity_reasoning)
        
        # Usage bonus (3% weight)
        usage_bonus, usage_reasoning = self._calculate_usage_bonus(diagram)
        score += usage_bonus * self.weights.usage_bonus
        reasoning.extend(usage_reasoning)
        
        # Ensure score is within bounds
        score = max(0.0, min(1.0, score))
        
        # Determine selection tier
        tier = self._determine_selection_tier(score)
        
        # Calculate confidence
        confidence = self._calculate_confidence(diagram, context)
        
        # Check prerequisites
        prerequisites_met = self._check_prerequisites(diagram, context)
        
        # Estimate effort
        effort = self._estimate_effort(diagram, context)
        
        return DiagramRecommendation(
            diagram=diagram,
            relevance_score=score,
            selection_tier=tier,
            reasoning=reasoning,
            confidence=confidence,
            prerequisites_met=prerequisites_met,
            estimated_effort=effort,
            complementary_diagrams=list(diagram.complementary_diagrams)
        )
    
    def _calculate_domain_score(self, diagram: DiagramType, context: ProjectContext) -> Tuple[float, List[str]]:
        """Calculate domain matching score"""
        if not context.domains or not diagram.domains:
            return 0.0, []
        
        # Direct domain matches
        direct_matches = len(context.domains.intersection(diagram.domains))
        
        # Mapped domain matches
        mapped_matches = 0
        for context_domain in context.domains:
            if context_domain in self._domain_mappings:
                mapped_domains = self._domain_mappings[context_domain]
                mapped_matches += len(mapped_domains.intersection(diagram.domains))
        
        total_matches = direct_matches + mapped_matches
        max_possible = len(context.domains) + len(diagram.domains)
        
        if max_possible == 0:
            return 0.0, []
        
        score = total_matches / max_possible
        reasoning = []
        
        if direct_matches > 0:
            reasoning.append(f"Direct domain match: {', '.join(context.domains.intersection(diagram.domains))}")
        
        if mapped_matches > 0:
            reasoning.append(f"Mapped domain match: {mapped_matches} related domains")
        
        return score, reasoning
    
    def _calculate_entity_score(self, diagram: DiagramType, context: ProjectContext) -> Tuple[float, List[str]]:
        """Calculate entity overlap score"""
        if not context.entities:
            return 0.0, []
        
        # Check if diagram keywords match entities
        entity_matches = 0
        matched_entities = set()
        
        for entity in context.entities:
            entity_lower = entity.lower()
            for keyword in diagram.keywords:
                if keyword.lower() in entity_lower or entity_lower in keyword.lower():
                    entity_matches += 1
                    matched_entities.add(entity)
        
        if len(context.entities) == 0:
            return 0.0, []
        
        score = entity_matches / len(context.entities)
        reasoning = []
        
        if matched_entities:
            reasoning.append(f"Entity matches: {', '.join(list(matched_entities)[:3])}")
        
        return score, reasoning
    
    def _calculate_phase_score(self, diagram: DiagramType, context: ProjectContext) -> Tuple[float, List[str]]:
        """Calculate phase matching score"""
        if not diagram.relevant_phases:
            return 0.0, []
        
        # Check if current phase is relevant
        phase_match = context.project_phase in diagram.relevant_phases
        
        # Apply phase importance weighting
        phase_weight = self._phase_importance.get(context.project_phase, 1.0)
        
        score = 1.0 if phase_match else 0.0
        score *= phase_weight
        
        reasoning = []
        
        if phase_match:
            reasoning.append(f"Relevant for {context.project_phase.value} phase")
        else:
            reasoning.append(f"Not typically used in {context.project_phase.value} phase")
        
        return score, reasoning
    
    def _calculate_complementary_score(self, diagram: DiagramType, context: ProjectContext) -> Tuple[float, List[str]]:
        """Calculate complementary diagram score"""
        if not diagram.complementary_diagrams:
            return 0.0, []
        
        # This would require knowing which other diagrams are being generated
        # For now, give a small bonus for having complementary diagrams
        score = min(0.5, len(diagram.complementary_diagrams) * 0.1)
        reasoning = []
        
        if diagram.complementary_diagrams:
            reasoning.append(f"Has {len(diagram.complementary_diagrams)} complementary diagrams")
        
        return score, reasoning
    
    def _calculate_stakeholder_score(self, diagram: DiagramType, context: ProjectContext) -> Tuple[float, List[str]]:
        """Calculate stakeholder matching score"""
        if not context.stakeholders or not diagram.target_stakeholders:
            return 0.0, []
        
        stakeholder_matches = len(context.stakeholders.intersection(diagram.target_stakeholders))
        
        if len(context.stakeholders) == 0:
            return 0.0, []
        
        score = stakeholder_matches / len(context.stakeholders)
        reasoning = []
        
        if stakeholder_matches > 0:
            matched_stakeholders = context.stakeholders.intersection(diagram.target_stakeholders)
            reasoning.append(f"Relevant for {', '.join([s.value for s in matched_stakeholders])}")
        
        return score, reasoning
    
    def _calculate_technology_score(self, diagram: DiagramType, context: ProjectContext) -> Tuple[float, List[str]]:
        """Calculate technology matching score"""
        score = 0.0
        reasoning = []
        
        # Check if diagram supports the project's technologies
        tech_matches = 0
        
        # Language matches
        if context.technology_stack.languages:
            for lang in context.technology_stack.languages:
                if lang.lower() in [k.lower() for k in diagram.keywords]:
                    tech_matches += 1
        
        # Framework matches
        if context.technology_stack.frameworks:
            for framework in context.technology_stack.frameworks:
                if framework.lower() in [k.lower() for k in diagram.keywords]:
                    tech_matches += 1
        
        # Calculate score
        total_tech = len(context.technology_stack.languages) + len(context.technology_stack.frameworks)
        if total_tech > 0:
            score = tech_matches / total_tech
            if tech_matches > 0:
                reasoning.append(f"Supports project technologies")
        
        return score, reasoning
    
    def _calculate_complexity_penalty(self, diagram: DiagramType, context: ProjectContext) -> Tuple[float, List[str]]:
        """Calculate complexity penalty"""
        complexity_scores = {
            "simple": 0.0,
            "moderate": 0.1,
            "complex": 0.2,
            "expert": 0.3
        }
        
        penalty = complexity_scores.get(diagram.complexity.value, 0.1)
        reasoning = []
        
        if diagram.complexity.value != "simple":
            reasoning.append(f"Complexity penalty for {diagram.complexity.value} diagram")
        
        return penalty, reasoning
    
    def _calculate_usage_bonus(self, diagram: DiagramType) -> Tuple[float, List[str]]:
        """Calculate usage frequency bonus"""
        score = diagram.usage_frequency * 0.5  # Scale down the bonus
        reasoning = []
        
        if diagram.usage_frequency > 0.7:
            reasoning.append("High usage frequency diagram")
        
        return score, reasoning
    
    def _determine_selection_tier(self, score: float) -> SelectionTier:
        """Determine selection tier based on score"""
        if score >= 0.70:
            return SelectionTier.MUST_GENERATE
        elif score >= 0.50:
            return SelectionTier.SHOULD_GENERATE
        elif score >= 0.30:
            return SelectionTier.COULD_GENERATE
        else:
            return SelectionTier.OPTIONAL
    
    def _calculate_confidence(self, diagram: DiagramType, context: ProjectContext) -> float:
        """Calculate confidence in the scoring"""
        confidence_factors = []
        
        # Domain confidence
        if context.domains and diagram.domains:
            domain_confidence = len(context.domains.intersection(diagram.domains)) / len(diagram.domains)
            confidence_factors.append(domain_confidence)
        
        # Phase confidence
        if context.project_phase in diagram.relevant_phases:
            confidence_factors.append(0.8)
        
        # Stakeholder confidence
        if context.stakeholders and diagram.target_stakeholders:
            stakeholder_confidence = len(context.stakeholders.intersection(diagram.target_stakeholders)) / len(diagram.target_stakeholders)
            confidence_factors.append(stakeholder_confidence)
        
        # Technology confidence
        if context.technology_stack.languages or context.technology_stack.frameworks:
            tech_confidence = 0.5  # Default tech confidence
            confidence_factors.append(tech_confidence)
        
        if confidence_factors:
            return sum(confidence_factors) / len(confidence_factors)
        
        return 0.5  # Default confidence
    
    def _check_prerequisites(self, diagram: DiagramType, context: ProjectContext) -> bool:
        """Check if prerequisites are met"""
        if not diagram.prerequisite_diagrams:
            return True
        
        # In a real implementation, this would check if prerequisite diagrams
        # are already generated or planned
        # For now, assume prerequisites are met
        return True
    
    def _estimate_effort(self, diagram: DiagramType, context: ProjectContext) -> str:
        """Estimate generation effort"""
        effort_scores = {
            "simple": "low",
            "moderate": "medium",
            "complex": "high",
            "expert": "very_high"
        }
        
        base_effort = effort_scores.get(diagram.complexity.value, "medium")
        
        # Adjust based on available information
        if context.source_files:
            return base_effort
        else:
            # Increase effort if no source information is available
            effort_levels = ["low", "medium", "high", "very_high"]
            current_index = effort_levels.index(base_effort)
            return effort_levels[min(current_index + 1, len(effort_levels) - 1)]
    
    def _assign_priorities(self, recommendations: List[DiagramRecommendation]):
        """Assign generation priorities to recommendations"""
        for i, rec in enumerate(recommendations):
            # Base priority from score
            if rec.selection_tier == SelectionTier.MUST_GENERATE:
                base_priority = 100
            elif rec.selection_tier == SelectionTier.SHOULD_GENERATE:
                base_priority = 80
            elif rec.selection_tier == SelectionTier.COULD_GENERATE:
                base_priority = 60
            else:
                base_priority = 40
            
            # Adjust for confidence
            priority_adjustment = rec.confidence * 20
            
            # Adjust for effort (lower effort = higher priority)
            effort_penalty = {
                "low": 0,
                "medium": -5,
                "high": -10,
                "very_high": -15
            }.get(rec.estimated_effort, -5)
            
            rec.generation_priority = int(base_priority + priority_adjustment + effort_penalty - i * 0.1)
    
    def _init_domain_mappings(self) -> Dict[str, Set[str]]:
        """Initialize domain mappings for better matching"""
        return {
            "finance": {"banking", "fintech", "payments", "trading"},
            "healthcare": {"medical", "pharma", "wellness", "clinical"},
            "retail": {"ecommerce", "shopping", "sales", "inventory"},
            "education": {"learning", "training", "academic", "school"},
            "government": {"public", "civic", "administrative", "policy"},
            "manufacturing": {"production", "factory", "industrial", "supply"},
            "logistics": {"transportation", "shipping", "warehouse", "delivery"},
        }
    
    def _init_technology_mappings(self) -> Dict[str, Set[str]]:
        """Initialize technology mappings"""
        return {
            "javascript": {"web", "frontend", "browser", "node"},
            "python": {"backend", "api", "data", "ml", "ai"},
            "java": {"enterprise", "backend", "android", "server"},
            "react": {"frontend", "web", "ui", "component"},
            "django": {"backend", "web", "api", "python"},
            "spring": {"backend", "enterprise", "java", "microservices"},
            "aws": {"cloud", "infrastructure", "deployment", "scaling"},
            "docker": {"container", "deployment", "devops", "microservices"},
        }
    
    def _init_phase_importance(self) -> Dict[ProjectPhase, float]:
        """Initialize phase importance weights"""
        return {
            ProjectPhase.DISCOVERY: 1.2,  # High importance for understanding
            ProjectPhase.ANALYSIS: 1.1,  # High importance for requirements
            ProjectPhase.DESIGN: 1.0,    # Standard importance
            ProjectPhase.DEVELOPMENT: 0.9,  # Lower importance (already decided)
            ProjectPhase.TESTING: 0.8,    # Lower importance
            ProjectPhase.DEPLOYMENT: 0.7,  # Lower importance
            ProjectPhase.MAINTENANCE: 0.6,  # Lower importance
            ProjectPhase.RETIREMENT: 0.5,  # Lowest importance
        }
    
    def _init_stakeholder_importance(self) -> Dict[StakeholderType, float]:
        """Initialize stakeholder importance weights"""
        return {
            StakeholderType.ARCHITECT: 1.2,      # High importance for technical diagrams
            StakeholderType.PRODUCT_MANAGER: 1.1, # High importance for business diagrams
            StakeholderType.DEVELOPER: 1.0,       # Standard importance
            StakeholderType.EXECUTIVE: 0.9,      # Lower importance (high-level)
            StakeholderType.QA_ENGINEER: 0.8,     # Lower importance
            StakeholderType.DEVOPS_ENGINEER: 0.8, # Lower importance
            StakeholderType.SECURITY_ENGINEER: 0.7, # Lower importance
            StakeholderType.BUSINESS_ANALYST: 0.7, # Lower importance
            StakeholderType.UX_DESIGNER: 0.6,     # Lower importance
            StakeholderType.DATA_ENGINEER: 0.6,   # Lower importance
        }
    
    def get_recommendations_summary(self, recommendations: List[DiagramRecommendation]) -> Dict:
        """Get summary of recommendations"""
        summary = {
            "total_diagrams": len(recommendations),
            "by_tier": {
                "must_generate": 0,
                "should_generate": 0,
                "could_generate": 0,
                "optional": 0
            },
            "by_category": {},
            "average_score": 0.0,
            "top_recommendations": []
        }
        
        scores = []
        
        for rec in recommendations:
            # Count by tier
            summary["by_tier"][rec.selection_tier.value] += 1
            
            # Count by category
            category = rec.diagram.category.value
            if category not in summary["by_category"]:
                summary["by_category"][category] = 0
            summary["by_category"][category] += 1
            
            # Collect scores
            scores.append(rec.relevance_score)
        
        # Calculate average score
        if scores:
            summary["average_score"] = sum(scores) / len(scores)
        
        # Get top recommendations
        summary["top_recommendations"] = [
            {
                "id": rec.diagram.id,
                "name": rec.diagram.name,
                "score": rec.relevance_score,
                "tier": rec.selection_tier.value,
                "reasoning": rec.reasoning[:3]  # Top 3 reasons
            }
            for rec in recommendations[:10]
        ]
        
        return summary
