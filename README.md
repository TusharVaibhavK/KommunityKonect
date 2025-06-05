# KommunityKonect

## 🏘️ Connecting Communities to Household Services

KommunityKonect is a comprehensive platform that bridges the gap between residential community members and service professionals. It streamlines the process of submitting, managing, and fulfilling household service requests—from plumbing emergencies to electrical issues and general repairs.

![KommunityKonect Dashboard](assets/dashboard_screenshot.png)

## 🌟 Core Features

### For Residents
- **Request Submission**: Easy-to-use form to submit detailed service requests with descriptions, photos, and urgency levels
- **Service Reports**: AI-powered service reports generated through NVIDIA's DeepSeek model
- **Status Tracking**: Monitor the progress of submitted requests in real-time

### For Service Professionals
- **Job Management Dashboard**: View assigned tasks, update status, and add notes
- **Schedule Management**: Track appointments and availability
- **Notification System**: Receive alerts when assigned new tasks

### For Administrators
- **Centralized Dashboard**: Comprehensive overview of all service requests
- **Assignment System**: Assign tasks to appropriate service professionals
- **Calendar Management**: Schedule and organize service appointments
- **Override Controls**: Emergency tools for manual intervention

## 📊 System Architecture

### User Roles
- **Residents**: Submit and track service requests
- **Service Professionals**: View and fulfill assigned tasks
- **Administrators**: Manage the entire service ecosystem

### Database Structure
The application uses MongoDB with the following collections:
- `users_col`: User accounts and authentication data
- `requests_col`: Service request details and status information

### Notification System
Integrated with Telegram for real-time notifications to service professionals and administrators

### Technology Stack
- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: MongoDB
- **AI Integration**: NVIDIA's DeepSeek model for service report generation
- **Authentication**: Custom hash-based authentication

## 🔄 System Flow

```mermaid
flowchart TD
    A[User] --> B[Frontend/UI Layer]
    B --> C[Authentication Service]
    B --> D[Community Management]
    B --> E[Event Management]
    B --> F[Communication Hub]
    
    C --> G[User Database]
    D --> H[Community Database]
    E --> I[Event Database]
    F --> J[Message Database]
    
    K[Admin Panel] --> L[Content Moderation]
    K --> M[User Management]
    K --> N[Analytics Dashboard]
    
    L --> H
    L --> J
    M --> G
    N --> O[Analytics Database]
    
    P[External APIs] --> Q[Email Service]
    P --> R[Push Notifications]
    P --> S[File Storage]
    
    B --> P
    C --> Q
    E --> R
    F --> S
    
    subgraph "Core Services"
        C
        D
        E
        F
    end
    
    subgraph "Database Layer"
        G
        H
        I
        J
        O
    end
    
    subgraph "Admin Features"
        K
        L
        M
        N
    end
    
    subgraph "External Services"
        P
        Q
        R
        S
    end
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style K fill:#fff3e0
```

### System Components

- **Frontend/UI Layer**: User interface for community interaction
- **Authentication Service**: User login, registration, and session management
- **Community Management**: Create, join, and manage communities
- **Event Management**: Schedule and organize community events
- **Communication Hub**: Messaging and discussion features
- **Admin Panel**: Administrative controls and monitoring
- **Database Layer**: Persistent storage for all application data
- **External Services**: Third-party integrations for enhanced functionality