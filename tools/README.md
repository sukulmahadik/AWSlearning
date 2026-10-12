# Explainer build tools

Each "<Topic>, Explained" guide is written in a Claude Doc, exported to Markdown, and built into a
landing page plus one page per chapter.

```
python3 tools/build_explainer.py tools/topics/<topic>.py <exported-doc.md> posts
```

- `build_explainer.py` – the shared builder (Markdown conversion, chapter pages, landing page, sidebar,
  Previous/Next links, reading times, redirects for old `#section` links).
- `topics/<topic>.py` – one config per guide: slug, title, hero (with a subject-specific signature
  element), lead, chapter map, diagrams, sources and any extra CSS.
- `template.html` – supplies the shared fonts and CSS (and, for Cognito, the original hero, diagram and
  sources).

Current topics:

| Config | Pages |
| --- | --- |
| `topics/cognito.py` | `posts/cognito-explained.html`, `posts/cognito/` |
| `topics/agentcore_identity.py` | `posts/agentcore-identity-explained.html`, `posts/agentcore-identity/` |

When a doc gains a new `##` section, the build stops with "chapter map out of sync" until the section
id is added to a chapter in the topic config. After a rebuild, keep the homepage meta line in
`index.html` in step with the landing page byline.
