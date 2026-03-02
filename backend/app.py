from flask import Flask, request, jsonify
from flask_cors import CORS
import face_recognition
import numpy as np
import base64
import io
from PIL import Image
import json
import os
import pickle
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for React Native requests

# Storage for face encodings
ENCODINGS_FILE = 'face_encodings.pkl'
encodings_db = {}

# Load existing encodings if file exists
if os.path.exists(ENCODINGS_FILE):
    with open(ENCODINGS_FILE, 'rb') as f:
        encodings_db = pickle.load(f)
    print(f"✅ Loaded {len(encodings_db)} faces from database")

# Storage for activity logs
ACTIVITIES_FILE = 'activities.pkl'
activities_log = []

# Load existing activities if file exists
if os.path.exists(ACTIVITIES_FILE):
    with open(ACTIVITIES_FILE, 'rb') as f:
        activities_log = pickle.load(f)
    print(f"📊 Loaded {len(activities_log)} activity logs")

def save_encodings():
    """Save encodings to disk"""
    with open(ENCODINGS_FILE, 'wb') as f:
        pickle.dump(encodings_db, f)
    print(f"💾 Saved {len(encodings_db)} faces to database")

def save_activities():
    """Save activities to disk"""
    with open(ACTIVITIES_FILE, 'wb') as f:
        pickle.dump(activities_log, f)

def log_activity(activity_type, success, details):
    """Log an activity to the activities log"""
    activity = {
        'id': f"{activity_type}_{datetime.now().timestamp()}",
        'timestamp': datetime.now().isoformat(),
        'activity_type': activity_type,
        'success': success,
        'details': details
    }
    activities_log.append(activity)
    save_activities()
    print(f"📝 Logged activity: {activity_type} - {'✅ success' if success else '❌ failed'}")

def decode_base64_image(base64_string):
    """Convert base64 string to numpy array"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_string)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        image_array = np.array(image)
        
        return image_array
    except Exception as e:
        print(f"❌ Error decoding image: {str(e)}")
        return None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if server is running"""
    return jsonify({
        'status': 'healthy',
        'message': 'Face Recognition Server is running',
        'faces_count': len(encodings_db)
    })

@app.route('/api/faces/upload', methods=['POST'])
def upload_face():
    """Upload and encode face images"""
    try:
        data = request.json
        name = data.get('name')
        relationship = data.get('relationship')
        photos = data.get('photos', [])  # List of base64 images
        added_by = data.get('added_by', 'caregiver')  # 'caregiver' or 'patient'
        
        if not name or not photos:
            return jsonify({'error': 'Name and photos are required'}), 400
        
        print(f"📸 Processing {len(photos)} photos for {name}")
        
        # Store all encodings for this person
        person_encodings = []
        
        for idx, photo_base64 in enumerate(photos):
            # Decode image
            image = decode_base64_image(photo_base64)
            if image is None:
                print(f"⚠️ Failed to decode photo {idx + 1}")
                continue
            
            # Detect faces
            face_locations = face_recognition.face_locations(image)
            
            if len(face_locations) == 0:
                print(f"⚠️ No face detected in photo {idx + 1}")
                continue
            
            if len(face_locations) > 1:
                print(f"⚠️ Multiple faces detected in photo {idx + 1}, using first one")
            
            # Generate face encoding (128-dimensional vector)
            encodings = face_recognition.face_encodings(image, face_locations)
            
            if len(encodings) > 0:
                person_encodings.append(encodings[0])
                print(f"✅ Encoded photo {idx + 1} for {name}")
        
        if len(person_encodings) == 0:
            return jsonify({'error': 'No faces could be encoded from the photos'}), 400
        
        # Average all encodings for better accuracy
        avg_encoding = np.mean(person_encodings, axis=0)
        
        # Generate unique ID for this person
        person_id = len(encodings_db) + 1
        
        # Store in database with timestamps
        from datetime import datetime
        created_at = datetime.now().isoformat()
        
        encodings_db[person_id] = {
            'id': person_id,
            'name': name,
            'relationship': relationship,
            'encoding': avg_encoding.tolist(),
            'photo_count': len(person_encodings),
            'added_by': added_by,
            'created_at': created_at,
            'last_seen': None
        }
        
        # Save to disk
        save_encodings()
        
        print(f"🎉 Successfully registered {name} with {len(person_encodings)} photos")
        
        return jsonify({
            'success': True,
            'face_id': person_id,
            'encodings_stored': len(person_encodings),
            'message': f'{name} has been registered successfully'
        })
        
    except Exception as e:
        print(f"❌ Error in upload_face: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/faces/recognize', methods=['POST'])
def recognize_face():
    """Recognize a face from a photo"""
    try:
        data = request.json
        photo_base64 = data.get('photo')
        filter_by = data.get('filter', 'all')  # 'caregiver', 'patient', or 'all'
        
        if not photo_base64:
            return jsonify({'error': 'Photo is required'}), 400
        
        print(f"🔍 Starting face recognition (filter: {filter_by})...")
        
        # Decode image
        image = decode_base64_image(photo_base64)
        if image is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        # Detect faces
        face_locations = face_recognition.face_locations(image)
        
        if len(face_locations) == 0:
            print("⚠️ No face detected in image")
            return jsonify({
                'success': False,
                'message': 'No face detected in the photo. Please try again with a clearer photo.'
            })
        
        print(f"✅ Detected {len(face_locations)} face(s)")
        
        # Generate encoding for detected face
        unknown_encodings = face_recognition.face_encodings(image, face_locations)
        
        if len(unknown_encodings) == 0:
            return jsonify({
                'success': False,
                'message': 'Could not encode the face. Please try again.'
            })
        
        unknown_encoding = unknown_encodings[0]
        
        # Compare with all known faces
        if len(encodings_db) == 0:
            return jsonify({
                'success': False,
                'message': 'No faces registered yet. Please add family members first.'
            })
        
        # Filter faces based on added_by if specified
        filtered_faces = {}
        for person_id, person_data in encodings_db.items():
            added_by = person_data.get('added_by', 'caregiver')
            if filter_by == 'all' or added_by == filter_by:
                filtered_faces[person_id] = person_data
        
        if len(filtered_faces) == 0:
            return jsonify({
                'success': False,
                'message': f'No faces registered in {filter_by} database yet.'
            })
        
        print(f"🔍 Comparing with {len(filtered_faces)} known faces (filter: {filter_by})...")
        
        best_match = None
        best_distance = float('inf')
        
        for person_id, person_data in filtered_faces.items():
            known_encoding = np.array(person_data['encoding'])
            
            # Calculate Euclidean distance
            distance = np.linalg.norm(unknown_encoding - known_encoding)
            
            print(f"  - {person_data['name']}: distance = {distance:.4f}")
            
            if distance < best_distance:
                best_distance = distance
                best_match = person_data
        
        # Threshold for recognition (lower = more strict)
        RECOGNITION_THRESHOLD = 0.6
        
        if best_distance < RECOGNITION_THRESHOLD:
            confidence = max(0, min(100, (1 - best_distance) * 100))
            
            # Update last_seen timestamp
            from datetime import datetime
            best_match['last_seen'] = datetime.now().isoformat()
            encodings_db[best_match['id']]['last_seen'] = best_match['last_seen']
            save_encodings()
            
            print(f"✅ Recognized: {best_match['name']} (confidence: {confidence:.1f}%)")
            
            # Log activity
            log_activity(
                activity_type='face_recognition',
                success=True,
                details={
                    'name': best_match['name'],
                    'relationship': best_match['relationship'],
                    'confidence': round(confidence, 1)
                }
            )
            
            # Get created_at and last_seen timestamps
            created_at = best_match.get('created_at', 'Unknown')
            last_seen = best_match.get('last_seen', created_at)
            
            return jsonify({
                'success': True,
                'recognized': True,
                'name': best_match['name'],
                'relationship': best_match['relationship'],
                'confidence': round(confidence, 1),
                'distance': round(best_distance, 4),
                'face_id': best_match['id'],
                'added_by': best_match.get('added_by', 'caregiver'),
                'created_at': created_at,
                'last_seen': last_seen
            })
        else:
            print(f"❌ Unknown person (closest match: {best_match['name']} with distance {best_distance:.4f})")
            
            # Log failed recognition attempt
            log_activity(
                activity_type='face_recognition',
                success=False,
                details={
                    'message': 'Unknown person',
                    'closest_match': best_match['name'],
                    'distance': round(best_distance, 4)
                }
            )
            
            return jsonify({
                'success': True,
                'recognized': False,
                'message': 'This person is not in the database.',
                'closest_match': {
                    'name': best_match['name'],
                    'distance': round(best_distance, 4)
                }
            })
        
    except Exception as e:
        print(f"❌ Error in recognize_face: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/faces', methods=['GET'])
def get_all_faces():
    """Get all registered faces"""
    try:
        # Get filter parameter (caregiver, patient, or all)
        filter_by = request.args.get('filter', 'all')
        
        faces = []
        for person_id, person_data in encodings_db.items():
            # Apply filter if specified
            added_by = person_data.get('added_by', 'caregiver')  # Default to caregiver for backward compatibility
            if filter_by != 'all' and added_by != filter_by:
                continue
            
            faces.append({
                'id': person_data['id'],
                'name': person_data['name'],
                'relationship': person_data['relationship'],
                'photo_count': person_data['photo_count'],
                'added_by': added_by
            })
        
        return jsonify({
            'success': True,
            'faces': faces,
            'total': len(faces),
            'filter': filter_by
        })
        
    except Exception as e:
        print(f"❌ Error in get_all_faces: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/faces/<int:face_id>', methods=['DELETE'])
def delete_face(face_id):
    """Delete a registered face"""
    try:
        if face_id not in encodings_db:
            return jsonify({'error': 'Face not found'}), 404
        
        person_name = encodings_db[face_id]['name']
        del encodings_db[face_id]
        
        # Save to disk
        save_encodings()
        
        print(f"🗑️ Deleted {person_name}")
        
        return jsonify({
            'success': True,
            'message': f'{person_name} has been removed'
        })
        
    except Exception as e:
        print(f"❌ Error in delete_face: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# OBJECT DETECTION (YOLOv8)
# ============================================================================

# Initialize YOLO model
try:
    from ultralytics import YOLO
    yolo_model = YOLO('yolov8n.pt')  # Nano model for fast inference
    print("✅ YOLOv8 model loaded successfully")
except Exception as e:
    print(f"⚠️ YOLOv8 not available: {str(e)}")
    yolo_model = None

# Storage for tagged objects (caregiver-added important objects)
OBJECTS_FILE = 'tagged_objects.pkl'
OBJECTS_IMAGES_DIR = 'tagged_objects_images'
tagged_objects = {}

# Create directory for object images
if not os.path.exists(OBJECTS_IMAGES_DIR):
    os.makedirs(OBJECTS_IMAGES_DIR)

# Load existing tagged objects
if os.path.exists(OBJECTS_FILE):
    with open(OBJECTS_FILE, 'rb') as f:
        tagged_objects = pickle.load(f)
    print(f"✅ Loaded {len(tagged_objects)} tagged objects")

def save_tagged_objects():
    """Save tagged objects to disk"""
    with open(OBJECTS_FILE, 'wb') as f:
        pickle.dump(tagged_objects, f)
    print(f"💾 Saved {len(tagged_objects)} tagged objects")

def calculate_image_similarity(img1, img2):
    """Calculate similarity between two images using histogram comparison"""
    import cv2
    
    # Resize images to same size
    img1_resized = cv2.resize(img1, (256, 256))
    img2_resized = cv2.resize(img2, (256, 256))
    
    # Convert to HSV for better color comparison
    hsv1 = cv2.cvtColor(img1_resized, cv2.COLOR_RGB2HSV)
    hsv2 = cv2.cvtColor(img2_resized, cv2.COLOR_RGB2HSV)
    
    # Calculate histograms
    hist1 = cv2.calcHist([hsv1], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist2 = cv2.calcHist([hsv2], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    
    # Normalize histograms
    cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    
    # Compare histograms (returns value between 0 and 1, higher = more similar)
    similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    
    return similarity

@app.route('/api/objects/detect', methods=['POST'])
def detect_objects():
    """Match patient's photo with caregiver-tagged objects using visual similarity"""
    try:
        data = request.json
        photo_base64 = data.get('photo')
        
        if not photo_base64:
            return jsonify({'error': 'Photo is required'}), 400
        
        print("🔍 Starting object matching...")
        
        # Decode patient's image
        patient_image = decode_base64_image(photo_base64)
        if patient_image is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        if len(tagged_objects) == 0:
            print("⚠️ No objects have been tagged by caregiver yet")
            return jsonify({
                'success': True,
                'detected': False,
                'message': 'No objects have been saved yet. Ask your caregiver to add important objects first.'
            })
        
        print(f"📊 Comparing with {len(tagged_objects)} saved objects...")
        
        # Find best match using image similarity
        best_match = None
        best_similarity = 0
        
        import cv2
        
        for obj_id, obj_data in tagged_objects.items():
            # Load saved object image
            image_path = obj_data.get('image_path')
            if not image_path or not os.path.exists(image_path):
                continue
            
            saved_image = cv2.imread(image_path)
            saved_image = cv2.cvtColor(saved_image, cv2.COLOR_BGR2RGB)
            
            # Calculate similarity
            similarity = calculate_image_similarity(patient_image, saved_image)
            
            print(f"  - {obj_data['custom_name']}: similarity = {similarity:.3f}")
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = obj_data
        
        # Threshold for matching (0.5 = 50% similar)
        MATCH_THRESHOLD = 0.4
        
        if best_similarity >= MATCH_THRESHOLD:
            confidence = min(100, best_similarity * 100)
            
            print(f"✅ Matched: {best_match['custom_name']} (similarity: {confidence:.1f}%)")
            
            # Log successful object identification
            log_activity(
                activity_type='object_identification',
                success=True,
                details={
                    'object_name': best_match['custom_name'],
                    'description': best_match.get('description', ''),
                    'confidence': round(confidence, 1)
                }
            )
            
            return jsonify({
                'success': True,
                'detected': True,
                'primary_object': {
                    'custom_name': best_match['custom_name'],
                    'description': best_match.get('description', ''),
                    'confidence': round(confidence, 1)
                },
                'message': f"This is your {best_match['custom_name']}"
            })
        else:
            print(f"⚠️ No good match found (best similarity: {best_similarity:.3f})")
            
            # Log failed object identification
            log_activity(
                activity_type='object_identification',
                success=False,
                details={
                    'message': 'No match found',
                    'best_similarity': round(best_similarity, 3)
                }
            )
            
            return jsonify({
                'success': True,
                'detected': False,
                'message': 'I don\'t recognize this object. It might not be saved yet. Ask your caregiver to add it.'
            })
        
    except Exception as e:
        print(f"❌ Error in detect_objects: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/objects/tag', methods=['POST'])
def tag_object():
    """Tag an object with custom name/description (caregiver feature) - no YOLO needed"""
    try:
        data = request.json
        photo_base64 = data.get('photo')  # Base64 image of the object
        custom_name = data.get('custom_name')  # e.g., "Dad's Heart Medicine"
        description = data.get('description', '')  # e.g., "Take 2 pills after breakfast"
        
        if not photo_base64 or not custom_name:
            return jsonify({'error': 'photo and custom_name required'}), 400
        
        # Generate unique ID
        tag_id = len(tagged_objects) + 1
        
        # Decode and save image
        image = decode_base64_image(photo_base64)
        if image is None:
            return jsonify({'error': 'Failed to decode image'}), 400
        
        # Save image to disk
        image_filename = f"object_{tag_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        image_path = os.path.join(OBJECTS_IMAGES_DIR, image_filename)
        
        pil_image = Image.fromarray(image)
        pil_image.save(image_path, quality=85)
        
        # Store tagged object
        tagged_objects[tag_id] = {
            'id': tag_id,
            'custom_name': custom_name,
            'description': description,
            'image_path': image_path,
            'image_filename': image_filename,
            'created_at': datetime.now().isoformat()
        }
        
        save_tagged_objects()
        
        print(f"🏷️ Tagged new object as '{custom_name}' (ID: {tag_id})")
        
        return jsonify({
            'success': True,
            'tag_id': tag_id,
            'message': f'Saved {custom_name} successfully!'
        })
        
    except Exception as e:
        print(f"❌ Error in tag_object: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/objects/tags', methods=['GET'])
def get_tagged_objects():
    """Get all tagged objects"""
    try:
        tags = []
        for tag_id, tag_data in tagged_objects.items():
            # Read image and convert to base64 for display
            image_base64 = None
            if 'image_path' in tag_data and os.path.exists(tag_data['image_path']):
                with open(tag_data['image_path'], 'rb') as img_file:
                    image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            
            tags.append({
                'id': tag_data['id'],
                'custom_name': tag_data['custom_name'],
                'description': tag_data.get('description', ''),
                'created_at': tag_data.get('created_at', 'Unknown'),
                'image': f"data:image/jpeg;base64,{image_base64}" if image_base64 else None
            })
        
        return jsonify({
            'success': True,
            'tags': tags,
            'total': len(tags)
        })
        
    except Exception as e:
        print(f"❌ Error in get_tagged_objects: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/objects/tags/<int:tag_id>', methods=['DELETE'])
def delete_tagged_object(tag_id):
    """Delete a tagged object"""
    try:
        if tag_id not in tagged_objects:
            return jsonify({'error': 'Tag not found'}), 404
        
        custom_name = tagged_objects[tag_id]['custom_name']
        
        # Delete image file if exists
        if 'image_path' in tagged_objects[tag_id]:
            image_path = tagged_objects[tag_id]['image_path']
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"🗑️ Deleted image: {image_path}")
        
        del tagged_objects[tag_id]
        
        save_tagged_objects()
        
        print(f"🗑️ Deleted tag: {custom_name}")
        
        return jsonify({
            'success': True,
            'message': f'{custom_name} has been removed'
        })
        
    except Exception as e:
        print(f"❌ Error in delete_tagged_object: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/activities', methods=['GET'])
def get_activities():
    """Get activity logs with statistics"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        
        # Get recent activities (most recent first)
        recent_activities = sorted(
            activities_log,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limit]
        
        # Calculate statistics
        face_recognitions = [a for a in activities_log if a['activity_type'] == 'face_recognition']
        object_identifications = [a for a in activities_log if a['activity_type'] == 'object_identification']
        
        face_success = len([a for a in face_recognitions if a['success']])
        object_success = len([a for a in object_identifications if a['success']])
        
        # Get today's activities
        from datetime import datetime, timedelta
        today = datetime.now().date()
        today_activities = [
            a for a in activities_log
            if datetime.fromisoformat(a['timestamp']).date() == today
        ]
        
        # Most recognized faces
        face_counts = {}
        for activity in face_recognitions:
            if activity['success']:
                name = activity['details'].get('name', 'Unknown')
                face_counts[name] = face_counts.get(name, 0) + 1
        
        most_recognized = sorted(
            face_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Most identified objects
        object_counts = {}
        for activity in object_identifications:
            if activity['success']:
                obj_name = activity['details'].get('object_name', 'Unknown')
                object_counts[obj_name] = object_counts.get(obj_name, 0) + 1
        
        most_identified = sorted(
            object_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        stats = {
            'total_activities': len(activities_log),
            'today_activities': len(today_activities),
            'face_recognition': {
                'total': len(face_recognitions),
                'success': face_success,
                'success_rate': round((face_success / len(face_recognitions) * 100) if face_recognitions else 0, 1)
            },
            'object_identification': {
                'total': len(object_identifications),
                'success': object_success,
                'success_rate': round((object_success / len(object_identifications) * 100) if object_identifications else 0, 1)
            },
            'most_recognized_faces': [{'name': name, 'count': count} for name, count in most_recognized],
            'most_identified_objects': [{'name': name, 'count': count} for name, count in most_identified]
        }
        
        return jsonify({
            'success': True,
            'activities': recent_activities,
            'statistics': stats
        })
        
    except Exception as e:
        print(f"❌ Error in get_activities: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Alzheimer Assist Server Starting...")
    print("=" * 50)
    print(f"📊 Loaded {len(encodings_db)} registered faces")
    print(f"📦 Loaded {len(tagged_objects)} tagged objects")
    print(f"📝 Loaded {len(activities_log)} activity logs")
    
    # Use PORT environment variable for cloud deployment (Render, Railway, etc.)
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print(f"🌐 Server running on: http://{host}:{port}")
    print("✅ Ready to accept requests!")
    print("=" * 50)
    
    # Use debug=False for production
    app.run(host=host, port=port, debug=False)
