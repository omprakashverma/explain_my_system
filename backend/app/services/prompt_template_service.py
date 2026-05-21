from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from fastapi import HTTPException, status

from backend.app.agents.qa_agent import qa_agent
from backend.app.models.request_models import QuestionScope
from backend.app.storage.repository_store import repository_store


@dataclass(frozen=True)
class PromptTemplate:
    id: str
    title: str
    category: str
    description: str
    prompt_template: str
    output_format: str = "markdown"
    scope: str = QuestionScope.REPOSITORY


PROMPT_TEMPLATES: tuple[PromptTemplate, ...] = (
    PromptTemplate(
        id="architecture_overview",
        title="Explain repository architecture",
        category="Architecture",
        description="Summarize the main layers, modules, and architectural boundaries.",
        prompt_template=(
            "Analyze the entire repository and explain the architecture. Cover the main layers, "
            "key modules, how responsibilities are split, and where the most important entrypoints live. "
            "Reference concrete file paths and highlight architectural strengths or risks."
        ),
    ),
    PromptTemplate(
        id="architecture_diagram",
        title="Generate architecture diagram",
        category="Architecture",
        description="Produce a repository-level Mermaid architecture diagram with explanation.",
        prompt_template=(
            "Analyze the whole repository and generate a Mermaid diagram that shows the main modules, "
            "data flow, and service boundaries. Return a fenced ```mermaid``` block first, then a short "
            "written explanation with referenced files and notable interactions."
        ),
        output_format="mermaid",
    ),
    PromptTemplate(
        id="module_interaction_flow",
        title="Explain module interaction flow",
        category="Architecture",
        description="Trace how major modules collaborate across the repository.",
        prompt_template=(
            "Analyze the repository and explain how modules interact. Focus on module boundaries, call flow, "
            "cross-file dependencies, and where tightly coupled interactions appear. Include referenced files."
        ),
    ),
    PromptTemplate(
        id="dependency_flow",
        title="Explain dependency flow",
        category="Architecture",
        description="Describe internal and external dependency relationships.",
        prompt_template=(
            "Analyze the repository and explain dependency flow across layers and modules. Cover internal module "
            "dependencies, important third-party libraries, and how data moves between components. Include risks "
            "or recommendations where dependencies are hard to reason about."
        ),
    ),
    PromptTemplate(
        id="service_communication",
        title="Explain service communication",
        category="Architecture",
        description="Show how services, APIs, and processing layers communicate.",
        prompt_template=(
            "Analyze the repository and explain service communication patterns. Describe API entrypoints, service "
            "layers, orchestration flow, and any background or helper processes. Reference files and interaction paths."
        ),
    ),
    PromptTemplate(
        id="class_diagram",
        title="Generate class diagram",
        category="UML",
        description="Produce a Mermaid class diagram for the most important classes or models.",
        prompt_template=(
            "Analyze the repository and generate a Mermaid class diagram for the most important classes, models, "
            "or core objects. Return a fenced ```mermaid``` block first, then explain the major relationships and "
            "any limitations if the codebase is not class-heavy."
        ),
        output_format="mermaid",
    ),
    PromptTemplate(
        id="inheritance_hierarchy",
        title="Explain inheritance hierarchy",
        category="UML",
        description="Describe inheritance and composition relationships across the codebase.",
        prompt_template=(
            "Analyze the repository and explain the inheritance hierarchy and composition patterns. Identify parent "
            "classes, subclasses, interfaces, or structural alternatives, and reference the relevant files."
        ),
    ),
    PromptTemplate(
        id="design_patterns",
        title="Identify design patterns used",
        category="UML",
        description="Point out architectural and implementation patterns in use.",
        prompt_template=(
            "Analyze the repository and identify design patterns or recurring architectural patterns in use. "
            "For each pattern, explain where it appears, why it fits, and which files show the evidence."
        ),
    ),
    PromptTemplate(
        id="component_diagram",
        title="Generate component diagram",
        category="UML",
        description="Produce a high-level Mermaid component diagram for major modules.",
        prompt_template=(
            "Analyze the repository and generate a Mermaid component diagram showing major modules, services, "
            "and dependencies. Return a fenced ```mermaid``` block first, followed by a concise explanation."
        ),
        output_format="mermaid",
    ),
    PromptTemplate(
        id="api_flow",
        title="Explain API flow",
        category="Backend",
        description="Trace how API requests move through the backend.",
        prompt_template=(
            "Analyze the repository and explain the API flow end to end. Cover routes, controllers, services, "
            "validation, and how responses are produced. Reference important files and request paths."
        ),
    ),
    PromptTemplate(
        id="request_lifecycle",
        title="Trace request lifecycle",
        category="Backend",
        description="Walk through request handling from entrypoint to response.",
        prompt_template=(
            "Analyze the repository and trace the request lifecycle from entrypoint to final response. Mention "
            "middleware, routing, validation, services, persistence, and error handling. Include file references."
        ),
    ),
    PromptTemplate(
        id="authentication_flow",
        title="Explain authentication flow",
        category="Backend",
        description="Describe login, auth checks, session handling, and protected routes.",
        prompt_template=(
            "Analyze the repository and explain the authentication flow. Cover credential handling, password "
            "storage, session or token issuance, authorization checks, and protected routes. Include referenced files."
        ),
    ),
    PromptTemplate(
        id="database_interaction",
        title="Explain database interaction flow",
        category="Backend",
        description="Summarize how the repository reads, writes, and organizes persistent data.",
        prompt_template=(
            "Analyze the repository and explain database interaction flow. Describe data models, persistence "
            "boundaries, queries or storage helpers, migrations or schema evolution, and any consistency risks."
        ),
    ),
    PromptTemplate(
        id="frontend_architecture",
        title="Explain frontend architecture",
        category="Frontend",
        description="Summarize the frontend structure, state boundaries, and UI composition.",
        prompt_template=(
            "Analyze the repository and explain the frontend architecture. Cover component structure, pages, "
            "state management, service layers, and how the UI talks to the backend. Include file references."
        ),
    ),
    PromptTemplate(
        id="routing_flow",
        title="Explain routing flow",
        category="Frontend",
        description="Describe how navigation and route handling are structured.",
        prompt_template=(
            "Analyze the repository and explain the routing flow. Cover page entrypoints, route organization, "
            "navigation patterns, and how route-specific data or state is managed."
        ),
    ),
    PromptTemplate(
        id="state_management",
        title="Explain state management flow",
        category="Frontend",
        description="Describe how state is stored, shared, and updated.",
        prompt_template=(
            "Analyze the repository and explain state management flow. Identify where local state, shared state, "
            "context, stores, or derived data live, and explain the tradeoffs or coupling that result."
        ),
    ),
    PromptTemplate(
        id="security_risks",
        title="Identify security risks",
        category="Security",
        description="Review the repository for common security issues and trust boundaries.",
        prompt_template=(
            "Analyze the repository for security risks. Review authentication, authorization, secrets handling, "
            "input validation, file handling, dependency concerns, and any exposed sensitive paths. Rank the main risks."
        ),
    ),
    PromptTemplate(
        id="code_smells",
        title="Detect code smells",
        category="Quality",
        description="Find coupling, duplication, and maintainability issues.",
        prompt_template=(
            "Analyze the repository and detect code smells. Focus on duplication, overly large modules, unclear "
            "responsibility boundaries, tight coupling, naming problems, and maintainability risks."
        ),
    ),
    PromptTemplate(
        id="error_handling",
        title="Explain error handling strategy",
        category="Quality",
        description="Describe how errors are surfaced, logged, and recovered from.",
        prompt_template=(
            "Analyze the repository and explain the error handling strategy. Cover validation errors, runtime "
            "failures, logging, user-facing fallbacks, and where the system may fail silently."
        ),
    ),
    PromptTemplate(
        id="tight_coupling",
        title="Identify tightly coupled modules",
        category="Quality",
        description="Point out modules that are hard to change independently.",
        prompt_template=(
            "Analyze the repository and identify tightly coupled modules. Explain why they are coupled, what "
            "dependencies drive that coupling, and what refactors might reduce the risk."
        ),
    ),
    PromptTemplate(
        id="deployment_flow",
        title="Explain deployment flow",
        category="DevOps",
        description="Summarize deployment-related configuration and runtime flow.",
        prompt_template=(
            "Analyze the repository and explain the deployment flow. Cover environment configuration, build steps, "
            "runtime entrypoints, deployment scripts, and infrastructure assumptions."
        ),
    ),
    PromptTemplate(
        id="cicd_setup",
        title="Explain CI/CD setup",
        category="DevOps",
        description="Describe automation pipelines and quality gates if present.",
        prompt_template=(
            "Analyze the repository and explain the CI/CD setup. Describe automation workflows, tests, build steps, "
            "release or deployment stages, and any missing safeguards."
        ),
    ),
    PromptTemplate(
        id="docker_setup",
        title="Explain Docker/container setup",
        category="DevOps",
        description="Review container-related files and summarize how they fit together.",
        prompt_template=(
            "Analyze the repository and explain the Docker or container setup. Cover Dockerfiles, compose files, "
            "runtime configuration, dependencies, and operational considerations."
        ),
    ),
    PromptTemplate(
        id="repository_purpose",
        title="Summarize repository purpose",
        category="Repository Insights",
        description="Summarize what the repository does and who it serves.",
        prompt_template=(
            "Analyze the repository and summarize its purpose, target users, main capabilities, and the most "
            "important workflows it appears to support. Reference the strongest evidence in the codebase."
        ),
    ),
    PromptTemplate(
        id="business_logic",
        title="Identify core business logic",
        category="Repository Insights",
        description="Point out where the most important domain behavior lives.",
        prompt_template=(
            "Analyze the repository and identify the core business logic. Explain which modules or files contain "
            "the most important domain behavior, how data moves through them, and what appears to be critical."
        ),
    ),
    PromptTemplate(
        id="folder_structure",
        title="Explain folder structure",
        category="Repository Insights",
        description="Summarize why the repository is organized the way it is.",
        prompt_template=(
            "Analyze the repository and explain the folder structure. Describe what each major folder is responsible "
            "for, how the layout supports the architecture, and where the main entrypoints are."
        ),
    ),
    PromptTemplate(
        id="major_dependencies",
        title="List major dependencies",
        category="Repository Insights",
        description="Summarize key libraries, frameworks, and config-driven dependencies.",
        prompt_template=(
            "Analyze the repository and list its major dependencies. Cover frameworks, libraries, config-driven "
            "platform dependencies, and where each one matters most in the codebase."
        ),
    ),
)


class PromptTemplateService:
    def __init__(self) -> None:
        self.templates = {template.id: template for template in PROMPT_TEMPLATES}

    def list_templates(self) -> List[Dict[str, Any]]:
        return [self._serialize(template) for template in PROMPT_TEMPLATES]

    def get_template(self, template_id: str) -> PromptTemplate:
        template = self.templates.get(template_id)
        if not template:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Prompt template not found.")
        return template

    def run_template(self, template_id: str) -> Dict[str, Any]:
        if not repository_store.files:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Load a repository before running a prompt template.")
        template = self.get_template(template_id)
        answer = qa_agent.answer(repository_store, template.prompt_template, None, template.scope)
        return {
            "template": self._serialize(template),
            "answer": answer,
            "found": len(repository_store.retrieve_similar(template.prompt_template)),
            "selected_file": None,
            "scope": template.scope,
        }

    def _serialize(self, template: PromptTemplate) -> Dict[str, Any]:
        return {
            "id": template.id,
            "title": template.title,
            "category": template.category,
            "description": template.description,
            "prompt_template": template.prompt_template,
            "output_format": template.output_format,
            "scope": template.scope,
        }


prompt_template_service = PromptTemplateService()
