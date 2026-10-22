# Day 05 — UI Design

## 01 Learn

User Interface (UI) design is the visual and interactive layer of a product. While UX determines how a system works and flows, UI determines how it looks, responds, and communicates visually. UI design translates structural wireframes into polished screens using typography, color, spacing, imagery, and interactive controls.

UI design matters because users judge credibility and ease of use within milliseconds. Clear visual styling reduces cognitive load by showing people where to look and what to do without requiring them to read every word. When UI is messy or inconsistent, users hesitate, miss important actions, and make errors.

One practical principle to master first is **Visual Hierarchy**. Visual hierarchy is the deliberate arrangement of elements to signal their order of importance. Instead of making everything bold or colorful, create three distinct levels of attention:
- **Primary:** The single most important element on the screen (such as a page heading or a primary call-to-action button). Give it the strongest contrast, largest size, or heaviest font weight.
- **Secondary:** Supporting information that users need next (such as section subheadings, input labels, or secondary actions). Keep these visible but visually subordinate to the primary element.
- **Tertiary:** Contextual metadata or background details (such as timestamps, helper text, or disabled states). Use lighter weights, smaller sizes, or muted neutral colors.

When you control visual hierarchy through scale, contrast, and spacing, your interface becomes intuitive to scan and effortless to navigate.

---

## 02 UX English

### 1. Visual Hierarchy
**English definition:** The organization and presentation of design elements in order of visual importance.  
**UX-context example:** "We improved the visual hierarchy of the checkout screen by increasing the size and contrast of the payment button."

### 2. Affordance
**English definition:** The visual clues that indicate how an object can be used or interacted with.  
**UX-context example:** "Adding a subtle drop shadow and rounded corners gave the card an affordance that suggested it was clickable."

### 3. White Space
**English definition:** The empty space around and between elements in an interface, also known as negative space.  
**UX-context example:** "Increasing the white space between form fields helped users read the labels without feeling overwhelmed."

### 4. Component
**English definition:** A reusable, self-contained UI building block, such as a button, input field, or modal dialog.  
**UX-context example:** "We updated the primary button component to ensure all interactive states look consistent across the entire platform."

### 5. Contrast Ratio
**English definition:** The measurement of the difference in luminance or brightness between foreground text and its background.  
**UX-context example:** "The light gray text failed our contrast ratio audit, so we darkened it to meet accessibility standards."

#### Professional Collocations
- **"Establish visual weight":** To make an element draw more or less attention relative to surrounding items (e.g., *"Use a bold typeface to establish visual weight on key metrics."*).
- **"Clean up the visual noise":** To remove unnecessary borders, competing colors, or redundant labels that distract the user (e.g., *"Let's remove the heavy table borders to clean up the visual noise."*).

---

## 03 Challenge

### Scenario
A task-tracking web application has a cluttered "Task Details" card. Users overlook critical deadlines and confuse secondary actions (like "Archive") with the main action ("Mark Complete") because every element uses similar font sizes, borders, and colors.

### Goal
Design a high-fidelity visual card interface for this task that establishes an unmistakable visual hierarchy, distinct button states, and clear text styling.

### Deliverable
A single visual UI design of a desktop task card (rendered in a design tool or hand-drawn cleanly on a grid) showing:
- Task title and status badge
- Due date and priority tag
- Short description (1–2 sentences)
- Primary action ("Mark Complete") and secondary action ("Archive")

### Completion Criteria
- The primary action button has the strongest visual weight and is visibly distinct from the secondary action.
- Content typography displays at least two distinct font sizes and weights to separate titles from body copy.
- Spacing between distinct groups (e.g., header vs. action buttons) is visibly larger than spacing between related items (e.g., title vs. status).
- All text meets basic readability standards against its background.

---

## 04 Practice

**Estimated Total Time:** 45 minutes

1. **Set Up the Card Frame (5 minutes)**  
   Create a rectangular container (recommended size: 400px wide by 280px tall). Apply a clean background color (such as white or light gray) and a subtle 1px border or soft drop shadow to define the card boundary.

2. **Structure Content by Levels (15 minutes)**  
   Place the content into the frame using a standard text hierarchy:
   - Primary: Task Title (e.g., 20px, Semi-Bold, dark neutral).
   - Secondary: Status and Priority tags (e.g., 12px, Medium, enclosed in small pill containers).
   - Tertiary: Task description and due date (e.g., 14px, Regular, medium neutral).  
   *Tip: Use line height of 1.4 to 1.5 times the font size for body text to maintain legibility.*

3. **Style the Interactive Elements (15 minutes)**  
   Design two action buttons at the bottom of the card:
   - Make "Mark Complete" a filled button using your primary accent color (e.g., solid blue with white text).
   - Make "Archive" an outlined or plain text button (e.g., neutral gray text with no fill).  
   *Tip: Ensure buttons have at least 8px to 12px of vertical padding and 16px of horizontal padding so they look clickable.*

4. **Calibrate Spacing and Alignment (10 minutes)**  
   Review the spacing using an 8-point spacing rule (multiples of 8px: 8px, 16px, 24px):
   - Set 24px padding inside the card container.
   - Leave 8px between the title and its tags.
   - Leave 24px between the description body and the bottom action buttons.  
   Align all text and buttons to a consistent left edge, keeping action buttons grouped together.

---

## 05 Review

### Self-Checklist
- [ ] Does the task title catch the eye before the body description?
- [ ] Is there an obvious difference in visual weight between the primary button and the secondary button?
- [ ] Is consistent spacing applied inside the card margins and between content blocks?
- [ ] Is all text dark enough against the card background to be easily read?

### Reflection Question
Squint at your finished design until the words become unreadable. What shapes or elements stand out first, and do they match the actual priorities of the user?
