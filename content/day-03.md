# Day 03｜信息架构 Information Architecture

## 01 Learn｜今日学习

**Information Architecture (IA) 信息架构** is the structural design of shared information environments. In digital product design, IA focuses on organizing, structuring, and labeling content effectively so that users can easily find information, understand where they are, and complete their intended tasks. 

**中文理解：** 信息架构（IA）是指对数字产品中的信息和功能进行逻辑分类、层级划分与命名的体系，其核心目标是帮助用户轻松理解内容并在产品中自如穿梭。

Why does IA matter so much? Visual design attracts attention, but information architecture determines usability. When IA is weak, users encounter high **Cognitive Load 认知负荷**—they become disoriented, struggle to navigate through menus, and often abandon the product entirely. A thoughtful IA aligns closely with the user's **Mental Model 心智模型** (how they intuitively expect things to work), making complex digital systems feel effortless and natural.

**中文理解：** 优秀的视觉设计吸引目光，但信息架构决定产品是否好用；当架构符合用户的心智模型时，用户无需费力思考即可凭直觉完成操作。

### Practical Principle: Clear Hierarchy and Distinct Labeling
A reliable IA relies on two fundamental principles: **Visual & Content Hierarchy 层级结构** and **Unambiguous Labeling 明确的标签命名**. 
1. **Hierarchy (层级):** Group content from general to specific. Strive for a balanced depth—avoid burying critical actions under four levels of nested menus (overly deep hierarchy), but also avoid dumping twenty unrelated items into a single navigation bar (overly shallow/cluttered hierarchy).
2. **Labeling (命名):** Use descriptive words that represent user language rather than internal company jargon or overly abstract metaphors.

**中文理解：** 实用原则：控制分类层级（既不要藏得太深，也不要一股脑平铺），并始终用通俗易懂的用户语言进行模块命名，拒绝晦涩的技术或团队内部黑话。

---

## 02 English｜UX English

### 1. Information Architecture (IA)
**English definition:** The structural blueprint used to organize, structure, and label content and features across a website, app, or software system.  
**中文解释：** 信息架构；产品功能与内容的底层组织与层级骨架。  
**UX-context example:** "Before designing high-fidelity wireframes, we mapped out the information architecture to ensure the checkout flow was intuitive."  
**中文辅助理解：** “在绘制高保真线框图之前，我们先梳理了信息架构，以确保结账流程足够直观。”

### 2. Taxonomy
**English definition:** A hierarchical classification scheme used to organize and categorize related content items into systematic groups.  
**中文解释：** 分类法 / 分类体系；将相关内容按层级归类的结构模型。  
**UX-context example:** "The e-commerce site needs a refined taxonomy so customers can filter products by size, color, and category."  
**中文辅助理解：** “该电商网站需要更合理的分类体系，方便顾客按尺寸、颜色和类别快速筛选商品。”

### 3. Findability
**English definition:** The ease with which users can discover specific information or locate a desired feature within a system.  
**中文解释：** 可寻性；用户在系统内轻松发现特定信息或功能的容易程度。  
**UX-context example:** "Improving global search and breadcrumbs significantly boosted the findability of support documentation."  
**中文辅助理解：** “优化全局搜索和面包屑导航显著提升了帮助文档的可寻性。”

### 4. Navigation System
**English definition:** The collection of UI components (such as menus, tabs, and breadcrumbs) that allows users to move through pages and features.  
**中文解释：** 导航系统；引导用户在页面和功能间跳转的操作组件集合。  
**UX-context example:** "We replaced the hamburger menu with a bottom tab bar to create a clearer primary navigation system on mobile."  
**中文辅助理解：** “我们在移动端用底部标签栏替代了汉堡菜单，以构建更清晰的主导航系统。”

### 5. Card Sorting
**English definition:** A generative UX research technique where participants organize topics or content items into logical categories to uncover user mental models.  
**中文解释：** 卡片分类法；让受访者对内容卡片进行分组归类以探索其心智模型的用户研究方法。  
**UX-context example:** "We ran an open card sorting session to decide which features belong inside the 'Account Settings' tab."  
**中文辅助理解：** “我们组织了一次开放式卡片分类测试，用来决定哪些功能应该放入‘账户设置’标签页。”

#### Professional Expressions
* **"Flatten the hierarchy"** — To reduce the number of navigation levels so users reach destination content with fewer clicks.  
  *短语释义：扁平化层级结构（减少点击层深，让内容更容易触达）。*
* **"Mutually exclusive categories"** — Categories that do not overlap, preventing confusion about where an item belongs.  
  *短语释义：互斥分类（各分类界限分明，避免用户纠结某个内容究竟属于哪里）。*

---

## 03 Challenge｜今日挑战

**Goal:** Understand how to group features logically and define an unambiguous navigation structure for a digital product.  
**中文辅助：** 目标：掌握如何将功能内容进行逻辑归类，并为一个数字产品定义清晰的导航层级。

**Task:** Design a simple 2-level Information Architecture Site Map for a lightweight **Recipe & Meal Planner App (食谱与膳食规划应用)**. Organize a provided set of features into mutually exclusive categories with user-friendly labels.  
**中文辅助：** 任务：为一款轻量级“食谱与膳食规划 App”梳理一份包含 2 个层级的信息架构站点地图（Site Map），将常用功能分类归纳，并赋予清晰的标签。

### Observable Completion Criteria:
1. Select and organize 8–10 distinct features into 3 to 4 clear primary navigation buckets (Level 1).  
   *将 8-10 个功能特性归纳到 3 到 4 个清晰的一级导航模块中。*
2. Ensure each category label is mutually exclusive and uses clear, descriptive English.  
   *确保每个分类标签语义互斥且通俗清晰，避免让用户产生混淆。*
3. Provide a brief design rationale explaining why these categories align with user expectations.  
   *附上简短的架构理由，阐述该分类方式为何契合用户的使用习惯。*

---

## 04 Practice｜实践

**Estimated Time:** 35–50 minutes

### Step-by-Step Instructions

1. **Review the Feature Inventory (5–10 mins):**  
   Look at this unsorted list of common app features: *Saved Recipes, Grocery List, Weekly Meal Calendar, Search by Ingredient, Nutritional Intake Tracker, User Profile & Dietary Preferences, Step-by-Step Cooking Mode, Community Reviews & Tips, Notification Settings.*  
   **中文辅助：** 仔细阅读上方列出的功能清单，理解每个功能的基本用途，准备进行归类。

2. **Group Related Content into Buckets (10–15 mins):**  
   Cluster similar functions together based on user intent (e.g., discovery, planning, personal records). Aim for 3 or 4 high-level groups.  
   **中文辅助：** 根据用户的使用动机（如探索浏览、制定规划、个人管理等），将相似功能归并到 3~4 个一级大类中。

3. **Define Navigation Labels (10 mins):**  
   Give each primary group a concise, familiar name (e.g., *Discover*, *Plan*, *Cook*, *Profile*). Ensure the labels are distinct from each other.  
   **中文辅助：** 为每个一级大类命名，用词需精准自然、符合行业常规规范。

4. **Document the IA Tree and Rationale (10–15 mins):**  
   Format your hierarchy into a clean text-based site map and write a short explanation of your organizational logic in English.  
   **中文辅助：** 使用文本树状图记录下该架构，并用简短英文写出你的分类依据与设计思考。

---

### Deliverable Template

Fill out the outline below in natural English:

```markdown
### IA Exercise: Recipe & Meal Planner App

#### 1. Primary Navigation Structure (Site Map)
- [Primary Tab 1 Label]
  - [Sub-feature A]
  - [Sub-feature B]
- [Primary Tab 2 Label]
  - [Sub-feature A]
  - [Sub-feature B]
- [Primary Tab 3 Label]
  - [Sub-feature A]
  - [Sub-feature B]
- [Primary Tab 4 Label]
  - [Sub-feature A]
  - [Sub-feature B]

#### 2. Labeling & Taxonomy Rationale
- Explain why you chose these primary labels:
- Explain how this structure reduces cognitive load for everyday cooks:
```

**字段填写说明：**
* **Primary Navigation Structure:** 填写你归纳出的 3~4 个一级导航名称，并在其下方缩进列出归属的二级功能。
* **Labeling & Taxonomy Rationale:** 简述一级标签的命名理由，并解释这套结构如何帮助下厨用户降低思考负担、快速找到想要的功能。

---

## 05 Review｜学习检查

### Self-Checklist
- [ ] Are all 8–10 features accounted for without confusing duplicates?  
  *所有功能是否都合理归位，且没有产生让人困惑的重复？*
- [ ] Are the primary navigation labels concise (1–2 words) and easy to understand?  
  *一级分类标签是否精炼易懂（通常为 1-2 个词）？*
- [ ] Is the category structure mutually exclusive (no overlap between tabs)?  
  *各个板块的职责是否清晰互斥，没有模糊的交叉边界？*

### Reflection Question
*If a user wants to quickly add missing ingredients from a recipe into their grocery list while cooking, how should your Information Architecture support this cross-feature workflow without breaking navigation?*  
**中文理解与思考：** 如果用户在做饭时需要把食谱中缺失的食材快速加入“购物清单”，你的信息架构应该如何支持这种跨功能的流畅联动，而不会让用户迷失在层级跳转中？
