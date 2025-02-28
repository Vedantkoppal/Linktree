# 🌟 Linktree/Bento-like Backend with Referral System

![Django](https://img.shields.io/badge/Django-4.2-green?style=flat-square)
![DRF](https://img.shields.io/badge/DRF-3.14-red?style=flat-square)
![Celery](https://img.shields.io/badge/Celery-5.3-orange?style=flat-square)
![Redis](https://img.shields.io/badge/Redis-7.0-blue?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?style=flat-square)
![JWT](https://img.shields.io/badge/JWT-Auth-yellow?style=flat-square)
![Gunicorn](https://img.shields.io/badge/Gunicorn-20.1-green?style=flat-square)
![Pytest](https://img.shields.io/badge/Pytest-7.1-blue?style=flat-square)

## 🚀 Overview
This project is a **backend system** for a platform similar to **Linktr.ee** or **Bento.me**, built using **Django** and **Django REST Framework (DRF)**. It features a **referral system**, secure authentication, API endpoints, and **scalability enhancements** to handle high traffic.

## 🎯 Features
### ✅ **User Authentication & Registration**
- User **sign-up** via email, username, and password.
- **JWT authentication** for secure login.
- Password hashing using **Argon2 (Django default)**.
- **Forgot password** flow via email verification.

### 🔗 **Referral System**
- Each user receives a **unique referral code**, generated using a **SHA-256 hash** of their email and a secret key.
- Users can invite others using their **referral link** (e.g., `https://yourdomain.com/register?referral=USER_ID`).
- Successful referrals are **tracked in the database**.
- **Rewards System:** Users earn credits, premium features, or discounts based on the number of successful referrals.
- **Celery processes referral calculations asynchronously** to ensure scalability.
- **Prevents self-referral abuse** through validation.

### 🔐 **Security Best Practices**
- **CSRF & XSS Protection** to prevent attacks.
- **Rate Limiting** to prevent brute-force login attempts.
- **JWT tokens stored securely** in HttpOnly cookies.
- SQL Injection protection via ORM queries.

### 📈 **Performance & Scalability**
- **Redis caching** for frequently accessed data.
- **Celery task queue** for background job processing.
- **Gunicorn** as the primary WSGI server for handling requests efficiently.
- **Horizontal scaling support** for high user loads.

### 🛠 **API Endpoints**
| Method | Endpoint | Description |
|--------|-----------|-------------|
| **POST** | `/api/register/` | Register a new user with an optional referral code. |
| **POST** | `/api/login/` | Authenticate user and return JWT tokens. |
| **POST** | `/api/forgot-password/` | Handle password recovery requests. |
| **GET** | `/api/referrals/` | Get a list of users referred by the logged-in user. |
| **GET** | `/api/referral-stats/` | Get referral statistics for the logged-in user. |

---

## 📂 Database Schema
### **Users Table**
| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary Key |
| `username` | String | Unique username |
| `email` | String | Unique email address |
| `password_hash` | String | Secure password storage |
| `referral_code` | String | Unique referral code |
| `referred_by` | ForeignKey(User) | Who referred this user |
| `created_at` | DateTime | User creation timestamp |

### **Referrals Table**
| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary Key |
| `referrer_id` | ForeignKey(User) | The referring user |
| `referred_user_id` | ForeignKey(User) | The referred user |
| `date_referred` | DateTime | Timestamp of referral |
| `status` | String | `pending`, `successful` |

### **Rewards Table (Optional)**
| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary Key |
| `user_id` | ForeignKey(User) | User earning the reward |
| `reward_type` | String | Type of reward (credits, premium) |
| `amount` | Decimal | Reward amount |
| `date_earned` | DateTime | Timestamp of reward |

---

## 🔥 **How Components Work Together**
### **Celery** - Used for background task processing, including tracking referrals and updating rewards asynchronously.
### **Gunicorn** - A WSGI server that runs the Django application efficiently.
### **Redis** - Stores frequently accessed data like user sessions, referral stats, and cached queries.
  - **Fetches data** quickly instead of querying the database repeatedly.
  - **Caches referral stats** to improve API performance.

---

## 🚦 Setup & Installation
### 🔹 **1. Clone the Repository**
```sh
git clone https://github.com/yourusername/linktree-backend.git
cd linktree-backend
```

### 🔹 **2. Create & Activate a Virtual Environment**
```sh
python -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate  # For Windows
```

### 🔹 **3. Install Dependencies**
```sh
pip install -r requirements.txt
```

### 🔹 **4. Start Celery Worker**
```sh
celery -A linktree_backend worker --loglevel=info
```

---

## 🛠 Testing
- **Unit tests** validate each function independently.
- **Integration tests** check how API endpoints work together.
- **End-to-End tests** simulate real user actions.
```sh
pytest
```
### **Test Coverage**
- **User Registration Tests** ✅
- **Login Tests** ✅
- **Referral System Tests** ✅
- **Edge Cases (Invalid Referral, Duplicate Email, Self-Referral)** ✅

---

## 📌 Future Improvements
- [ ] Implement **reward system** for referrals.
- [ ] Add **OAuth 2.0 authentication** (Google, Facebook, etc.).
- [ ] Improve **caching strategy** for user data.
- [ ] Enhance **rate limiting** for better security.

---

## 📄 License
This project is licensed under the **MIT License**.

---

### 🌟 **Star this repo if you found it useful!** ⭐

