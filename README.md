# 💊 IoT & ML-Based Real-Time Pharmaceutical Quality Monitoring

A Flask-powered dashboard that simulates IoT sensor data for pharmaceutical supply chains and predicts product spoilage using machine learning logic. Built to demonstrate real-time monitoring, predictive analytics, and risk alerts — even without hardware.

---

## 🚀 Features
- Real-time simulation of temperature, humidity, and gas levels  
- Dynamic charts using Chart.js for live data visualization  
- Predictive risk assessment for spoilage alerts  
- Responsive and modern UI built with HTML, CSS, and JS  
- Modular Flask backend for easy ML model integration  

---

## 🏗️ Project Structure






---

## ⚙️ Installation & Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/pharma_quality_monitoring.git
   cd pharma_quality_monitoring

## Install dependencies:
   pip install flask

## Run the server:
  python app.py

## Open your browser and visit:

  http://127.0.0.1:5000/

🧠 How It Works

Flask serves the dashboard and simulates IoT sensor readings (temperature, humidity, gas).

Real-time data updates every 2 seconds on the frontend using AJAX.

“Predict Spoilage” triggers a backend calculation that estimates spoilage risk.

🧩 Future Enhancements

Integrate Firebase Firestore for cloud data storage

Connect real ESP32 hardware sensors

Implement trained LSTM and Random Forest models for real predictions

Add alert notifications via email/SMS


