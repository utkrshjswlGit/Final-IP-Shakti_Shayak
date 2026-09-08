# UI Architecture

The UI is built with Next.js and Tailwind CSS. It must feel like a professional, institutional assessment workspace.

## Visual Principles
*   **No Chatbot Interface:** The primary interaction is filling out an innovation profile and reviewing generated reports. Chat is reserved strictly for a sidebar "Clarification" step.
*   **Typography & Color:** Neutral, high-contrast colors (slate, navy, white) with semantic highlighting (green for safe, amber for warning/escalation). No glowing "AI" gradients.
*   **Information Density:** High density suitable for legal/regulatory professionals, but clearly structured with distinct cards.

## Core Screens

### 1. Landing / Intake
*   Clean, authoritative hero section.
*   Large, focused text area: "Describe your Ayurveda innovation, product, or process."
*   Jurisdiction toggle (India / International) prominently displayed before submission.

### 2. The Assessment Workspace (Main Dashboard)
This is the core product view. It consists of a multi-pane layout:

*   **Header:** Innovation summary, current jurisdiction badge (e.g., "🇮🇳 INDIA").
*   **Left Column (Interaction/Clarification):**
    *   Displays questions the system needs answered to complete the assessment (e.g., "Is this a classical text formulation?").
*   **Center Column (Assessment Cards):**
    *   *Classification Card:* Preliminary product category.
    *   *IP Opportunity Map:* Grid showing Patent, Trademark, Design, GI status.
    *   *TK & ABS Assessment:* Dedicated sections highlighting Biodiversity Act or Nagoya Protocol relevance.
    *   *Action Plan:* Prioritized list of next steps.
*   **Right Column (Evidence Viewer / Drawer):**
    *   Hidden by default.
    *   When a user clicks a citation (e.g., `[Sec 3(p)]`) in the center column, this drawer slides open displaying the verbatim text of the legal source, the authority, and a link to the original URL.

### 3. Escalation Brief View
*   A printable/exportable summary view cleanly formatting the current findings and the specific reason why human expert intervention is recommended.

## Components
*   `EvidenceBadge`: Small inline component for citations.
*   `ConfidenceIndicator`: Visual bar or tag (HIGH, MODERATE, LIMITED, INSUFFICIENT).
*   `JurisdictionToggle`: Strict state-management toggle.
