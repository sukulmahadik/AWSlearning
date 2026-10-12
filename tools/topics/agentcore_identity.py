"""Topic config for "AgentCore Identity, Explained". Build with:
    python3 tools/build_explainer.py tools/topics/agentcore_identity.py <doc.md> posts
"""
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
STYLE_TEMPLATE = os.path.join(_HERE, "..", "template.html")

SLUG = "agentcore-identity"
LANDING = "agentcore-identity-explained.html"
TITLE = "AgentCore Identity, Explained"
DESCRIPTION = ("A beginner-friendly guide to Amazon Bedrock AgentCore Identity: inbound auth, workload identities, "
               "the token vault, credential providers and OAuth flows for AI agents.")

HERO_HTML = """<header class="hero">
    <div class="eyebrow">AWS agents · a beginner's guide</div>
    <h1>AgentCore Identity, Explained</h1>
    <p class="dek">How Amazon Bedrock AgentCore Identity decides who may call your agent, gives the agent an identity of its own, and fetches the right credential for each user, written for someone meeting these ideas for the first time.</p>
    <div class="byline">Sukul Mahadik · October 11, 2026 · %%META%%</div>
    <div>
      <div class="chain" aria-label="The three tokens behind every outbound call: login token, workload access token, provider token">
        <div class="link l1"><span class="k">Step 1 · Inbound</span><span class="t">The user's login token</span><span class="v">Issued by Cognito, Okta or Entra ID, and checked before the agent runs.</span><code>iss + sub → Maya</code></div>
        <span class="arrow" aria-hidden="true">→</span>
        <div class="link l2"><span class="k">Step 2 · Agent + user</span><span class="t">Workload access token</span><span class="v">Created by AgentCore: this agent, acting for this user, right now.</span><code>travel-agent ⇄ Maya</code></div>
        <span class="arrow" aria-hidden="true">→</span>
        <div class="link l3"><span class="k">Step 3 · Outbound</span><span class="t">Provider token from the vault</span><span class="v">Released only to this agent, for this user, for these scopes.</span><code>Google · calendar.readonly</code></div>
      </div>
      <p class="chain-key">Every outbound call starts from a verified login and ends with a credential scoped to one agent and one user.</p>
    </div>
  </header>"""

LEAD_HTML = ('<p class="lead">AI agents call many services on behalf of many people, and every one of those calls needs a credential. '
             "AgentCore Identity is AWS's answer: it checks who calls the agent, gives the agent an identity of its own, and keeps "
             "each user's tokens in a vault so the agent's code never holds a secret. This guide builds up the ideas one at a time, "
             'and pairs with <a href="cognito-explained.html">Cognito, Explained</a>.</p>')

PART1_INTRO = "The core ideas, in order. Each chapter builds on the ones before it."
SOURCES_HTML = None  # built from the doc's "Sources" section

EXTRA_CSS = """
.chain { display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr) auto minmax(0, 1fr); gap: 12px; align-items: stretch; }
.chain .link { --c: var(--accent); background: var(--surface); border: 1px solid var(--rule); border-left: 4px solid var(--c); border-radius: 10px; padding: 14px 16px; display: grid; gap: 4px; align-content: start; min-width: 0; }
.chain .l1 { --c: var(--seg-header); }
.chain .l2 { --c: var(--seg-payload); }
.chain .l3 { --c: var(--seg-sig); }
.chain .k { font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.06em; text-transform: uppercase; color: var(--c); }
.chain .t { font-family: var(--display); font-weight: 700; font-size: 1.08rem; color: var(--fg); }
.chain .v { font-size: 0.95rem; color: var(--muted); line-height: 1.45; }
.chain code { justify-self: start; margin-top: 4px; font-size: 0.8rem; }
.chain .arrow { align-self: center; font-family: var(--mono); font-size: 1.3rem; color: var(--muted); }
.chain-key { margin: 10px 0 0; font-family: var(--display); font-size: 0.85rem; color: var(--muted); }
@media (max-width: 760px) {
  .chain { grid-template-columns: minmax(0, 1fr); }
  .chain .arrow { justify-self: center; transform: rotate(90deg); }
}
.sources ul { margin: 0 0 1em; padding-left: 1.2em; }
.sources li { margin-bottom: 0.25em; }
"""

_FIGURE = """<figure>
      <div class="diagram">
        <svg viewBox="0 0 760 432" role="img" aria-label="Inbound checks the caller; outbound fetches the right credential">
          <defs><marker id="ac-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" style="fill:var(--muted)"/></marker></defs>
          <text x="24" y="34" style="fill:var(--fg);font-family:var(--display);font-weight:700;font-size:16px">Inbound checks the caller; outbound fetches the right credential</text>
          <g style="fill:none;stroke:var(--muted);stroke-width:1.25">
            <path d="M130 235H170" marker-end="url(#ac-arr)"/><path d="M320 235H360" marker-end="url(#ac-arr)"/>
            <path d="M530 235H565" marker-end="url(#ac-arr)"/><path d="M245 138V207" marker-end="url(#ac-arr)"/>
            <path d="M445 263V312" marker-start="url(#ac-arr)" marker-end="url(#ac-arr)"/>
          </g>
          <g style="font-family:var(--display);font-size:13px">
            <rect x="150" y="82" width="190" height="56" rx="8" style="fill:var(--surface);stroke:var(--muted);stroke-width:1.25"/>
            <text x="245" y="106" text-anchor="middle" style="fill:var(--fg);font-weight:700">Identity provider</text>
            <text x="245" y="126" text-anchor="middle" style="fill:var(--muted);font-size:11.5px">Cognito, Okta, Entra ID</text>
            <rect x="20" y="207" width="110" height="56" rx="8" style="fill:var(--surface);stroke:var(--muted);stroke-width:1.25"/>
            <text x="75" y="239" text-anchor="middle" style="fill:var(--fg);font-weight:700">User</text>
            <rect x="170" y="207" width="150" height="56" rx="8" style="fill:var(--surface);stroke:var(--muted);stroke-width:1.25"/>
            <text x="245" y="231" text-anchor="middle" style="fill:var(--fg);font-weight:700">Your app</text>
            <text x="245" y="251" text-anchor="middle" style="fill:var(--muted);font-size:11.5px">holds a login token</text>
            <rect x="360" y="207" width="170" height="56" rx="8" style="fill:var(--accent-soft);stroke:var(--accent);stroke-width:2"/>
            <text x="445" y="231" text-anchor="middle" style="fill:var(--fg);font-weight:700">Your agent</text>
            <text x="445" y="251" text-anchor="middle" style="fill:var(--fg);font-size:11.5px">in AgentCore Runtime</text>
            <rect x="565" y="207" width="170" height="56" rx="8" style="fill:var(--surface);stroke:var(--muted);stroke-width:1.25"/>
            <text x="650" y="231" text-anchor="middle" style="fill:var(--fg);font-weight:700">Outside services</text>
            <text x="650" y="251" text-anchor="middle" style="fill:var(--muted);font-size:11.5px">Google, GitHub, Slack, APIs</text>
            <rect x="295" y="312" width="300" height="96" rx="8" style="fill:var(--surface);stroke:var(--muted);stroke-width:1.25"/>
            <text x="445" y="338" text-anchor="middle" style="fill:var(--fg);font-weight:700">AgentCore Identity</text>
            <text x="445" y="362" text-anchor="middle" style="fill:var(--muted);font-size:11.5px">workload identities and token vault</text>
            <text x="445" y="380" text-anchor="middle" style="fill:var(--muted);font-size:11.5px">credential providers and inbound authorizer</text>
          </g>
          <g style="font-family:var(--display);font-size:11.5px;fill:var(--muted)">
            <text x="255" y="176">user signs in</text>
            <text x="340" y="196" text-anchor="middle">inbound: token checked</text>
            <text x="560" y="196" text-anchor="middle">outbound: calls with token</text>
            <text x="455" y="284">asks for this user's</text>
            <text x="455" y="300">Google token, gets it</text>
          </g>
        </svg>
      </div>
      <figcaption></figcaption>
    </figure>"""

DIAGRAMS = [
    (r"embedded content: inbound and outbound auth around an agent", _FIGURE,
     r"^(The user signs in with an identity provider such as Cognito;.*)$"),
]

CHAPTERS = [
    # (slug, part, title, description, [section ids])
    ("basics", 1, "The basics", "Agents, tools, inbound and outbound auth, workload identities, tokens, OAuth flows, API keys and the token vault, then how the pieces fit together.",
     ["start-here-the-basic-ideas-in-plain-words", "the-big-picture"]),
    ("why", 1, "Why agents need their own identity system", "The problems agents create for ordinary login systems, delegation vs impersonation, and what AgentCore Identity is not.",
     ["why-agents-need-their-own-identity-system"]),
    ("inbound", 1, "Inbound authentication: who may call your agent", "IAM (SigV4) vs JWT bearer tokens, configuring the JWT authorizer, and when to use each.",
     ["inbound-authentication-who-may-call-your-agent"]),
    ("workload-identity", 1, "Workload identities and access tokens", "The agent's own identity, the agent identity directory, and the token that ties an agent to a user.",
     ["workload-identities-the-agent-s-own-identity", "workload-access-tokens-tying-the-agent-to-a-user"]),
    ("token-vault", 1, "The token vault, credential providers and API keys", "Where credentials live, how they are protected, built-in and custom providers, and API key storage.",
     ["the-token-vault-and-credential-providers", "api-keys"]),
    ("outbound", 1, "Outbound flows and session binding", "Acting for a user (3LO), acting alone (M2M), token exchange, and confirming the right user after consent.",
     ["outbound-flows-acting-for-a-user-or-acting-alone", "session-binding-and-the-callback-flow"]),
    ("sdk", 2, "Using the AgentCore SDK decorators in your agent code", "@requires_access_token and @requires_api_key: parameters, behaviour and using them as agent tools.",
     ["using-the-agentcore-sdk-decorators-in-your-agent-code"]),
    ("setup", 2, "Setting up providers and gateways", "Registering a credential provider step by step, and inbound and outbound auth on AgentCore Gateway.",
     ["setting-up-a-credential-provider-step-by-step", "agentcore-gateway-inbound-and-outbound-auth-for-tools"]),
    ("production", 2, "From laptop to production", "How local, Runtime and self-hosted agents differ, a development path, security practices and common mistakes.",
     ["local-development-vs-agentcore-runtime", "security-practices-and-common-mistakes"]),
    ("pricing-and-cognito", 2, "Pricing, limits and Cognito", "What AgentCore Identity costs, limits to know, and how it works alongside Cognito.",
     ["pricing-and-limits", "how-agentcore-identity-relates-to-cognito"]),
    ("glossary", 3, "Glossary", "One-line definitions of every term used in the guide.", ["glossary"]),
]
