# Face Recognition Backend

Python Flask server for face recognition in the Alzheimer's Assist app.

## Setup Instructions

### 1. Install Python
Make sure you have Python 3.8+ installed:
```bash
python --version
```

### 2. Create Virtual Environment
```bash
cd backend
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note:** Installing `dlib` and `face-recognition` may take 5-10 minutes.

If you encounter errors installing `dlib` on Windows:
1. Install Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
2. Or install pre-built wheel: `pip install dlib-19.24.2-cp311-cp311-win_amd64.whl`

### 5. Start the Server
```bash
python app.py
```

Server will start on: **http://localhost:5000**

## API Endpoints

### Health Check
```
GET /api/health
```

### Upload Face
```
POST /api/faces/upload
Body: {
  "name": "Sarah",
  "relationship": "Daughter",
  "photos": ["base64_image1", "base64_image2", ...]
}
```

### Recognize Face
```
POST /api/faces/recognize
Body: {
  "photo": "base64_image"
}
```

### Get All Faces
```
GET /api/faces
```

### Delete Face
```
DELETE /api/faces/:id
```

## How It Works

1. **Face Detection:** Uses dlib HOG detector to find faces in images
2. **Face Encoding:** Converts each face to a 128-dimensional vector using FaceNet
3. **Face Matching:** Calculates Euclidean distance between vectors
4. **Recognition:** Matches if distance < 0.6 threshold

## Storage

Face encodings are stored in `face_encodings.pkl` (pickled Python dictionary)

## Testing

You can test the API using:
- Postman
- curl commands
- The React Native app

## Troubleshooting

**Server won't start:**
- Check if port 5000 is available
- Make sure virtual environment is activated
- Verify all dependencies are installed

**No face detected:**
- Ensure good lighting in photos
- Face should be clearly visible
- Try different angles

**Low accuracy:**
- Add more photos per person (3-5 recommended)
- Use photos with different angles/lighting
- Ensure photos are clear and in focus
