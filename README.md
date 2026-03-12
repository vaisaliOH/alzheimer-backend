# 🧠 Alzheimer's Assist

An AI-powered mobile application designed to help Alzheimer's patients maintain independence and improve quality of life through facial recognition, object detection, and cognitive assistance features.

[![GitHub](https://img.shields.io/badge/GitHub-vaisaliOH-blue)](https://github.com/vaisaliOH/alzheimer-assist)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![React Native](https://img.shields.io/badge/React%20Native-Expo-blue)](https://expo.dev)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow)](https://python.org)

## 📱 Overview

Alzheimer's Assist is a comprehensive mobile solution that addresses core cognitive challenges faced by Alzheimer's patients, including:

- **Face Recognition** - Help patients identify family members, friends, and caregivers
- **Object Detection** - Identify everyday objects and their purposes using YOLOv8
- **Memory Journal** - Store and recall important memories and events
- **Cognitive Games** - Brain training exercises to maintain cognitive function
- **Medication Reminders** - Never miss important medications or appointments
- **Emergency Assistance** - Quick access to emergency contacts and ID information
- **Caregiver Dashboard** - Monitor patient activities and progress remotely

## ✨ Key Features

### For Patients
- 👤 **Face Database**: Store photos and information about important people
- 📸 **Real-time Recognition**: Instantly identify faces using the camera
- 🎯 **Object Identification**: Detect and learn about everyday objects
- 📝 **Memory Journal**: Record and revisit cherished memories
- 🎮 **Brain Games**: 5+ cognitive games (memory cards, color match, word recall, etc.)
- ⏰ **Smart Reminders**: Medication, appointments, and daily task notifications
- 🆘 **Emergency ID**: Quick access to medical info and emergency contacts

### For Caregivers
- 📊 **Activity Dashboard**: Monitor patient engagement and progress
- 📈 **Game Scores**: Track cognitive performance over time
- 👥 **Face Management**: Add and update face database entries
- 🔔 **Remote Alerts**: Get notified about important patient activities

## 🛠️ Tech Stack

### Frontend (Mobile App)
- **Framework**: React Native with Expo
- **Language**: TypeScript
- **Navigation**: Expo Router (file-based routing)
- **Database**: SQLite (local storage)
- **UI Components**: React Native Elements
- **Camera**: Expo Camera
- **Notifications**: Expo Notifications

### Backend (AI Services)
- **Framework**: Flask (Python)
- **Face Recognition**: face_recognition library (dlib)
- **Object Detection**: YOLOv8 (Ultralytics)
- **Image Processing**: OpenCV, Pillow
- **API**: RESTful endpoints

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.8+
- Expo CLI: `npm install -g expo-cli`
- Android Studio / Xcode (for emulators)
- Git

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/vaisaliOH/alzheimer-assist.git
cd alzheimer-assist
```

#### 2. Frontend Setup
```bash
# Install dependencies
npm install

# Start the Expo development server
npx expo start
```

Choose your platform:
- Press `a` for Android emulator
- Press `i` for iOS simulator
- Scan QR code with Expo Go app on your device

#### 3. Backend Setup

**Navigate to backend folder:**
```bash
cd backend
```

**Create and activate virtual environment:**

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Mac/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Start the Flask server:**
```bash
python app_simple.py
```

Backend will run on: `http://localhost:5000`

#### 4. Configure API Endpoint

Update the API URL in `alzheimer-assist/constants/apiConfig.ts`:
```typescript
export const API_BASE_URL = 'http://YOUR_LOCAL_IP:5000';
```

Find your local IP:
- Windows: `ipconfig`
- Mac/Linux: `ifconfig`

## 📁 Project Structure

```
alzheimer-assist/
├── app/                      # App screens and navigation
│   ├── (tabs)/              # Tab-based navigation
│   ├── games/               # Cognitive game screens
│   ├── patient-*.tsx        # Patient-facing screens
│   └── caregiver-*.tsx      # Caregiver screens
├── components/              # Reusable UI components
├── constants/               # Configuration and themes
├── db/                      # SQLite database setup
├── utils/                   # Utility functions
├── backend/                 # Python Flask backend
│   ├── app_simple.py       # Face recognition server
│   ├── app.py              # Advanced ML features
│   ├── yolov8n.pt          # YOLOv8 model weights
│   └── requirements.txt    # Python dependencies
└── assets/                  # Images and static files
```

## 📚 Documentation

Comprehensive guides are available in the repository:

- [Architecture Overview](ARCHITECTURE.md)
- [API Configuration Guide](API_CONFIG_GUIDE.md)
- [Face Recognition Guide](FACE_RECOGNITION_GUIDE.md)
- [YOLO Training Tutorial](YOLO_TRAINING_TUTORIAL.md)
- [Research Proposal](RESEARCH_PROPOSAL.md)
- [Technical Analysis](TECHNICAL_ANALYSIS.md)
- [Project Status](PROJECT_STATUS.md)
- [Backend Installation](backend/INSTALLATION_GUIDE.md)
- [Backend Implementation](backend/IMPLEMENTATION_GUIDE.md)

## 🎮 Cognitive Games

The app includes 5 brain training games:

1. **Memory Cards** - Classic card matching game
2. **Color Match** - Match colors to boost attention
3. **Picture Memory** - Remember and recall images
4. **Word Recall** - Remember word sequences
5. **Simple Math** - Basic arithmetic exercises

## 🔒 Privacy & Security

- **Offline-First**: All face recognition runs locally
- **No Cloud Storage**: Patient data stays on device
- **SQLite Database**: Encrypted local storage
- **No Data Collection**: No analytics or tracking
- **HIPAA Considerations**: Designed with healthcare privacy in mind

## 🌟 Use Cases

- **Early-stage Alzheimer's patients** maintaining independence
- **Family caregivers** supporting loved ones at home
- **Memory care facilities** supplementing patient care
- **Research institutions** studying cognitive assistance tools
- **Healthcare providers** as a clinical recommendation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Vaisali** - [@vaisaliOH](https://github.com/vaisaliOH)

## 🙏 Acknowledgments

- YOLOv8 by Ultralytics
- face_recognition library by Adam Geitgey
- Expo Framework
- React Native Community
- All caregivers and Alzheimer's patients who inspire this work

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**⚠️ Disclaimer**: This app is designed to assist Alzheimer's patients and caregivers but is not a replacement for professional medical care. Always consult healthcare providers for medical decisions.
