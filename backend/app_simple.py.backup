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

# Simple storage (just save face data, no actual ML recognition)
FACES_FILE = 'faces_database.json'

def load_faces():
    """Load faces from JSON file"""
    if os.path.exists(FACES_FILE):
        with open(FACES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_faces(faces):
    """Save faces to JSON file"""
    with open(FACES_FILE, 'w') as f:
        json.dump(faces, f, indent=2)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    faces = load_faces()
    return jsonify({
        'status': 'running',
        'message': 'Simplified backend (no ML recognition)',
        'faces_count': len(faces),
        'note': 'Install Visual Studio Build Tools for real face recognition'
    })

@app.route('/api/faces/upload', methods=['POST'])
def upload_face():
    """Upload face data (stores metadata only, no ML processing)"""
    try:
        data = request.get_json()
        name = data.get('name')
        relationship = data.get('relationship')
        photos = data.get('photos', [])

        if not name or not relationship or not photos:
            return jsonify({
                'success': False, 
                'error': 'Missing required fields'
            }), 400

        # Generate unique ID
        face_id = f"{name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}"
        
        # Load existing faces
        faces = load_faces()
        
        # Add new face
        faces.append({
            'id': face_id,
            'name': name,
            'relationship': relationship,
            'photo_count': len(photos),
            'created_at': datetime.now().isoformat()
        })
        
        save_faces(faces)
        
        print(f"✅ Face uploaded: {name} ({relationship}) - {len(photos)} photos")
        
        return jsonify({
            'success': True,
            'message': f'Face data saved for {name}',
            'id': face_id,
            'note': 'Simplified backend - no ML encoding performed'
        })
        
    except Exception as e:
        print(f"❌ Error uploading face: {str(e)}")
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/faces/recognize', methods=['POST'])
def recognize_face():
    """
    Recognize face (simplified version - returns first match for demo)
    In real version, this would use FaceNet ML model
    """
    try:
        faces = load_faces()
        
        if not faces:
            print("❌ No faces in database")
            return jsonify({
                'success': True,
                'match': False,
                'message': 'No faces in database'
            })
        
        # DEMO MODE: Just return the first face as a match
        # In real version, this would use face_recognition.compare_faces()
        first_face = faces[0]
        
        print(f"✅ Match found (DEMO): {first_face['name']}")
        
        return jsonify({
            'success': True,
            'match': True,
            'name': first_face['name'],
            'relationship': first_face['relationship'],
            'distance': 0.35,  # Fake confidence score
            'note': 'DEMO MODE: Always returns first person in database'
        })
        
    except Exception as e:
        print(f"❌ Error recognizing face: {str(e)}")
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/faces', methods=['GET'])
def get_all_faces():
    """Get all registered faces"""
    try:
        faces = load_faces()
        print(f"📋 Returning {len(faces)} faces")
        return jsonify({
            'success': True, 
            'faces': faces
        })
        
    except Exception as e:
        print(f"❌ Error getting faces: {str(e)}")
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/faces/<face_id>', methods=['DELETE'])
def delete_face(face_id):
    """Delete a face from database"""
    try:
        faces = load_faces()
        
        # Find and remove the face
        original_count = len(faces)
        faces = [f for f in faces if f['id'] != face_id]
        
        if len(faces) < original_count:
            save_faces(faces)
            print(f"🗑️ Face deleted: {face_id}")
            return jsonify({
                'success': True, 
                'message': 'Face deleted'
            })
        else:
            return jsonify({
                'success': False, 
                'error': 'Face not found'
            }), 404
            
    except Exception as e:
        print(f"❌ Error deleting face: {str(e)}")
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 SIMPLIFIED BACKEND STARTING")
    print("=" * 70)
    print("⚠️  WARNING: This is a simplified version WITHOUT ML face recognition")
    print("📝 Face recognition will always return the first person in database")
    print("🔧 For REAL ML face recognition:")
    print("   1. Install Visual Studio Build Tools")
    print("   2. Run: pip install face-recognition")
    print("   3. Use: python app.py (instead of app_simple.py)")
    print("=" * 70)
    print("✅ Server running on: http://0.0.0.0:5000")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
