# 🏨 Grand Horizon Hotel Management System

## 👨‍💻 Developed By
### **Yashwanth Reddy Anugu**

🎓 Master’s Student in Computer Science at Rivier University  
💡 Interested in Software Engineering, Distributed Systems, Cloud Computing, and Full-Stack Application Development

---

# 📌 Project Overview

The **Grand Horizon Hotel Management System** is a complete web-based application developed to simplify and automate hotel operations in a structured and efficient way.

This system provides an end-to-end solution for handling important hotel activities such as room management, guest handling, reservations, billing, housekeeping, maintenance tracking, and hotel analytics.

The application is developed using Streamlit and follows a role-based architecture where different users such as administrators, managers, front desk staff, housekeeping teams, and maintenance staff can securely access the system based on their responsibilities.

The main goal of this project is to improve hotel management efficiency, reduce manual work, and provide better visibility into hotel operations through centralized management and analytics.

---

# ❗ Problem Statement

In many small and medium-sized hotels, daily operations are still managed manually or through disconnected systems. This creates several operational challenges such as:

- Difficulty tracking room availability
- Reservation conflicts and overlapping bookings
- Manual billing and payment errors
- Lack of centralized guest management
- Delays in housekeeping and maintenance coordination
- Poor visibility into hotel revenue and occupancy trends

These issues reduce operational efficiency and affect customer experience.

The Grand Horizon Hotel Management System solves these problems by providing a centralized and intelligent platform for managing all hotel operations in one place.

---

# ✨ Core Features

## 👥 User Management

The system supports secure role-based access control.

### Supported Roles
- Administrator
- Hotel Manager
- Front Desk Staff
- Housekeeping Team
- Maintenance Team

### Capabilities
- Secure login system
- Password hashing and authentication
- User registration and activity tracking
- Controlled access based on user role

---

# 🛏️ Room Management

The room management module allows hotel staff to efficiently manage hotel rooms and their availability.

### Features
- Add new rooms
- Update room details
- View room availability
- Track room status in real time
- Manage room categories and pricing
- Configure room amenities

### Room Status Types
- Available
- Occupied
- Cleaning
- Maintenance

---

# 🧾 Guest Management

This module stores and manages guest-related information.

### Features
- Register guest profiles
- Maintain guest booking history
- Track guest spending details
- View visit frequency and stay history
- Manage customer information centrally

---

# 📅 Reservation Management System

The reservation system is one of the main components of the application.

### Features
- Create reservations
- Modify bookings
- Cancel reservations
- Real-time room availability checking
- Prevent overlapping reservations
- Manage booking schedules efficiently

### Supported Payment Methods
- Cash
- Credit/Debit Card
- UPI
- Online Payments

---

# 🔑 Check-In & Check-Out Management

The system simplifies the hotel check-in and check-out process.

### Features
- Fast guest check-in
- Booking confirmation validation
- Automatic room status updates
- Integrated billing during checkout
- Smooth guest departure workflow

---

# 🧹 Housekeeping Management

The housekeeping module helps manage cleaning activities across hotel rooms.

### Features
- Assign housekeeping tasks
- Track room cleaning progress
- View completed and pending work
- Update cleaning status in real time

This improves coordination between front desk and housekeeping teams.

---

# 🔧 Maintenance Management

The maintenance module helps track hotel maintenance requests and technical issues.

### Features
- Create maintenance requests
- Assign priority levels
- Track issue status
- Monitor repair progress
- Maintain maintenance history

---

# 📊 Dashboard & Analytics

The application provides visual analytics and reporting features for hotel management.

### Dashboard Features
- Real-time hotel statistics
- Occupancy rate analysis
- Revenue tracking
- Booking trend analysis
- Guest activity insights
- Room utilization metrics

The analytics help management make better operational decisions.

---

# 🏗️ System Architecture

The application follows a modular and layered design approach.

### 🔹 Authentication Layer
Handles secure login and role-based authorization.

### 🔹 Hotel Operations Layer
Manages reservations, rooms, guests, and billing.

### 🔹 Service Management Layer
Handles housekeeping and maintenance workflows.

### 🔹 Reporting & Analytics Layer
Provides visualization and hotel performance analysis.

### 🔹 Database Layer
Stores all hotel records and operational data using SQLite.

---

# 🛠️ Technologies Used

## 💻 Programming Language
- Python

## 🌐 Frontend / UI
- Streamlit

## 🗄️ Database
- SQLite

## 📊 Data Handling & Visualization
- Pandas
- Plotly

## 🔐 Security
- Hashlib for password hashing

---

# 📂 Database Structure

The application uses SQLite and includes the following major tables:

- users
- rooms
- guests
- reservations
- housekeeping
- maintenance
- activity_log

These tables help organize and manage all hotel operations efficiently.

---

# ⚙️ Installation Guide

## Step 1 — Install Required Packages

```bash
pip install streamlit pandas plotly
```

---

## Step 2 — Run the Application

```bash
streamlit run app.py
```

---

## Step 3 — Open in Browser

```bash
http://localhost:8501
```

---

# 🔐 Default Login Credentials

## 👑 Administrator
- Username: admin
- Password: Admin

## 🛎️ Front Desk Staff
- Username: frontdesk
- Password: Front Desk

## 📋 Manager
- Username: manager
- Password: Hotel Manager

---

# 🔄 System Workflow

## Step 1
User logs into the system based on assigned role.

## Step 2
Front desk staff manages reservations and guest bookings.

## Step 3
Guests are checked in and room status is updated automatically.

## Step 4
Housekeeping teams receive room cleaning assignments.

## Step 5
Maintenance staff handle technical issues and repairs.

## Step 6
Managers monitor hotel performance using analytics dashboards.

## Step 7
System stores all activities and records in the database.

---

# 📈 Key Benefits

## ⚡ Improves Operational Efficiency
Automates major hotel management activities.

## 🧾 Reduces Manual Errors
Minimizes booking conflicts and billing issues.

## 📊 Provides Real-Time Visibility
Managers can monitor hotel performance instantly.

## 🤝 Improves Team Coordination
Supports collaboration between departments.

## 🔒 Ensures Secure Access
Role-based authentication protects system data.

---

# 🌟 Key Highlights

✅ Modern and responsive UI design  
✅ Real-time room and reservation management  
✅ Complete role-based system  
✅ Fully integrated SQLite database  
✅ Interactive dashboards and analytics  
✅ Easy to extend and customize  
✅ Suitable for academic and real-world learning purposes

---

# ⚠️ Current Limitations

- Uses SQLite, which may not support very large-scale deployments
- Simplified authentication system
- No cloud deployment integration currently
- Limited third-party integrations

---

# 🔮 Future Improvements

## ☁️ Cloud Deployment
Deploy using AWS or Azure cloud services.

## 📡 Real-Time Notifications
Add SMS and email notifications for reservations and alerts.

## 🤖 AI-Based Forecasting
Predict occupancy trends and booking demand.

## 💳 Advanced Payment Integration
Integrate secure payment gateways.

## 📱 Mobile Optimization
Develop mobile-friendly interfaces and applications.

---

# 🧪 Testing & Validation

The system includes validation for:

- Reservation conflict detection
- User authentication
- Room availability management
- Billing calculations
- Database operations
- Role-based access control

---

# 🎯 Final Conclusion

The **Grand Horizon Hotel Management System** provides a centralized and intelligent solution for handling hotel operations efficiently.

By combining room management, reservation handling, guest tracking, housekeeping coordination, maintenance monitoring, and analytics into a single platform, the system improves operational productivity and enhances overall hotel management.

This project demonstrates practical implementation of full-stack software engineering concepts, database integration, workflow management, and real-world business process automation.

--- 
