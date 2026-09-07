# Frontend Agent Brief

You are implementing the frontend for Retailor, a resume-tailoring MVP.

Before writing code, read:

- `AGENTS.md`
- `README.md`
- `docs/frontend-context.md`
- `docs/frontend-api-contract.md`
- `app/schema.py`
- `app/routes/upload.py`
- `app/routes/jd.py`
- `app/routes/tailor.py`
- `app/main.py`

First report:

1. Your understanding of the user flow.
2. The pages/components you plan to create.
3. The frontend state model.
4. Any mismatch or ambiguity between the backend and the context documents.

Do not silently guess about API behavior. Report mismatches before changing the
backend contract.

## Implementation Scope

Build the frontend in these phases:

1. Application shell and workflow state
2. API client and persistent device ID
3. Resume upload and resume editor
4. Job-description editor and analysis
5. Tailoring progress and result review
6. Download and error handling
7. Responsive polish
8. Tests and accessibility review

The required workflow is:

1. Upload resume
2. Review and edit parsed resume
3. Paste job description
4. Review and edit parsed requirements
5. Tailor resume
6. Review original versus tailored content
7. Download DOCX

## Non-Negotiable Behavior

- Generate a stable browser device ID once and send it as `x-device-id` on all
  LLM-backed requests.
- Preserve user edits while navigating backward and forward.
- Send the edited resume and edited JD to `/tailor`.
- Never silently replace edited content with a new server response.
- Disable duplicate requests while an operation is running.
- Show useful loading, empty, validation, rate-limit, retry, and provider-error
  states.
- Never expose API keys in browser code.
- Never log or send resume/JD content to analytics.
- Treat `download_url` as temporary.
- Support desktop and mobile without horizontal scrolling.

## Design Direction

Design Retailor as a focused resume and job-application workspace. Do not make
it look like an admin dashboard, analytics product, AI chat app, or generic
marketing page.

Use:

- Light gray or warm-white page background
- White editing surfaces
- Dark charcoal typography
- Strong blue primary actions
- Restrained coral warnings
- Thin borders
- Subtle shadows
- Lightly rounded controls
- Editorial document-oriented spacing

Desktop should use a narrow workflow rail with a readable main workspace.
Mobile should use a compact top progress indicator and one major task per
screen. Results should use side-by-side comparison on desktop and
`Original`/`Tailored` tabs on mobile.

Avoid:

- Purple gradients
- Fake metrics and analytics
- Excessive floating cards
- Decorative AI sparkle effects
- Huge hero sections inside the product
- Dense all-in-one forms
- Automatically accepting AI output without review

## Completion Criteria

The implementation is complete when:

- A user can complete the full flow with the real backend.
- Parsed resume fields are editable.
- Parsed JD fields are editable.
- Tailoring uses the edited values.
- Loading and failure states are understandable.
- Rate-limit responses are handled clearly.
- The temporary DOCX URL can be used to download the export.
- The interface works on desktop and mobile.
- No sensitive resume or JD content is written to logs.
- Frontend checks and tests pass.

## Impeccable Design Skill

Use the Impeccable Design skill as the visual design authority for this frontend.

Read these documents first:

- `docs/frontend-context.md`
- `docs/frontend-api-contract.md`
- `docs/frontend-agent-prompt.md`

Use the product context to understand:

- Who the user is
- What the workflow must accomplish
- Which interactions are essential
- Which privacy and responsive behaviors are non-negotiable

Use the Impeccable Design skill to improve:

- Visual hierarchy
- Typography
- Spacing and rhythm
- Color system
- Component composition
- Form and editor usability
- Loading, empty, error, and success states
- Mobile responsiveness
- Accessibility
- Visual consistency

The exact colors, fonts, border radii, shadows, and component styling in
`docs/frontend-context.md` are directional references, not immutable requirements.
You may refine or replace them if the result remains calm, editorial, practical,
trustworthy, and document-oriented.

Do not use visual design recommendations to override:

- The required product workflow
- Editable resume and job-description review
- User preservation and non-destructive editing rules
- Mobile support
- API request and response contracts
- Privacy requirements
- Rate-limit and error handling behavior

Before implementing, produce:

1. A visual direction proposal
2. A design token proposal
3. A screen-by-screen layout proposal
4. A component hierarchy
5. A list of any recommendations that conflict with the existing context

Resolve conflicts explicitly instead of silently changing product behavior.
