# healthcare_api_backend/app.py
"""
Healthcare API Integration Backend
Flask application for healthcare interoperability dashboard
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import logging
import os
import time
import random
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
           template_folder='../client/templates',
           static_folder='../client/static')
CORS(app)  # Enable CORS for frontend integration

# Healthcare API service classes
class FHIRService:
    """FHIR R4 service for patient resource management"""
    
    def __init__(self):
        self.base_url = "https://fhir.epic.com/interconnect-fhir-oauth"
        logger.info("FHIR Service initialized")
    
    def validate_patient_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Validate FHIR R4 Patient resource"""
        logger.info(f"Validating FHIR resource: {resource.get('resourceType', 'Unknown')}")
        
        errors = []
        checks = []
        
        # Required field validation
        if not resource.get('resourceType'):
            errors.append("Missing required field: resourceType")
        else:
            checks.append(f"ResourceType '{resource['resourceType']}' present")
        
        # Patient-specific validation
        if resource.get('resourceType') == 'Patient':
            if not resource.get('identifier') or len(resource['identifier']) == 0:
                errors.append("Patient resource missing identifier")
            else:
                checks.append("Patient identifier present")
            
            if not resource.get('name') or len(resource['name']) == 0:
                errors.append("Patient resource missing name")
            else:
                checks.append("Patient name present")
            
            gender = resource.get('gender')
            if gender and gender not in ['male', 'female', 'other', 'unknown']:
                errors.append("Invalid gender value")
            elif gender:
                checks.append("Valid gender value")
        
        is_valid = len(errors) == 0
        logger.info(f"FHIR validation result: {'VALID' if is_valid else 'INVALID'}")
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'checks': checks,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_patient_metrics(self) -> Dict[str, Any]:
        """Get current patient metrics"""
        metrics = {
            'active_patients': 2847 + random.randint(0, 100),
            'requests_per_minute': 156 + random.randint(-20, 20),
            'uptime_percentage': round(99.8 + random.uniform(-0.2, 0.2), 1),
            'response_time_ms': 145 + random.randint(-30, 30)
        }
        
        logger.info(f"Generated FHIR patient metrics: {metrics}")
        return metrics


class HL7Service:
    """HL7 v2.x message processing service"""
    
    def __init__(self):
        self.message_types = {
            'ADT^A01': 'Admit Patient',
            'ADT^A08': 'Update Patient Information',
            'ORM^O01': 'Order Message',
            'ORU^R01': 'Observation Result',
            'DFT^P03': 'Post Detail Financial Transaction'
        }
        logger.info("HL7 Service initialized")
    
    def parse_hl7_message(self, hl7_message: str) -> Dict[str, Any]:
        """Parse HL7 v2.x message and extract key information"""
        logger.info("Parsing HL7 message")
        
        try:
            segments = hl7_message.strip().split('\n')
            parsed_data = {
                'message_type': 'Unknown',
                'control_id': 'Unknown',
                'processing_id': 'Unknown',
                'segments': {},
                'patient_info': {}
            }
            
            for segment in segments:
                fields = segment.split('|')
                segment_type = fields[0] if fields else ''
                
                if segment_type == 'MSH':
                    parsed_data['message_type'] = fields[8] if len(fields) > 8 else 'Unknown'
                    parsed_data['control_id'] = fields[9] if len(fields) > 9 else 'Unknown'
                    parsed_data['processing_id'] = fields[10] if len(fields) > 10 else 'Unknown'
                    parsed_data['segments']['MSH'] = 'Message Header'
                    
                elif segment_type == 'PID':
                    parsed_data['patient_info'] = {
                        'patient_id': fields[3].split('^')[0] if len(fields) > 3 else '',
                        'patient_name': fields[5].replace('^', ' ') if len(fields) > 5 else '',
                        'date_of_birth': fields[7] if len(fields) > 7 else '',
                        'gender': fields[8] if len(fields) > 8 else ''
                    }
                    parsed_data['segments']['PID'] = 'Patient Identification'
                    
                elif segment_type == 'PV1':
                    parsed_data['segments']['PV1'] = 'Patient Visit'
                elif segment_type == 'EVN':
                    parsed_data['segments']['EVN'] = 'Event Type'
            
            logger.info(f"Successfully parsed HL7 message type: {parsed_data['message_type']}")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing HL7 message: {str(e)}")
            raise ValueError(f"Invalid HL7 message format: {str(e)}")
    
    def transform_hl7_to_fhir(self, hl7_message: str) -> Dict[str, Any]:
        """Transform HL7 v2.x message to FHIR Patient resource"""
        logger.info("Transforming HL7 to FHIR")
        
        parsed = self.parse_hl7_message(hl7_message)
        patient_info = parsed.get('patient_info', {})
        
        fhir_patient = {
            'resourceType': 'Patient',
            'id': patient_info.get('patient_id', 'unknown'),
            'identifier': [{
                'use': 'usual',
                'type': {
                    'coding': [{
                        'system': 'http://terminology.hl7.org/CodeSystem/v2-0203',
                        'code': 'MR',
                        'display': 'Medical Record Number'
                    }]
                },
                'value': patient_info.get('patient_id', '')
            }],
            'active': True,
            'name': [{
                'use': 'official',
                'text': patient_info.get('patient_name', ''),
                'family': patient_info.get('patient_name', '').split(' ')[0] if patient_info.get('patient_name') else '',
                'given': patient_info.get('patient_name', '').split(' ')[1:] if patient_info.get('patient_name') else []
            }],
            'gender': self._map_hl7_gender_to_fhir(patient_info.get('gender', '')),
            'birthDate': self._format_hl7_date(patient_info.get('date_of_birth', ''))
        }
        
        logger.info(f"Successfully transformed HL7 to FHIR Patient: {fhir_patient['id']}")
        return fhir_patient
    
    def _map_hl7_gender_to_fhir(self, hl7_gender: str) -> str:
        """Map HL7 gender codes to FHIR gender values"""
        mapping = {'M': 'male', 'F': 'female', 'O': 'other', 'U': 'unknown'}
        return mapping.get(hl7_gender.upper(), 'unknown')
    
    def _format_hl7_date(self, hl7_date: str) -> str:
        """Convert HL7 date format (YYYYMMDD) to FHIR date format (YYYY-MM-DD)"""
        if hl7_date and len(hl7_date) >= 8:
            return f"{hl7_date[:4]}-{hl7_date[4:6]}-{hl7_date[6:8]}"
        return None
    
    def get_message_metrics(self) -> Dict[str, Any]:
        """Get current HL7 message processing metrics"""
        metrics = {
            'daily_message_count': 1234 + random.randint(0, 200),
            'avg_processing_time': round(2.3 + random.uniform(-0.5, 0.5), 1),
            'most_common_type': 'ADT^A01',
            'queue_depth': random.randint(10, 100)
        }
        
        logger.info(f"Generated HL7 metrics: {metrics}")
        return metrics


class EpicService:
    """Epic Interconnect integration service"""
    
    def __init__(self):
        self.base_url = "https://fhir.epic.com/interconnect-fhir-oauth"
        self.client_id = os.getenv('EPIC_CLIENT_ID', 'demo-client-id')
        logger.info("Epic Service initialized")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Epic MyChart connection"""
        logger.info("Testing Epic connection")
        
        # Simulate connection test
        time.sleep(1)  # Simulate network delay
        
        test_results = {
            'oauth_auth': {'status': 'success', 'response_time': 145},
            'patient_api': {'status': 'success', 'response_time': 167},
            'appointment_api': {'status': 'success', 'response_time': 134},
            'provider_directory': {'status': 'success', 'response_time': 156},
            'overall_status': 'operational'
        }
        
        logger.info(f"Epic connection test results: {test_results['overall_status']}")
        return test_results
    
    def get_epic_metrics(self) -> Dict[str, Any]:
        """Get Epic integration metrics"""
        metrics = {
            'provider_organizations': 847,
            'patient_records': '23.4M',
            'response_time_ms': 145 + random.randint(-25, 25),
            'api_calls_per_second': 156 + random.randint(-20, 20)
        }
        
        logger.info(f"Generated Epic metrics: {metrics}")
        return metrics


class CernerService:
    """Cerner PowerChart integration service"""
    
    def __init__(self):
        self.base_url = "https://fhir-open.cerner.com"
        logger.info("Cerner Service initialized")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Cerner PowerChart connection"""
        logger.info("Testing Cerner connection")
        
        # Simulate connection test
        time.sleep(1)  # Simulate network delay
        
        test_results = {
            'smart_on_fhir': {'status': 'connected', 'response_time': 189},
            'medication_orders': {'status': 'active', 'response_time': 156},
            'lab_results': {'status': 'syncing', 'response_time': 198},
            'radiology_reports': {'status': 'delayed', 'response_time': 890},
            'overall_status': 'operational_with_delays'
        }
        
        logger.info(f"Cerner connection test results: {test_results['overall_status']}")
        return test_results
    
    def get_cerner_metrics(self) -> Dict[str, Any]:
        """Get Cerner integration metrics"""
        metrics = {
            'connected_facilities': 234,
            'medication_orders_today': 1567,
            'lab_results_processed': 892,
            'average_response_time': 189 + random.randint(-30, 30)
        }
        
        logger.info(f"Generated Cerner metrics: {metrics}")
        return metrics


class AzureHealthService:
    """Azure Health Data Services integration"""
    
    def __init__(self):
        self.workspace_url = "https://yourworkspace-yourfhirservice.fhir.azurehealthcareapis.com"
        logger.info("Azure Health Service initialized")
    
    def get_azure_metrics(self) -> Dict[str, Any]:
        """Get Azure Health Data Services metrics"""
        metrics = {
            'sla_compliance': round(99.8 + random.uniform(-0.2, 0.2), 1),
            'data_processed_tb': round(2.1 + random.uniform(-0.3, 0.3), 1),
            'api_calls_per_second': 156 + random.randint(-30, 30),
            'storage_used_gb': 15678 + random.randint(-1000, 1000)
        }
        
        logger.info(f"Generated Azure Health metrics: {metrics}")
        return metrics


# Initialize services
fhir_service = FHIRService()
hl7_service = HL7Service()
epic_service = EpicService()
cerner_service = CernerService()
azure_service = AzureHealthService()


# API Routes
@app.route('/')
def index():
    """Serve the main dashboard"""
    logger.info("Serving main dashboard")
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'fhir': 'operational',
            'hl7': 'operational',
            'epic': 'operational',
            'cerner': 'operational',
            'azure': 'operational'
        }
    })


@app.route('/api/fhir/validate', methods=['POST'])
def validate_fhir():
    """Validate FHIR resource"""
    try:
        resource = request.json
        logger.info(f"FHIR validation requested for resource type: {resource.get('resourceType', 'Unknown')}")
        
        validation_result = fhir_service.validate_patient_resource(resource)
        return jsonify(validation_result)
        
    except Exception as e:
        logger.error(f"FHIR validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/fhir/metrics', methods=['GET'])
def get_fhir_metrics():
    """Get FHIR service metrics"""
    logger.info("FHIR metrics requested")
    metrics = fhir_service.get_patient_metrics()
    return jsonify(metrics)


@app.route('/api/hl7/parse', methods=['POST'])
def parse_hl7():
    """Parse HL7 message"""
    try:
        hl7_message = request.json.get('message', '')
        logger.info("HL7 parsing requested")
        
        parsed_result = hl7_service.parse_hl7_message(hl7_message)
        return jsonify(parsed_result)
        
    except Exception as e:
        logger.error(f"HL7 parsing error: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/hl7/transform', methods=['POST'])
def transform_hl7_to_fhir():
    """Transform HL7 to FHIR"""
    try:
        hl7_message = request.json.get('message', '')
        logger.info("HL7 to FHIR transformation requested")
        
        fhir_resource = hl7_service.transform_hl7_to_fhir(hl7_message)
        return jsonify(fhir_resource)
        
    except Exception as e:
        logger.error(f"HL7 to FHIR transformation error: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/hl7/metrics', methods=['GET'])
def get_hl7_metrics():
    """Get HL7 service metrics"""
    logger.info("HL7 metrics requested")
    metrics = hl7_service.get_message_metrics()
    return jsonify(metrics)


@app.route('/api/epic/test', methods=['POST'])
def test_epic_connection():
    """Test Epic connection"""
    logger.info("Epic connection test requested")
    test_results = epic_service.test_connection()
    return jsonify(test_results)


@app.route('/api/epic/metrics', methods=['GET'])
def get_epic_metrics():
    """Get Epic integration metrics"""
    logger.info("Epic metrics requested")
    metrics = epic_service.get_epic_metrics()
    return jsonify(metrics)


@app.route('/api/cerner/test', methods=['POST'])
def test_cerner_connection():
    """Test Cerner connection"""
    logger.info("Cerner connection test requested")
    test_results = cerner_service.test_connection()
    return jsonify(test_results)


@app.route('/api/cerner/metrics', methods=['GET'])
def get_cerner_metrics():
    """Get Cerner integration metrics"""
    logger.info("Cerner metrics requested")
    metrics = cerner_service.get_cerner_metrics()
    return jsonify(metrics)


@app.route('/api/azure/metrics', methods=['GET'])
def get_azure_metrics():
    """Get Azure Health Data Services metrics"""
    logger.info("Azure Health metrics requested")
    metrics = azure_service.get_azure_metrics()
    return jsonify(metrics)


@app.route('/api/analytics/response-times', methods=['GET'])
def get_response_times():
    """Get API response time analytics"""
    logger.info("Response time analytics requested")
    
    # Generate realistic response time data
    time_labels = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00']
    
    response_data = {
        'labels': time_labels,
        'datasets': [
            {
                'label': 'FHIR API',
                'data': [145 + random.randint(-20, 20) for _ in time_labels],
                'borderColor': '#059669'
            },
            {
                'label': 'HL7 Processing',
                'data': [230 + random.randint(-30, 30) for _ in time_labels],
                'borderColor': '#e67e22'
            },
            {
                'label': 'Epic Bridge',
                'data': [167 + random.randint(-25, 25) for _ in time_labels],
                'borderColor': '#6b46c1'
            }
        ]
    }
    
    return jsonify(response_data)


@app.route('/api/analytics/message-volume', methods=['GET'])
def get_message_volume():
    """Get HL7 message volume analytics"""
    logger.info("Message volume analytics requested")
    
    volume_data = {
        'labels': ['ADT (Admit/Discharge)', 'ORM (Orders)', 'ORU (Results)', 'DFT (Financial)'],
        'data': [45 + random.randint(-5, 5) for _ in range(4)],
        'backgroundColor': ['#0078d4', '#e67e22', '#6b46c1', '#059669']
    }
    
    return jsonify(volume_data)


@app.route('/api/analytics/system-health', methods=['GET'])
def get_system_health():
    """Get system health analytics"""
    logger.info("System health analytics requested")
    
    health_data = {
        'labels': ['Epic Bridge', 'Cerner API', 'FHIR Service', 'HL7 Engine', 'Azure Health'],
        'data': [
            round(99.8 + random.uniform(-0.2, 0.2), 1) for _ in range(5)
        ],
        'backgroundColor': ['#6b46c1', '#e67e22', '#059669', '#f59e0b', '#0078d4']
    }
    
    return jsonify(health_data)


if __name__ == '__main__':
    # Set environment variables for development
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', 'True')
    
    logger.info("Starting Healthcare API Integration Backend")
    app.run(host='0.0.0.0', port=5000, debug=True)