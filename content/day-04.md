# Day 04 — User Flow

## 01 Learn

A user flow is a diagram that maps the step-by-step path a user takes through an interface to complete a specific task. While a sitemap shows the organizational structure of a website and a wireframe shows layout, a user flow focuses on progression and logic over time. It connects user actions, system responses, and screen states into a coherent sequence.

Mapping user flows early prevents architectural flaws. By tracking user steps before drawing high-fidelity screens, you can spot unnecessary friction, redundant steps, and dead ends. It also creates a shared blueprint for designers, developers, and product managers to agree on functional requirements and technical constraints.

A fundamental principle of user flows is to design the happy path first. Always establish the most direct, error-free path from the entry point to task completion before adding branches. Once this baseline works, introduce decision points, edge cases, and alternate routes. Keeping diagrams oriented in a single direction—either strictly left-to-right or top-to-bottom—ensures readability.

## 02 UX English

### 1. User Flow
**English definition:** A visual diagram representing the sequence of actions a user takes to complete a specific goal within a digital product.  
**UX-context example:** Before drafting wireframes for the checkout experience, the team mapped the user flow to confirm every required step.  
- **Map a flow:** (Common collocation) To systematically plan and illustrate the sequence of user actions from start to finish.

### 2. Happy Path
**English definition:** The default, ideal user journey where everything functions as intended and no errors or blockers occur.  
**UX-context example:** We tested the happy path first to ensure a user could purchase an item in under three clicks.  
- **Happy path scenario:** (Useful phrase) The baseline use case that assumes ideal user behavior and system success.

### 3. Decision Node
**English definition:** A point in a flowchart, typically represented as a diamond shape, where the path diverges based on user choice or system conditions.  
**UX-context example:** The decision node checks whether the user is logged in before routing them to the payment screen.  
- **Branching logic:** (Useful phrase) The conditional rules that determine which direction a flow takes after a decision point.

### 4. Entry Point
**English definition:** The initial screen, touchpoint, or state where a user starts a specific task or journey.  
**UX-context example:** A push notification serves as the primary entry point for the order-tracking flow.  
- **Single entry point:** (Useful phrase) A setup where all users must start a flow from the exact same interface location.

### 5. Edge Case
**English definition:** An uncommon situation or extreme condition that occurs outside the typical user journey but still requires a design solution.  
**UX-context example:** Handling an expired credit card during an automated subscription renewal is an edge case we must account for.  
- **Handle edge cases:** (Common collocation) To design fallback states, error notices, or alternative routes for rare user scenarios.

## 03 Challenge

### Scenario
A mobile coffee-ordering app allows registered customers to reorder a previous purchase directly from the home screen. However, items can occasionally be out of stock, requiring the user to adjust their selection or cancel.

### Goal
Map a clear user flow showing how a returning customer selects a previous order, reviews the item, handles potential inventory issues, and completes checkout.

### Deliverable
A user flow diagram (hand-drawn or created in a digital whiteboard tool) showing the complete journey from app launch to order confirmation.

### Completion Criteria
- Clearly identifies the entry point (e.g., Home Screen) and terminal state (e.g., Order Confirmation).
- Contains at least one decision node representing an inventory check (in-stock vs. out-of-stock).
- Uses consistent shape conventions: rectangles for screens/states, diamonds for decision points, and labeled arrows for actions.
- Features zero dead ends; every branch either reaches the confirmation state or provides an exit route back to the home screen.

## 04 Practice

Estimated time: 40 minutes

1. **List the core steps (8 minutes)**  
   Write down the text-only sequence for the happy path: open app, tap reorder button, view order summary, tap pay, view confirmation. Keep the initial list strictly linear.

2. **Introduce branching logic (10 minutes)**  
   Identify where things can deviate. Place a decision point after the user taps reorder: "Is the item in stock?" Create a "Yes" path moving forward to payment, and a "No" path leading to an "Item Unavailable" state with options to pick a substitute or return home.

3. **Convert text into standard flow shapes (12 minutes)**  
   Use this basic flow structure to sketch or build your diagram:
   ```text
   [Entry Screen] ---> (User Action) ---> <Decision Point?>
                                              |
                                     +--------+--------+
                                     | Yes             | No
                                     v                 v
                              [Next Screen]     [Fallback State]
   ```
   *Tip:* Label connection arrows with active verbs (e.g., "Taps Reorder", "Selects Alternative") to describe what triggers each transition.

4. **Verify transitions and eliminate dead ends (10 minutes)**  
   Trace your finger through every line from start to finish. Ensure that any error state or alternate path has an arrow directing the user toward either task completion or a safe exit.

## 05 Review

### Self-Checklist
- [ ] Does the diagram flow in a single primary direction (left-to-right or top-to-bottom)?
- [ ] Are all lines leaving a decision node explicitly labeled (e.g., Yes/No, In Stock/Out of Stock)?
- [ ] Are screen states, user actions, and decision points visually distinct from one another?
- [ ] Can a user recover and complete an order if their primary item is out of stock?

### Reflection Question
Where in your flow does the system do the work instead of the user, and how does that reduce friction in the overall experience?
