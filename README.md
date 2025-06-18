# FastAPI GraphQL Citizen Support System (FAQ's)

This project is a backend system built with FastAPI and GraphQL, designed to enhance citizen support systems, primarily focusing on managing and delivering FAQs for the public sector. It emphasizes efficient data querying, scalability, real-time updates (planned), role-based access control, customizable data insights, a feedback mechanism, and auditability.

**Project Goal:** To provide a flexible, scalable, and auditable data access layer for public sector FAQ and citizen support information, leveraging the power of GraphQL for client interactions.

**Key Technologies:**

*   **Backend Framework:** FastAPI
*   **API Layer:** GraphQL (via Strawberry-GraphQL) & RESTful APIs
*   **Programming Language:** Python
*   **Database:** PostgreSQL
*   **Authentication:** JWT-based (Access & Refresh Tokens)
*   **Cloud Integration (Optional):** Google Cloud Storage for file uploads (can also use local storage)

---

## Features

*   **GraphQL API (/graphql):**
    *   **Efficient Data Querying:** Clients can request exactly the data they need, reducing over-fetching and under-fetching.
    *   **FAQ Management:**
        *   Create, Read, Update, Delete (CRUD) for FAQ Categories.
        *   CRUD for FAQ Items, including publishing status, tags, and view counts.
        *   Query FAQs by category, search terms, and publication status.
    *   **Feedback Mechanism:**
        *   Citizens can submit feedback (comments, ratings) on FAQs or the system.
        *   Admins/Editors can review and manage feedback status.
    *   **User & Role Management (via GraphQL queries for admins):**
        *   List users and roles.
    *   **Auditability & Traceability:**
        *   Comprehensive logging of significant actions (creations, updates, deletions, status changes).
        *   Queryable audit logs for administrators.
    *   **Role-Based Access Control (RBAC):**
        *   GraphQL queries and mutations are protected based on user roles (e.g., "Super Admin", "Editor").
    *   **Real-Time Updates (Planned):**
        *   Subscription stubs are in place for future implementation of real-time notifications (e.g., when an FAQ is updated or new feedback is submitted).
*   **RESTful APIs (Existing):**
    *   User authentication (login, logout, token refresh, password reset).
    *   User account management (CRUD operations by Super Admins).
    *   Role management (listing roles).
    *   File uploads (to Google Cloud Storage or local storage).
*   **Scalability:** Designed with practices that support scaling, such as using a robust framework and database.
*   **Customizable Data Insights (Foundation):**
    *   Fields like `view_count` on FAQs and `rating` on feedback provide data for generating insights.
*   **Security:**
    *   JWT-based authentication.
    *   Intruder detection and logging (basic implementation).
    *   Account locking mechanisms for failed login attempts.
    *   HTTPS (assumed for production deployment).

---

## Project Structure