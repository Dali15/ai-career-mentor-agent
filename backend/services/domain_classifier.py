"""Domain classifier
Provides `classify_domains(clean_skills, detected_intents, interests_text)` which
maps normalized skill tokens and detected intents into professional-grade domain
labels per the v1.2 upgrade rules.
"""
from __future__ import annotations

from typing import List, Set
import re


# --- Domain taxonomy (core list) -------------------------------------------
DOMAINS = [
    # Core software
    "backend_engineering",
    "frontend_engineering",
    "full_stack_engineering",
    "software_engineering_general",
    "mobile_development",

    # Cloud / infra
    "devops_engineering",
    "cloud_engineering",
    "platform_engineering",
    "site_reliability_engineering",
    "infrastructure_engineering",

    # Cybersecurity
    "cybersecurity_general",
    "cybersecurity_analyst",
    "penetration_testing",
    "ethical_hacking",
    "red_team",
    "blue_team",
    "security_engineering",
    "application_security",
    "network_security",

    # AI / Data
    "ai_engineering",
    "machine_learning_engineering",
    "data_science",
    "data_analytics",
    "data_engineering",

    # System / Architecture
    "system_architecture",
    "distributed_systems",
    "database_engineering",
    "api_design_engineering",

    # Frontend / Product
    "ui_engineering",
    "ux_engineering",
    "product_engineering",

    # General / Mixed
    "general_software_profile",
    "mixed_technical_profile",
    "unknown_profile",
]


def _has_any(tokens: Set[str], keywords: List[str]) -> bool:
    return any(k in tokens for k in keywords)


def classify_domains(clean_skills: List[str], detected_intents: List[str], interests_text: str = "") -> List[str]:
    """Classify a profile into ordered domains following the v1.2 rules.

    Returns ordered domains by priority (highest first). May return multiple domains.
    """
    skills = {s.lower() for s in clean_skills}
    intents = {i.lower() for i in detected_intents}
    interests = interests_text.lower()

    results: List[str] = []

    # --- Rule 1: Cybersecurity signals must map to security domains, never backend
    security_signals = {"security", "cybersecurity", "pentest", "pentesting", "penetration testing", "ethical hacking", "red team", "blue team", "siem", "owasp", "vulnerability"}
    if _has_any(skills, list(security_signals)) or any(re.search(rf"\b{s}\b", interests) for s in security_signals) or any(s in intents for s in ("cybersecurity", "security")):
        # choose most specific security domain when possible
        if "pentest" in skills or "penetration testing" in skills or "ethical hacking" in skills or "red team" in skills:
            results.append("penetration_testing")
        elif "siem" in skills or "security" in skills or "cybersecurity" in skills:
            results.append("cybersecurity_analyst")
        # always add security_engineering as general fallback
        if "security_engineering" not in results:
            results.append("security_engineering")

    # --- Rule 4: AI split
    if _has_any(skills, ["ai", "artificial intelligence"]) or "ai" in intents or re.search(r"\bai\b", interests or ""):
        results.append("ai_engineering")
    if _has_any(skills, ["machine learning", "ml", "models", "deep learning"]) or any(re.search(r"\b(ml|model|machine learning)\b", interests or "") for _ in [0]):
        # note: still add machine learning if skills strongly indicate ML
        if _has_any(skills, ["machine learning", "ml", "models", "deep learning"] ) or re.search(r"\b(ml|model|machine learning)\b", interests or ""):
            results.append("machine_learning_engineering")
    # data signals
    if _has_any(skills, ["data analysis", "analytics", "sql", "pandas", "tableau"]):
        # stronger data+statistics -> data_science
        if _has_any(skills, ["statistics", "probability", "math", "stochastic"]):
            results.append("data_science")
        else:
            results.append("data_analytics")

    # --- Rule 3: DevOps vs Cloud split
    cloud_kw = ["aws", "gcp", "azure"]
    devops_kw = ["docker", "kubernetes", "ci/cd", "jenkins", "ansible", "pipeline"]
    has_cloud = _has_any(skills, cloud_kw) or any(re.search(rf"\b{s}\b", interests) for s in cloud_kw)
    has_devops = _has_any(skills, devops_kw) or any(re.search(rf"\b{s}\b", interests) for s in devops_kw) or _has_any(skills, ["devops"])
    if has_cloud and has_devops:
        results.append("platform_engineering")
    elif has_cloud:
        results.append("cloud_engineering")
    elif has_devops:
        results.append("devops_engineering")

    # --- Rule 2: Full Stack
    frontend_kw = ["react", "javascript", "vue", "angular", "html", "css"]
    backend_kw = ["node", "flask", "django", "spring", "apis", "system design", "sql", "server"]
    has_frontend = _has_any(skills, frontend_kw) or bool(re.search(r"\b(frontend|ui|ux|react)\b", interests or ""))
    has_backend = _has_any(skills, backend_kw) or bool(re.search(r"\b(backend|api|server|system design)\b", interests or ""))

    # Prevent backend bias: require APIs or system design or explicit server signals to call backend
    backend_strong = _has_any(skills, ["apis", "system design", "server", "flask", "django", "spring"]) or bool(re.search(r"\b(api|system design|server)\b", interests or ""))

    if has_frontend and has_backend:
        results.append("full_stack_engineering")
    else:
        if has_frontend:
            results.append("frontend_engineering")
        if has_backend and backend_strong:
            results.append("backend_engineering")

    # Mobile
    if _has_any(skills, ["flutter", "swift", "kotlin", "android", "ios", "react native"]):
        results.append("mobile_development")

    # System / architecture
    if _has_any(skills, ["system design", "architecture", "distributed systems", "microservices"]):
        results.append("system_architecture")
    if _has_any(skills, ["database", "postgres", "mysql", "sql"]):
        results.append("database_engineering")
    if _has_any(skills, ["api", "apis", "rest api"]):
        results.append("api_design_engineering")

    # UI/UX / product
    if _has_any(skills, ["ui/ux", "ux", "ui", "design", "product"]):
        results.append("ui_engineering")
        results.append("ux_engineering")

    # Fallbacks: software general or mixed
    # If many distinct domain signals exist, mark as mixed
    if len(results) >= 3:
        results.append("mixed_technical_profile")

    # If nothing matched, mark unknown
    if not results:
        results.append("unknown_profile")

    # --- Apply priority hierarchy (Rule 6)
    priority_order = [
        "security_engineering", "penetration_testing", "cybersecurity_analyst",
        "ai_engineering", "machine_learning_engineering",
        "platform_engineering", "cloud_engineering", "devops_engineering",
        "backend_engineering", "frontend_engineering",
        "data_science", "data_analytics",
    ]

    # stable unique preserve relative order by priority then original
    ordered: List[str] = []
    for p in priority_order:
        if p in results and p not in ordered:
            ordered.append(p)
    for r in results:
        if r not in ordered:
            ordered.append(r)

    # Deduplicate final list
    final = []
    for d in ordered:
        if d not in final:
            final.append(d)

    return final
