# Face Recognition Backend - Installation Guide for Windows

## The Problem

The `face-recognition` library requires `dlib`, which needs to be compiled from source on Windows. This requires Visual Studio Build Tools (~6GB download).

## Solution Options

### Option 1: Install Visual Studio Build Tools (Recommended for Full Face Recognition)

This takes about 30-45 minutes but gives you the real ML-powered face recognition.

1. **Download Visual Studio Build Tools:**
   - Go to: https://visualstudio.microsoft.com/downloads/
   - Scroll down to "Tools for Visual Studio"
   - Download "Build Tools for Visual Studio 2022"

2. **Install C++ Build Tools:**
   - Run the installer
   - Select "Desktop development with C++"
   - Click Install (this will download ~6GB)
   - **Wait for installation to complete** (30-45 minutes)

3. **Restart your computer** (important!)

4. **Install face-recognition:**
   ```bash
   cd "C:/Users/vaisa/Desktop/Alzheimers 1/alzheimer-assist/backend"
   source venv/Scripts/activate
   pip install face-recognition
   ```

5. **Run the backend:**
   ```bash
   python app.py
   ```

---

### Option 2: Use Simplified Backend (Quick Start - For Testing Only)

If you want to test the app NOW without ML, use this simplified version that just stores/displays faces without actual recognition.

**Create `app_simple.py`:**

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import io
from PIL import Image
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Simple storage (just save face data, no actual recognition)
FACES_FILE = 'faces_database.json'

def load_faces():
    if os.path.exists(FACES_FILE):
        with open(FACES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_faces(faces):
    with open(FACES_FILE, 'w') as f:
        json.dump(faces, f)

@app.route('/api/health', methods=['GET'])
def health_check():
    faces = load_faces()
    return jsonify({
        'status': 'running',
        'message': 'Simplified backend (no ML recognition)',
        'faces_count': len(faces)
    })

@app.route('/api/faces/upload', methods=['POST'])
def upload_face():
    try:
        data = request.get_json()
        name = data.get('name')
        relationship = data.get('relationship')
        photos = data.get('photos', [])

        if not name or not relationship or not photos:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        faces = load_faces()
        face_id = f"{name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}"
        
        faces.append({
            'id': face_id,
            'name': name,
            'relationship': relationship,
            'photo_count': len(photos),
            'created_at': datetime.now().isoformat()
        })
        
        save_faces(faces)
        
        return jsonify({
            'success': True,
            'message': f'Face data saved for {name}',
            '  note': 'ML recognition disabled - using simple matching'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/faces/recognize', methods=['POST'])
def recognize_face():
    try:
        # Simple: just return random match for demo
        faces = load_faces()
        
        if not faces:
            return jsonify({
                'success': True,
                'match': False,
                'message': 'No faces in database'
            })
        
        # For demo: return first face as match
        first_face = faces[0]
        return jsonify({
            'success': True,
            'match': True,
            'name': first_face['name'],
            'relationship': first_face['relationship'],
            'distance': 0.3,  # Fake confidence
            'note': 'Simplified backend - not using ML recognition'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/faces', methods=['GET'])
def get_all_faces():
    try:
        faces = load_faces()
        return jsonify({'success': True, 'faces': faces})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/faces/<face_id>', methods=['DELETE'])
def delete_face(face_id):
    try:
        faces = load_faces()
        faces = [f for f in faces if f['id'] != face_id]
        save_faces(faces)
        return jsonify({'success': True, 'message': 'Face deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("SIMPLIFIED BACKEND - NO ML RECOGNITION")
    print("For real face recognition, install Visual Studio Build Tools")
    print("See INSTALLATION_GUIDE.md for details")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Run simplified backend:**
```bash
# Make sure you're in backend folder with venv activated
python app_simple.py
```

This will let you test the entire app flow WITHOUT needing to compile dlib. Face "recognition" will just return the first person in the database (for demo purposes).

---

## Recommendation

- **For your project submission:** Use Option 1 (install Build Tools) to get real ML face recognition
- **For quick testing NOW:** Use Option 2 (simplified backend)

Once you install Build Tools, you can switch back to the real `app.py` with full face recognition.

---

## Alternative: Install dlib Pre-compiled Wheel (Advanced)

If you find a pre-compiled dlib wheel for Python 3.12 on Windows:

```bash
# Find wheel at: https://github.com/sachadee/Dlib
# Or: https://pypi.org/project/dlib/#files
pip install dlib-19.24.0-cp312-cp312-win_amd64.whl
pip install face-recognition
```

---

## Current Status

✅ Installed: Flask, numpy, opencv-python, Pillow  
❌ Missing: face-recognition (requires dlib compilation)

Your options:
1. Install VS Build Tools (30-45 min) → Get real ML face recognition
2. Use simplified backend → Test app now, no ML

Choose based on your timeline!
