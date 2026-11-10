# Day 06 — Interactive Prototype

## 01 Learn

An interactive prototype is a simplified, testable model of a product. It connects interface screens or states so someone can perform a task and experience how the product responds. A prototype can be made with paper, slides, or a design tool; it does not need production code or final visual polish.

Prototypes make design ideas concrete. A static screen can show what an interface looks like, but an interactive prototype helps a team inspect what happens after a tap, what feedback appears, and where a person may hesitate. It is useful for communicating a flow, checking interaction logic, and finding unanswered design questions before development.

Choose fidelity to match the question. Low-fidelity screens are quick to change and work well for exploring structure. Higher-fidelity screens are useful when a question depends on visual hierarchy, realistic content, or detailed interaction feedback. Adding detail without a clear question costs time and can make a weak idea feel more finished than it is.

**Practical principle: prototype the decision, not every screen.** Start with one user goal and include the states needed to complete it. For every important action, show a visible system response. Include a way to recover from a mistake or return to a safe point. A prototype is a learning tool, not proof that the design is already correct.

## 02 UX English

### 1. Interactive Prototype
**English definition:** A simplified product model that lets people move through screens and experience key interactions.  
**UX-context example:** We used an interactive prototype to check whether a student could reserve a study room without help.

### 2. Fidelity
**English definition:** The level of detail and realism represented in a design or prototype.  
**UX-context example:** We kept the prototype at low fidelity because the team was still deciding how room availability should be organized.

### 3. Interaction State
**English definition:** A specific condition of an interface before, during, or after a user action.  
**UX-context example:** The disabled state makes it clear that the Reserve button cannot be used until a time slot is selected.

### 4. Clickable Hotspot
**English definition:** An interactive area that links one part of a prototype to another screen or state.  
**UX-context example:** I added a clickable hotspot to the room card so the prototype opens the room details screen.

### 5. Microinteraction
**English definition:** A small, focused response to an action, such as a confirmation, toggle, or brief status change.  
**UX-context example:** A short confirmation message is a useful microinteraction after a reservation is saved.

Useful expressions:
- **Match fidelity to the question:** Choose the amount of detail that helps answer the current design question.
- **Make the next state visible:** Show what changes after an action so the interaction is understandable.

## 03 Challenge

### Scenario
A university study-space app lets students find an available room and reserve a time slot. A reservation must show a clear confirmation, and students need a simple way to cancel and return to the availability list.

### Goal
Create a small interactive prototype that communicates the reservation flow and makes the system response clear at each important step.

### Deliverable
A clickable prototype with four to six screens or states, plus a short note naming the design question the prototype is intended to explore.

### Completion Criteria
- The prototype includes a starting point, room availability, a room or time-slot selection, and a reservation confirmation.
- A visible interaction connects each required step; the main path can be completed from start to confirmation.
- The selected time and reservation status remain understandable on the confirmation state.
- At least one recovery path lets a student change a selection or cancel before completion.
- The note states one specific question the prototype can help the designer answer.

## 04 Practice

Estimated time: 40 minutes

1. **Choose the question and scope (5 minutes)**  
   Write one question, such as: “Can a student tell which room and time they are reserving?” Limit the prototype to the screens needed to explore that question.

2. **Sketch the key states (10 minutes)**  
   Draw the availability list, a room or time-slot detail, and a confirmation. Add a selection or unavailable state only if it helps explain the flow. Use simple rectangles and labels; visual polish is not required.

3. **Connect the interactions (15 minutes)**  
   In a design tool, link the relevant controls to their next states. With paper, place the screens in order and move between them when a user action is named. Add feedback after selecting a slot and a clear route to change or cancel.

4. **Walk through and refine (10 minutes)**  
   Start at the first screen and perform the reservation task without skipping steps. Check that each action has a visible response, the selected time is retained, and the recovery path is easy to find. Fix one confusing transition and write down the question the prototype still cannot answer.

## 05 Review

### Self-Checklist
- [ ] Does the prototype support one clear user goal?
- [ ] Does each important action lead to a visible state change?
- [ ] Can a student understand the reservation status?
- [ ] Is there a safe way to revise or cancel the selection?
- [ ] Is the prototype detailed only where the design question requires it?

**Reflection question:** Which interaction did you make clearer after walking through the prototype, and what evidence from the walkthrough led you to change it?
