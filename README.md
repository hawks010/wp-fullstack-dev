# WordPress Full‑Stack Development GPT Skill – by Sonny x Inkfire

An **agentic, self‑correcting Custom GPT skill** that acts as your senior WordPress developer for **plugins, child themes, block themes, React admin interfaces, REST APIs, and full accessibility & performance auditing**. It plans, codes, tests, refines, and manages every aspect of a modern WordPress project – automatically.

Created by **Sonny x Inkfire**, this toolkit embodies the highest standards of professional WordPress development and demonstrates deep expertise in AI‑assisted coding workflows.

## Goal
Transform a generic GPT into a **fully autonomous WordPress development agent** that:
- Builds standards‑compliant plugins **and** themes (classic child, block/FSE)
- Creates clean, React‑powered admin interfaces with `@wordpress/components`
- Scaffolds dynamic Gutenberg blocks with `block.json`
- Designs secure, versioned REST API endpoints
- Enforces WCAG 2.1 AA accessibility via WAVE‑style audits
- Performs browser‑level visual passes and user‑flow analysis
- Optimises performance (caching, asset loading, queries)
- Manages database versioning, multisite compatibility, and complete uninstallation
- Generates professional phpDoc and auto‑READMEs for every output

The agent operates with a strict multi‑pass self‑correction loop, never delivering placeholder code and always producing production‑ready, fully documented output.

## Features
- **Plugin & Theme Development** – Classic child themes, block themes, FSE templates.
- **Block Editor Mastery** – `block.json`, dynamic blocks, `@wordpress/scripts`, editor styles.
- **REST API Endpoints** – Secure, versioned, sanitised, documented.
- **React Admin UIs** – Accessible dashboards using WordPress components.
- **Accessibility Audit** – Simulated WAVE check (contrast, ARIA, heading order, labels).
- **Performance Optimization** – Transients, object caching, conditional enqueuing.
- **CI/CD & Testing** – GitHub Actions example, PHPUnit, Jest, PHPCS, Playwright.
- **Multisite Awareness** – Network activation, per‑site cleanup.
- **Automatic Documentation** – phpDoc blocks, hook reference, README generation.
- **Agentic Loop** – Plan → Generate → Audit (Security, i18n, Visual, UX, A11y, Performance, Docs, Blocks/REST) → Refine.

## How to Use
1. Create a new Custom GPT (ChatGPT or any compatible platform).
2. Copy the entire content of `skill-instructions.md` into the GPT’s **Instructions** field.
3. Upload `knowledge-base.md` into the GPT’s **Knowledge** section.
4. Start any conversation related to WordPress – the GPT will automatically act as your full‑stack development agent.

## Repository Contents
- `skill-instructions.md` – The agentic prompt with extended plugin/theme/block/UI/a11y loops.
- `knowledge-base.md` – Condensed standards for PHP, blocks, REST, performance, CI/CD, multisite, design patterns, and WAVE.
- `example-plugin/` – A minimal plugin demonstrating all core rules.
- `example-child-theme/` – A child theme scaffold with proper enqueuing and template overrides.
- `CHANGELOG.md` – Version history.
- `CONTRIBUTING.md` – How to contribute.

## Who is This For?
- WordPress developers who want a tireless, standards‑enforcing coding partner.
- Agencies building custom themes, plugins, and admin UIs with React.
- Accessibility advocates who need automatic WAVE‑like audits built into the workflow.
- Anyone looking to explore agentic AI in real‑world WordPress projects.

## Author
Created by **Sonny x Inkfire** – showcasing modern WordPress engineering with AI.

## License
MIT – use freely in commercial and personal projects.
