# FitSync Data Flow Diagrams (DFDs)

This document contains the visual blueprints for the **FitSync** system, mapped to the sections in Chapter 3.

## 3.2 Context Flow Design (Level 0 DFD)
The high-level interaction between the system and its users.

```mermaid
graph TD
    Member((Member)) -- Login/Registration --> FS[FitSync System]
    Member -- Track Workout/Nutrition --> FS
    Member -- Make Payment --> FS
    
    Trainer((Trainer)) -- Upload Content --> FS
    Trainer -- Provide Feedback --> FS
    
    Admin((Admin)) -- Manage Users/Staff --> FS
    Admin -- Generate Reports --> FS
    
    FS -- Goal Progress/Notifications --> Member
    FS -- Member Stats/Earnings --> Trainer
    FS -- Financial/System Analytics --> Admin
```

---

## 3.6 DFD for Admin (Level 1)
Detailed data flows for administrative processes (Mapping to 3.6.1 - 3.6.16).

```mermaid
graph LR
    subgraph Admin Processes
        P1[3.6.1 Login]
        P2[3.6.3 Staff/Trainer Management]
        P3[3.6.4 Diet/Menu Management]
        P4[3.6.7 Payment Verification]
        P5[3.6.14 Help Center/Support]
    end
    
    A[Admin Entity] --> P1
    P1 --> UDB[(User Database)]
    
    A --> P2
    P2 --> TDB[(Trainer Database)]
    
    A --> P3
    P3 --> DDB[(Diet Database)]
    
    P4 --> PAY[(Payment Database)]
    P4 --> A
    
    P5 --> HDB[(Help Ticket Database)]
```

---

## 3.7 DFD for Trainer / Staff (Level 1)
Detailed data flows for Trainer activities (Mapping to 3.7.1 - 3.7.6).

```mermaid
graph LR
    subgraph Trainer Processes
        T1[3.7.1 Login]
        T2[3.7.3 View Member Attendance]
        T3[3.7.5 View Member Progress]
        T4[3.7.6 Manage Exercise Videos]
    end
    
    TRN[Trainer Entity] --> T1
    T1 --> UDB[(User Database)]
    
    TRN --> T4
    T4 --> MDB[(Media/Video Store)]
    
    UDB --> T2
    T2 --> TRN
    
    UDB --> T3
    T3 --> TRN
```

---

## 3.8 DFD for Member / User (Level 1)
Detailed data flows for Member activities (Mapping to 3.8.1 - 3.8.12).

```mermaid
graph LR
    subgraph Member Processes
        M1[3.8.1 Login/Register]
        M2[3.8.3 Browse Trainers]
        M3[3.8.5 Log Nutrition/Meals]
        M4[3.8.9 Make Payment]
        M5[3.8.11 Support/Help]
    end
    
    MEM[Member Entity] --> M1
    M1 --> UDB[(User Database)]
    
    MEM --> M3
    M3 --> NUT[(Nutrition Logs)]
    
    MEM --> M4
    M4 --> PAY[(Payment Gateway)]
    
    MEM --> M5
    M5 --> HDB[(Help DB)]
    
    TDB[(Trainer DB)] --> M2
    M2 --> MEM
```
