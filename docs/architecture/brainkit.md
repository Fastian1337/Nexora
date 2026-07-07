# Nexora BrainKit v1.0

This is the central design system and visual handbook for **Nexora Technologies**. It acts as the single source of truth for visual guidelines, colors, typography, UX layouts, AI personality profiles, and technical constraints.

For the active agent configuration, see [.agents/AGENTS.md](file:///c:/Users/saifu/Desktop/Nexora/.agents/AGENTS.md).

---

## Brand Colors (HSL and HEX values)

| Token Name | HEX Code | HSL Mapping | Purpose |
|---|---|---|---|
| **Nexora Blue** | `#2563EB` | `221 83% 53%` | Primary buttons, CTA components |
| **Deep Indigo** | `#4338CA` | `244 60% 53%` | Accent structures, secondary alerts |
| **Tech Cyan** | `#06B6D4` | `189 94% 43%` | Active statuses, visual waveforms |
| **Midnight Navy** | `#0B1120` | `220 50% 8%` | Dark Mode background |
| **Cloud White** | `#F8FAFC` | `210 40% 98%` | Light Mode background |
| **Slate Border** | `#E2E8F0` | `214 32% 91%` | Subtle border bounds |

---

## Border Radius Tokens

- **Cards:** `16px` (`rounded-2xl`)
- **Buttons / Inputs:** `12px` (`rounded-xl`)
- **Dialogs / Modals:** `20px` (`rounded-3xl`)

---

## AI Persona Guidelines

1. **Be professional, helpful, and concise.** Keep answers short and accurate.
2. **Handle uncertainty safely.** Do not guess values if RAG retrieval results are empty; explain what is unknown.
3. **Respect tenant partitions.** Always ensure user requests are scoped strictly within the active organization context.
