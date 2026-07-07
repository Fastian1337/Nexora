# Nexora BrainKit v1.0
This document is the DNA of Nexora Technologies. Every AI tool, compiler, generator, or developer agent MUST read, understand, and strictly follow this manual before generating any code, assets, or interface modifications.

---

## 1. Brand Identity & Personality

### Name & Tagline
- **Company:** Nexora Technologies (brand as **Nexora**)
- **Tagline:** *AI Employees for Modern Businesses* / *Build Smarter Businesses with AI*

### Personality & Emotion
- **Tone:** Intelligent, Modern, Professional, Premium, Trustworthy, Innovative, Minimal, Fast, Enterprise, Friendly.
- **Emotion:** When users open Nexora, they should immediately feel: *"This is a premium enterprise AI platform"* (not a generic chatbot template).
- **Inspirations:** Stripe, Vercel, Linear, Notion, Apple, OpenAI, Anthropic.

---

## 2. Design & Color System

The signature technology identity of Nexora is locked as follows:

| Token Name | HEX Code | HSL Mapping | Purpose / Usage |
|---|---|---|---|
| **Nexora Blue** | `#2563EB` | `221 83% 53%` | Primary branding color, main buttons |
| **Deep Indigo** | `#4338CA` | `244 60% 53%` | Secondary intelligence highlights |
| **Tech Cyan** | `#06B6D4` | `189 94% 43%` | Accent actions, active statuses |
| **Midnight Navy** | `#0B1120` | `220 50% 8%` | Dark background (Default Core UI) |
| **Cloud White** | `#F8FAFC` | `210 40% 98%` | Light background |
| **Pure Surface** | `#FFFFFF` | `0 0% 100%` | Surface layouts, modal cards |
| **Slate Border** | `#E2E8F0` | `214 32% 91%` | Subtle border bounds |

### Avoid
- ❌ Bright saturated red (except for error triggers)
- ❌ Bright warning yellow (except for alert states)
- ❌ Neon green (except for active statuses)

### Gradients
- **Primary:** Nexora Blue (`#2563EB`) → Deep Indigo (`#4338CA`)
- **Premium:** Nexora Blue (`#2563EB`) → Tech Cyan (`#06B6D4`)
- **Hero Title:** Deep Indigo (`#4338CA`) → Purple/Violet (`#7C3AED`)

---

## 3. Typography & UI Layout Controls

- **Typography:** **Inter** (Primary) or **Geist** (Secondary). Never use more than two fonts.
- **Icons:** **Lucide React** outline style. Never mix icon libraries.
- **Radius Bounds:**
  - Cards: `16px` (`rounded-2xl`)
  - Buttons & Inputs: `12px` (`rounded-xl`)
  - Dialogs: `20px` (`rounded-3xl`)
- **Shadows:** Soft, high-dispersion drop shadows only. No heavy black outlines.
- **Animations:** Standardize on Framer Motion. Keep transition times between `150ms` and `300ms` (never exceed `400ms`).
- **Layout Spacing:** Base 8px scale system (`p-2`, `p-4`, `p-6`, `p-8`). Maximum container width `1280px`. Navbar height `72px`.

---

## 4. UX & AI Personality Rules

- **Access Guard:** Maximum 3 clicks to reach any specific configuration or action.
- **Layout:** Generous whitespace, zero clutter, single clear path of action.
- **AI Tone:** Confident, polite, expert, concise, accurate.
- **Safety:** Never hallucinate facts. If context or RAG data is missing, clearly explain the uncertainty.
- **Accessibility:** WCAG AA compliance. Focus outline rings, keyboard navigability, and clear ARIA labeling on all inputs.
- **Responsive design:** Every viewport (Mobile, Tablet, Desktop) must render elements cleanly without overlap or horizontal scrolling.

---

## 5. Directory Structure Mapping

- `frontend/`: Next.js 16 + React + Tailwind v4 + Lucide React.
- `backend/`: FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL + Redis.
- `docs/`: Markdown guides.
- `docker/`: nginx configurations, database initializers.
- `scripts/`: Dev & Prod startup automations.
- `tests/`: Pytest (Unit and Integration) + Cypress (E2E).
