"""Topic config for "Cognito, Explained". Build with:
    python3 tools/build_explainer.py tools/topics/cognito.py <doc.md> posts
"""
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
STYLE_TEMPLATE = os.path.join(_HERE, "..", "template.html")
_tpl = open(STYLE_TEMPLATE, encoding="utf-8").read()

SLUG = "cognito"
LANDING = "cognito-explained.html"
TITLE = "Cognito, Explained"
DESCRIPTION = "A beginner-friendly guide to Amazon Cognito: User Pools, Identity Pools, client IDs, PKCE, tokens and access control, in 12 chapters."

# Hero, lead, diagram and sources come from the original single-page post (template.html).
HERO_HTML = re.sub(r"about \d+ minutes", "%%META%%",
                   re.search(r'<header class="hero">.*?</header>', _tpl, flags=re.S).group(0))
LEAD_HTML = re.search(r'<p class="lead">.*?</p>', _tpl, flags=re.S).group(0)
SOURCES_HTML = re.search(r'<footer class="sources">.*?</footer>', _tpl, flags=re.S).group(0)
PART1_INTRO = "The core ideas, in order. Each chapter builds on the ones before it."
EXTRA_CSS = ""

DIAGRAMS = [
    (r"embedded content: trust chain",
     re.search(r"<figure>.*?</figure>", _tpl, flags=re.S).group(0),
     r"^(Each arrow is a trust relationship with its own registration;.*)$"),
]

CHAPTERS = [
    # (slug, part, title, description, [section ids])
    ("basics", 1, "The basics", "Authentication vs authorization, identity providers, tokens, JWTs, OAuth and IAM, then how Cognito's pieces fit together.",
     ["start-here-the-basic-ideas-in-plain-words", "the-big-picture"]),
    ("pools", 1, "User Pools and Identity Pools", "What each pool does, how they chain together, and how one User Pool serves both people and apps.",
     ["user-pools-and-identity-pools", "one-user-pool-two-kinds-of-callers-people-and-apps"]),
    ("clients-and-pkce", 1, "Clients, secrets and PKCE", "Client IDs and secrets, the four app client types (web app, SPA, mobile, machine-to-machine), and how PKCE protects apps that can't keep a secret.",
     ["client-ids-and-client-secrets", "the-four-types-of-app-clients", "pkce-protecting-logins-for-apps-that-can-t-keep-a-secret"]),
    ("identity-providers", 1, "Google, Facebook and other identity providers", "Federation, trust chains, the two sets of client IDs, and the credentials Google and Facebook give Cognito and AgentCore.",
     ["how-a-user-pool-works-with-other-identity-providers", "how-identity-providers-trust-each-other",
      "the-confusing-part-two-sets-of-client-ids", "two-ways-to-bring-in-google-or-any-idp",
      "google-facebook-and-other-providers-the-credentials-behind-t", "predefined-and-custom-identity-providers-who-handles-the-cal"]),
    ("tokens-and-scopes", 1, "Tokens, scopes and resource servers", "What is inside ID, access and refresh tokens, how resource servers and custom scopes work, and where every claim comes from.",
     ["what-is-inside-a-token-claims-and-scopes", "resource-servers-and-custom-scopes-how-they-work", "defining-claims-and-scopes-in-depth"]),
    ("identity-pools", 1, "Identity Pools and AWS credentials", "How an Identity Pool turns a login into temporary AWS credentials, its providers, flows and guest access, and how it picks IAM roles.",
     ["identity-pools-in-depth-from-a-login-to-aws-credentials", "iam-roles-and-identity-pools"]),
    ("access-control", 1, "How Cognito controls what a signed-in user can access", "Every layer that decides what a signed-in user can do, and who enforces each one.",
     ["how-cognito-controls-what-a-signed-in-user-can-access"]),
    ("callbacks", 1, "Callback URLs and callback servers", "Why logins come back through the browser, why OAuth uses a code, and what a callback server implements.",
     ["callback-urls-and-callback-servers"]),
    ("token-safety", 2, "Logging out, storing and checking tokens", "Revoking access, where to keep tokens safely, and a worked example of validating them in your API.",
     ["logging-out-and-cancelling-tokens", "where-to-keep-tokens-in-a-browser-or-app", "checking-tokens-in-your-api-a-worked-example"]),
    ("building-login", 2, "Building the login experience", "Managed login vs your own screens, Lambda triggers, and choosing an API Gateway authorizer.",
     ["cognito-s-login-page-vs-building-your-own-screens", "lambda-triggers-customizing-each-step", "choosing-an-api-gateway-authorizer"]),
    ("users", 2, "Moving and linking users", "Migrating users from an existing system, and avoiding duplicate accounts with account linking.",
     ["moving-existing-users-into-cognito", "account-linking-avoiding-duplicate-users"]),
    ("architecture", 2, "Architecture, regions and pricing", "Multi-tenancy, Cognito vs IAM Identity Center, regional outages, and pricing tiers and limits.",
     ["apps-with-many-customer-companies-multi-tenancy", "user-pool-vs-iam-identity-center-vs-iam-users",
      "regions-outages-and-backups", "pricing-tiers-and-limits"]),
    ("agentcore", 2, "Where AgentCore Identity fits next to Cognito", "How AI agents use Cognito for inbound access and AgentCore Identity for the services they call.",
     ["where-agentcore-identity-fits-next-to-cognito"]),
    ("glossary", 3, "Glossary", "One-line definitions of every term used in the guide.", ["glossary"]),
]
