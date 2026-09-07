# Retailor Frontend Context

## Product

Retailor helps a job seeker tailor one resume to one job description. The user
must be able to review and edit AI-parsed content before it is used for
tailoring. AI output is a starting point, not an unquestionable final answer.

The frontend is a focused application workspace, not an admin dashboard and
not an AI chat application.

## Primary Flow

1. Upload a PDF or DOCX resume.
2. Wait for the backend to extract and structure the resume.
3. Review and edit the parsed resume.
4. Paste a job description.
5. Analyze the job description.
6. Review and edit the parsed requirements.
7. Start tailoring.
8. Review the tailored resume against the original.
9. Download the generated DOCX.

The user should not have to re-upload the resume when moving backward through
the flow. User edits must survive navigation between steps.

## Product Principles

- Never silently overwrite user edits.
- Keep parsed and tailored content editable.
- Make AI-generated content clearly reviewable.
- Do not imply that the system can fix missing qualifications.
- Do not invent experience, skills, credentials, or achievements.
- Show useful errors without exposing provider or server details.
- Preserve resume and job-description state during the current session.
- Do not log resume text, contact information, or job-description text.
- Treat the temporary download URL as temporary, not as a permanent resource.

## Visual Direction

The visual language should feel calm, editorial, practical, and trustworthy.
It should feel closer to a well-designed document editor than to a generic SaaS
dashboard.

### Color

- Page background: warm white or very light cool gray, approximately `#F5F7F9`
- Surface: white, approximately `#FFFFFF`
- Primary text: dark charcoal, approximately `#18222D`
- Secondary text: muted slate, approximately `#68727D`
- Borders: light blue-gray, approximately `#D9E0E7`
- Primary action: strong blue, approximately `#2563EB`
- Primary hover: darker blue, approximately `#1D4ED8`
- Warning or attention: restrained coral, approximately `#D96C4A`
- Success: muted green, approximately `#2F855A`

Use blue for actions and focus states, not as the entire visual identity.
Use restrained shadows and thin borders. Prefer lightly rounded controls over
large pill-shaped elements.

### Typography

Use a highly readable sans-serif for interface text, such as Inter, Geist, or
IBM Plex Sans. A restrained serif may be used in the resume preview for section
headings, but the editor itself should remain easy to scan.

Typography priorities:

- Clear hierarchy
- Comfortable body text
- Compact labels
- Readable long-form job-description text
- No oversized display text inside the product

## Layout

### Desktop

Use a narrow left workflow rail and a readable main workspace:

```text
┌─────────────────────────────────────────────────────────┐
│ Retailor                                  Save progress │
├───────────────┬─────────────────────────────────────────┤
│ 1 Upload      │                                         │
│ 2 Review      │           Current workflow task          │
│ 3 Job         │                                         │
│ 4 Tailor      │           Main editor / interaction      │
│ 5 Result      │                                         │
│               │                                         │
│ Privacy note  │                                         │
└───────────────┴─────────────────────────────────────────┘
```

The main workspace should have a readable maximum width. Do not make the
interface a tiny centered card or a full-width admin dashboard.

### Mobile

- Replace the left rail with a compact top progress indicator.
- Show one main task at a time.
- Keep controls reachable without horizontal scrolling.
- Use tabs for original versus tailored resume comparison.
- Keep long text areas comfortable to edit on a phone.

## Screens

### 1. Upload Resume

- Prominent but not oversized drag-and-drop area
- Browse button
- Clear PDF/DOCX support message
- Maximum-size message: 5 MB
- Upload and parsing loading state
- Error state for unsupported, empty, malformed, or oversized files
- Do not accept the upload silently without showing what happens next

### 2. Review Resume

This is a core screen, not a technical debug screen.

- Compact identity and contact section
- Editable summary
- Editable skills
- Repeatable experience entries
- Repeatable project entries
- Repeatable education entries
- Add, remove, and reorder controls where practical
- Clear section labels
- Continue action that preserves all edits

The user should feel like they are reviewing an extracted document, not filling
out an intimidating database form.

### 3. Job Description

- Large text editor for the original job description
- Character count and clear maximum-length feedback
- Analyze action
- Loading state while the backend processes the text
- Parsed title, company, location, employment type, requirements,
  nice-to-have items, and responsibilities shown afterward
- Parsed requirements remain editable

### 4. Tailoring

Show the selected resume and job context. Do not use a fake percentage when the
backend does not provide progress events. Use understandable state messages:

- Preparing resume
- Matching relevant experience
- Writing tailored content
- Generating DOCX

Disable duplicate submissions while tailoring is running.

### 5. Result Review

On desktop, use a comparison layout with original and tailored content. On
mobile, use `Tailored` and `Original` tabs.

The tailored result must remain editable before download. Highlight changed
sections subtly, but do not highlight every changed word.

### 6. Download

- Strong primary download action
- Show the generated filename
- Explain that the link is temporary
- Keep the tailored content visible after download
- Offer a `Start another application` action

## Interaction Rules

- Disable an action while its request is running.
- Place errors near the action that caused them.
- Offer retry for temporary backend/provider failures.
- Explain the daily limit when a `429` response occurs.
- Confirm destructive actions such as clearing the current resume.
- Do not clear the current workflow after a failed request.
- Do not automatically replace edited data with a later response.
- Generate the device ID once and persist it in browser storage.

## Avoid

- Purple gradients
- Generic dashboard cards everywhere
- Fake analytics or application metrics
- Decorative AI sparkle effects
- A chat interface as the primary workflow
- A huge marketing hero before the product
- Dense forms showing every workflow step at once
- Automatically accepting AI output without review
- Horizontal scrolling on mobile

## Frontend State

The application state should preserve:

- Current workflow step
- Stable device ID
- Uploaded file metadata
- Parsed resume
- User-edited resume
- Raw job-description text
- Parsed job description
- User-edited job description
- Tailored resume
- Temporary download URL
- Loading state per operation
- Error state per operation

Keep the state model explicit. Do not hide important workflow state inside
individual presentational components.

## Privacy

- Do not send API keys to the browser.
- Do not send resume or job-description content to analytics services.
- Do not log resume content, contact information, or job-description text.
- Store only the minimum local state needed for the current workflow.
- A browser-generated device ID is an abuse-prevention identifier, not user
  authentication.
