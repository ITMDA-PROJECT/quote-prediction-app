# 🏭 Quote Prediction App  

## 📘 Overview  
The **Quote Prediction App** is a microservices-based system built for a manufacturing company to **optimize quote generation** using **machine learning**.  
By analyzing historical manufacturing data, the app predicts accurate quotes and reduces manual processing time — improving both **efficiency** and **pricing accuracy**.

---

## 🧩 Architecture  
The system follows a **microservices architecture** with a connected Android frontend:  

- 🧑‍💼 **User Service** – Handles user registration, authentication, and authorization.  
- 💬 **Quote Service** – Manages quote requests, generation, and communication with the ML model.  
- 🤖 **ML Service** – Serves the trained ML model for quote prediction.  
- 📱 **Android Frontend** – Built with **Java** and **XML**, allowing users to easily create and view quotes from their devices.  

Each service communicates via **REST APIs**, ensuring scalability, modularity, and clean separation of concerns.

---

## 🛠️ Tech Stack  
**Frontend:**  
- Android (Java, XML)  

**Backend:**    
- Python (APIs & Machine Learning Model)  
- SQL (Relational Database)  

---

## 🗂️ Repository Structure  
- **`frontend/`** → Android app (UI and client logic)  
- **`backend/`** → Microservices for User, Quote, and ML functionality  

---

## ✨ Project Highlights  
- 🔍 **ML-Powered Quote Prediction:** Uses trained models to forecast manufacturing costs.  
- 🔐 **Secure Authentication:** Role-based access with user management via backend services.  
- ⚙️ **Scalable Microservices:** Independent, modular services for maintainability and deployment.  
- 📲 **User-Friendly Android App:** Simple interface for quote requests and results display.  

---

## 📈 Future Improvements  
- 📊 Integrate advanced ML algorithms for better prediction accuracy.  
- ☁️ Deploy services using Docker and AWS for cloud scalability.  
- 📬 Add real-time quote status updates and notifications.  

---

## 👩‍💻 Contributors  
**Team Project:** Developed collaboratively with a focus on clean architecture, modular design, and practical application of machine learning in manufacturing.

---

> 💡 *This project showcases the integration of backend microservices, machine learning, and Android development — demonstrating full-stack engineering across data, model, and user layers.*
