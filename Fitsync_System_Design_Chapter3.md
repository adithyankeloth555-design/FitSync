# CHAPTER-3: SYSTEM DESIGN

## 3.1 Introduction
The System Design for **FitSync** translates the gathered requirements into a logical blueprint. This chapter details the architectural flow, data movement, and role-specific processes through Context Flow Diagrams and Data Flow Diagrams (DFD). The design ensures a secure, scalable, and intuitive experience for Gym Members, Trainers, and Administrators.

## 3.2 Context Flow Design
The Context Flow (Level 0 DFD) represents the **FitSync** system as a single process interacting with external entities. It illustrates the high-level data exchange between the system and the outside world.

*   **Member (User)**: Interacts by providing registration data, logging calories, tracking workouts, and initiating payments. In return, the system provides goal progress, notifications, and personalized plans.
*   **Trainer (Staff)**: Provides instructional content, diet plans, and feedback. The system provides them with member statistics and earnings reports.
*   **Administrator**: Manages global system settings, user roles, and subscription plans. The system provides financial analytics and system-wide audit reports.

> **[Diagram 3.2: Level 0 Context Flow Diagram]** (See DIAGRAMS.md for visual representation)

## 3.3 Data Flow Diagram (DFD)
The Data Flow Diagram illustrates how information moves through the system. It breaks down the system into sub-processes to show how data is input, processed, stored in the database (PostgreSQL/SQLite), and eventually output as dashboards or reports.

## 3.4 Rules Regarding DFD Constraints
*   **Consistency**: Every process must have at least one input and one output.
*   **Direction**: Data flows in one direction between entities and processes.
*   **Storage**: Data cannot move directly between two data stores; it must pass through a process.
*   **Roles**: Entities (Admin, Trainer, Member) cannot interact with each other directly except through the system interface.

## 3.5 DFD Symbols
*   **Circle/Rounded Rectangle**: Represent Processes (e.g., "Calculate BMI").
*   **Square/Rectangle**: Represent External Entities (e.g., "Member").
*   **Open-ended Rectangle**: Represent Data Stores (e.g., "Payment Table").
*   **Arrows**: Represent Data Flow direction.

---

## 3.6 DFD for Admin
The Administrative Data Flow Diagram details the processes available to the platform owner.

*   **3.6.1 DFD for Login**: Validates admin credentials against the UserProfile database.
*   **3.6.2 DFD for Workout/Gym Management**: Process for managing gym-wide workout categories.
*   **3.6.3 DFD for Staff/Trainer Management**: Management of trainer onboarding and certifications.
*   **3.6.4 DFD for Diet/Nutrition Management**: Oversight of global meal and diet templates.
*   **3.6.5 DFD for Subscription Management**: Updates pricing and tiers for membership plans.
*   **3.6.6 DFD for Attendance Management**: Generates reports for member gym-entry logs.
*   **3.6.7 DFD for View Payment**: Financial audit of all successful transactions.
*   **3.6.8 DFD for View Users**: Interface for listing and managing all registered members.
*   **3.6.9 DFD for View Rating**: Monitoring feedback provided for sessions/trainers.
*   **3.6.10 DFD for View Support and Verify**: Verification of submitted help desk inquiries.
*   **3.6.11 DFD for Work Allocation to Staff**: Assigning specific members to designated trainers.
*   **3.6.12 DFD for System Alerts**: Logic for automated membership expiry notifications.
*   **3.6.13 DFD for View Review about Progress**: Oversight of member transformation journals.
*   **3.6.14 DFD for View Complaint and Send Reply**: Handling user grievances and support tickets.
*   **3.6.15 DFD for View Feedback about Content**: Analyzing satisfaction with diet and workout videos.
*   **3.6.16 DFD for View Payment Status and Update**: Manual override/check of transaction statuses.

> **[Diagram 3.6: Admin Level DFD]** (See DIAGRAMS.md)

---

## 3.7 DFD for Staff (Trainers)
*   **3.7.1 DFD for Login**: Secure authentication for service providers.
*   **3.7.2 DFD for View Profile**: Editing specialties, bio, and hourly rates.
*   **3.7.3 DFD for View Member Attendance**: Monitoring the daily logs of assigned trainees.
*   **3.7.4 DFD for View Salary/Earnings**: Tracking commissions earned from hired sessions.
*   **3.7.5 DFD for View Member Progress Status**: Analyzing trainee weight/muscle transformation charts.
*   **3.7.6 DFD for View Training Videos**: Managing uploaded instructional content.

> **[Diagram 3.7: Staff Level DFD]** (See DIAGRAMS.md)

---

## 3.8 DFD for User (Members)
*   **3.8.1 DFD for Login**: Personal profile authentication.
*   **3.8.2 DFD for Register**: Setting fitness goals and physical metrics.
*   **3.8.3 DFD for View Programs**: Browsing available workout and diet regimes.
*   **3.8.4 DFD for View Coaching**: Browsing and hiring available staff.
*   **3.8.5 DFD for Track Nutrition**: Daily logging of calorie and water intake.
*   **3.8.9 DFD for Make Payment**: Integrated gateway for membership/trainer fees.
*   **3.8.10 DFD for View Rating about Programs**: Accessing community feedback.
*   **3.8.11 DFD for Send Support Inquiry and View Replies**: Communicating with Admin/Support.
*   **3.8.12 DFD for Send Feedback**: Submitting satisfaction reports regarding plans.

> **[Diagram 3.8: User Level DFD]** (See DIAGRAMS.md)
