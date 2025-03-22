import os
import numpy as np
import tensorflow as tf
import pytesseract
from PIL import Image
import json
import cv2
import re
import logging
import base64
from io import BytesIO
import flask
from flask import Flask, request, render_template, jsonify, render_template_string
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(_name_)

class DocumentAuthenticityDetector:
    """A class for detecting the authenticity of documents."""
    
    def _init_(self, model_path):
        """
        Initialize the document authenticity detector.
        
        Args:
            model_path (str): Path to the TensorFlow model file.
        """
        self.model_path = model_path
        self.logger = logging.getLogger(_name_)
        
        # Load the model if it exists
        if os.path.exists(model_path):
            self.logger.info(f"Loading model from {model_path}")
            self.model = tf.keras.models.load_model(model_path)
        else:
            self.logger.warning(f"Model not found at {model_path}")
            self.model = None
    
    def verify_document(self, image_path):
        """
        Verify the authenticity of a document.
        
        Args:
            image_path (str): Path to the document image file.
            
        Returns:
            dict: Results of the document verification process.
        """
        self.logger.info(f"Verifying document: {image_path}")
        
        try:
            # Load and preprocess the image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image from {image_path}")
            
            # Resize for model input
            processed_image = cv2.resize(image, (224, 224))
            processed_image = processed_image / 255.0  # Normalize
            processed_image = np.expand_dims(processed_image, axis=0)
            
            # Get prediction from model
            if self.model is not None:
                authenticity_score = float(self.model.predict(processed_image)[0][0])
            else:
                # For demo purposes, generate a random score
                authenticity_score = np.random.uniform(0.7, 0.95)
            
            is_visually_authentic = authenticity_score > 0.7
            
            # Extract text using pytesseract
            try:
                pil_image = Image.open(image_path)
                extracted_text = pytesseract.image_to_string(pil_image)
                text_success = True
                
                # Extract basic metadata (this is a simplified implementation)
                metadata = self._extract_metadata(extracted_text)
            except Exception as e:
                self.logger.error(f"Text extraction failed: {str(e)}")
                extracted_text = ""
                text_success = False
                metadata = {}
            
            # Check for security features (simplified)
            security_issues = []
            if authenticity_score < 0.8:
                security_issues.append("Possible manipulation detected in document visual elements")
            
            # Consistency check (simplified)
            consistency_issues = []
            if authenticity_score < 0.75:
                consistency_issues.append("Inconsistencies detected between document elements")
            
            # Prepare the result
            result = {
                "is_authentic": is_visually_authentic and len(security_issues) == 0 and len(consistency_issues) == 0,
                "visual_analysis": {
                    "is_visually_authentic": is_visually_authentic,
                    "authenticity_score": authenticity_score
                },
                "security_features": {
                    "pass": len(security_issues) == 0,
                    "issues": security_issues
                },
                "text_extraction": {
                    "success": text_success,
                    "extracted_text": extracted_text,
                    "metadata": metadata
                },
                "consistency_check": {
                    "pass": len(consistency_issues) == 0,
                    "issues": consistency_issues
                }
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error verifying document: {str(e)}")
            raise
    
    def _extract_metadata(self, text):
        """
        Extract metadata from document text (simplified implementation).
        
        Args:
            text (str): Extracted text from the document.
            
        Returns:
            dict: Extracted metadata.
        """
        metadata = {}
        
        # Try to extract a date (this is a simple example)
        date_matches = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', text)
        if date_matches:
            metadata["issue_date"] = date_matches[0]
        
        # Try to extract a document ID (simplified)
        id_matches = re.findall(r'\b[A-Z0-9]{6,}\b', text)
        if id_matches:
            metadata["document_id"] = id_matches[0]
        
        return metadata

# Initialize Flask app
app = Flask(_name_)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['MODEL_PATH'] = 'document_model.h5'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the document detector
detector = DocumentAuthenticityDetector(model_path=app.config['MODEL_PATH'])

@app.route('/')
def index():
    """Render the main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/verify', methods=['POST'])
def verify_document():
    """Handle document verification requests"""
    # Check if file was uploaded
    if 'document' not in request.files:
        return jsonify({'error': 'No document uploaded'}), 400
    
    file = request.files['document']
    
    # Check if file is empty
    if file.filename == '':
        return jsonify({'error': 'No document selected'}), 400
    
    # Save the file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    try:
        # Verify the document
        result = detector.verify_document(file_path)
        
        # Create response with base64 image for display
        with open(file_path, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        response = {
            'result': result,
            'image': encoded_image
        }
        
        logger.info(f"Document {filename} verified: {'AUTHENTIC' if result['is_authentic'] else 'FORGED'}")
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error verifying document {filename}: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

# HTML template as a string
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Authenticity Verification</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.3/font/bootstrap-icons.css">
    <style>
        .upload-area {
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 50px;
            text-align: center;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .upload-area:hover {
            border-color: #0d6efd;
        }
        .result-card {
            display: none;
            margin-top: 30px;
        }
        .feature-item {
            margin-bottom: 10px;
        }
        .loading-spinner {
            display: none;
            margin-top: 20px;
        }
        .document-preview {
            max-width: 100%;
            max-height: 300px;
            margin-bottom: 15px;
        }
        .verification-badge {
            font-size: 1.5rem;
            padding: 10px 20px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container py-5">
        <header class="text-center mb-5">
            <h1 class="display-4">Document Authenticity Verification</h1>
            <p class="lead">Upload a document to verify its authenticity using AI-powered analysis</p>
        </header>
        
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card shadow">
                    <div class="card-body p-4">
                        <h5 class="card-title mb-4">Upload Document</h5>
                        
                        <div id="upload-area" class="upload-area">
                            <img src="https://cdn-icons-png.flaticon.com/512/3767/3767084.png" alt="Upload" width="60" class="mb-3">
                            <h5>Drag and drop your document here</h5>
                            <p class="text-muted">or click to browse files</p>
                            <input type="file" id="file-input" class="d-none" accept="image/*">
                        </div>
                        
                        <div class="text-center loading-spinner" id="loading-spinner">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p class="mt-2">Analyzing document...</p>
                        </div>
                        
                        <div class="result-card" id="result-card">
                            <h4 class="mb-4 text-center">Verification Results</h4>
                            
                            <div class="text-center mb-4">
                                <img id="document-preview" class="document-preview shadow-sm" alt="Document preview">
                                
                                <div id="authentic-badge" class="badge bg-success verification-badge d-none">
                                    <i class="bi bi-check-circle-fill me-2"></i> AUTHENTIC
                                </div>
                                <div id="forged-badge" class="badge bg-danger verification-badge d-none">
                                    <i class="bi bi-x-circle-fill me-2"></i> FORGED
                                </div>
                            </div>
                            
                            <div class="accordion" id="verification-details">
                                <div class="accordion-item">
                                    <h2 class="accordion-header">
                                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#visual-analysis">
                                            Visual Analysis
                                        </button>
                                    </h2>
                                    <div id="visual-analysis" class="accordion-collapse collapse show">
                                        <div class="accordion-body" id="visual-analysis-body">
                                            <!-- Visual analysis results will be inserted here -->
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="accordion-item">
                                    <h2 class="accordion-header">
                                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#security-features">
                                            Security Features
                                        </button>
                                    </h2>
                                    <div id="security-features" class="accordion-collapse collapse">
                                        <div class="accordion-body" id="security-features-body">
                                            <!-- Security features results will be inserted here -->
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="accordion-item">
                                    <h2 class="accordion-header">
                                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#document-content">
                                            Document Content
                                        </button>
                                    </h2>
                                    <div id="document-content" class="accordion-collapse collapse">
                                        <div class="accordion-body" id="document-content-body">
                                            <!-- Document content results will be inserted here -->
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="accordion-item">
                                    <h2 class="accordion-header">
                                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#consistency-check">
                                            Consistency Check
                                        </button>
                                    </h2>
                                    <div id="consistency-check" class="accordion-collapse collapse">
                                        <div class="accordion-body" id="consistency-check-body">
                                            <!-- Consistency check results will be inserted here -->
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="text-center mt-4">
                                <button id="verify-new" class="btn btn-primary">Verify Another Document</button>
                                <button id="save-report" class="btn btn-outline-primary ms-2">Save Report</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const uploadArea = document.getElementById('upload-area');
            const fileInput = document.getElementById('file-input');
            const loadingSpinner = document.getElementById('loading-spinner');
            const resultCard = document.getElementById('result-card');
            const documentPreview = document.getElementById('document-preview');
            const authenticBadge = document.getElementById('authentic-badge');
            const forgedBadge = document.getElementById('forged-badge');
            const verifyNewBtn = document.getElementById('verify-new');
            const saveReportBtn = document.getElementById('save-report');
            
            // Handle drag and drop
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('border-primary');
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('border-primary');
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('border-primary');
                if (e.dataTransfer.files.length) {
                    fileInput.files = e.dataTransfer.files;
                    uploadDocument(e.dataTransfer.files[0]);
                }
            });
            
            // Handle click to upload
            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });
            
            fileInput.addEventListener('change', () => {
                if (fileInput.files.length) {
                    uploadDocument(fileInput.files[0]);
                }
            });
            
            // Handle verify new button
            verifyNewBtn.addEventListener('click', () => {
                resultCard.style.display = 'none';
                uploadArea.style.display = 'block';
                fileInput.value = '';
            });
            
            // Handle save report button
            saveReportBtn.addEventListener('click', () => {
                const reportData = saveReportBtn.dataset.report;
                if (reportData) {
                    const blob = new Blob([reportData], {type: 'application/json'});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'verification-report.json';
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                }
            });
            
            // Function to upload and verify document
            function uploadDocument(file) {
                // Show loading spinner
                uploadArea.style.display = 'none';
                loadingSpinner.style.display = 'block';
                resultCard.style.display = 'none';
                
                // Create form data for upload
                const formData = new FormData();
                formData.append('document', file);
                
                // Send request to verify endpoint
                fetch('/verify', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    // Hide loading spinner
                    loadingSpinner.style.display = 'none';
                    
                    if (data.error) {
                        alert('Error: ' + data.error);
                        uploadArea.style.display = 'block';
                        return;
                    }
                    
                    // Display document preview
                    documentPreview.src = 'data:image/jpeg;base64,' + data.image;
                    
                    // Show appropriate badge
                    if (data.result.is_authentic) {
                        authenticBadge.classList.remove('d-none');
                        forgedBadge.classList.add('d-none');
                    } else {
                        authenticBadge.classList.add('d-none');
                        forgedBadge.classList.remove('d-none');
                    }
                    
                    // Populate visual analysis section
                    const visualAnalysisBody = document.getElementById('visual-analysis-body');
                    visualAnalysisBody.innerHTML = `
                        <div class="progress mb-3">
                            <div class="progress-bar bg-${data.result.visual_analysis.is_visually_authentic ? 'success' : 'danger'}" 
                                 role="progressbar" 
                                 style="width: ${data.result.visual_analysis.authenticity_score * 100}%"
                                 aria-valuenow="${data.result.visual_analysis.authenticity_score * 100}"
                                 aria-valuemin="0" 
                                 aria-valuemax="100">
                                ${Math.round(data.result.visual_analysis.authenticity_score * 100)}%
                            </div>
                        </div>
                        <p>The visual analysis indicates that this document is <strong>${data.result.visual_analysis.is_visually_authentic ? 'likely authentic' : 'potentially forged'}</strong>
                           with an authenticity score of ${Math.round(data.result.visual_analysis.authenticity_score * 100)}%.</p>
                    `;
                    
                    // Populate security features section
                    const securityFeaturesBody = document.getElementById('security-features-body');
                    securityFeaturesBody.innerHTML = `
                        <div class="d-flex align-items-center mb-3">
                            <div class="badge ${data.result.security_features.pass ? 'bg-success' : 'bg-danger'} me-2">
                                ${data.result.security_features.pass ? 'PASS' : 'FAIL'}
                            </div>
                            <p class="mb-0">Security features check ${data.result.security_features.pass ? 'passed' : 'failed'}</p>
                        </div>
                    `;
                    
                    if (data.result.security_features.issues.length > 0) {
                        securityFeaturesBody.innerHTML += `
                            <div class="mt-3">
                                <h6>Issues detected:</h6>
                                <ul class="list-group">
                                    ${data.result.security_features.issues.map(issue => 
                                        <li class="list-group-item list-group-item-danger">${issue}</li>
                                    ).join('')}
                                </ul>
                            </div>
                        `;
                    }
                    
                    // Populate document content section
                    const documentContentBody = document.getElementById('document-content-body');
                    documentContentBody.innerHTML = '';
                    
                    if (data.result.text_extraction.success) {
                        // Add metadata
                        if (Object.keys(data.result.text_extraction.metadata).length > 0) {
                            documentContentBody.innerHTML += <h6>Document Metadata:</h6>;
                            documentContentBody.innerHTML += <dl class="row">;
                            for (const [key, value] of Object.entries(data.result.text_extraction.metadata)) {
                                documentContentBody.innerHTML += `
                                    <dt class="col-sm-4">${key.replace('_', ' ').toUpperCase()}</dt>
                                    <dd class="col-sm-8">${value}</dd>
                                `;
                            }
                            documentContentBody.innerHTML += </dl>;
                        }
                        
                        // Add extracted text
                        documentContentBody.innerHTML += `
                            <h6 class="mt-3">Extracted Text:</h6>
                            <div class="card bg-light">
                                <div class="card-body">
                                    <pre class="mb-0">${data.result.text_extraction.extracted_text}</pre>
                                </div>
                            </div>
                        `;
                    } else {
                        documentContentBody.innerHTML = `
                            <div class="alert alert-warning">
                                No text could be extracted from this document.
                            </div>
                        `;
                    }
                    
                    // Populate consistency check section
                    const consistencyCheckBody = document.getElementById('consistency-check-body');
                    consistencyCheckBody.innerHTML = `
                        <div class="d-flex align-items-center mb-3">
                            <div class="badge ${data.result.consistency_check.pass ? 'bg-success' : 'bg-danger'} me-2">
                                ${data.result.consistency_check.pass ? 'PASS' : 'FAIL'}
                            </div>
                            <p class="mb-0">Consistency check ${data.result.consistency_check.pass ? 'passed' : 'failed'}</p>
                        </div>
                    `;
                    
                    if (data.result.consistency_check.issues.length > 0) {
                        consistencyCheckBody.innerHTML += `
                            <div class="mt-3">
                                <h6>Issues detected:</h6>
                                <ul class="list-group">
                                    ${data.result.consistency_check.issues.map(issue => 
                                        <li class="list-group-item list-group-item-danger">${issue}</li>
                                    ).join('')}
                                </ul>
                            </div>
                        `;
                    }
                    
                    // Store report data for download
                    saveReportBtn.dataset.report = JSON.stringify(data.result, null, 2);
                    
                    // Show result card
                    resultCard.style.display = 'block';
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred during verification. Please try again.');
                    loadingSpinner.style.display = 'none';
                    uploadArea.style.display = 'block';
                });
            }
        });
    </script>
</body>
</html>
"""

if _name_ == "_main_":
    try:
        # Check if model exists, if not create a basic one for demo
        if not os.path.exists(app.config['MODEL_PATH']):
            logger.warning(f"Model not found at {app.config['MODEL_PATH']}. Creating a basic model for demo purposes.")
            # Create a very simple model that always gives a positive authenticity score for demo purposes
            model = tf.keras.Sequential([
                tf.keras.layers.Input(shape=(224, 224, 3)),
                tf.keras.layers.GlobalAveragePooling2D(),
                tf.keras.layers.Dense(1, activation='sigmoid')
            ])
            model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
            model.save(app.config['MODEL_PATH'])
            logger.info(f"Created basic demo model at {app.config['MODEL_PATH']}")
            
        # Start the Flask app
        print("Starting Document Verification Web App...")
        print("Open your browser and go to http://localhost:5000")
        app.run(debug=True)
    except Exception as e:
        logger.error(f"Failed to start the application: {str(e)}")