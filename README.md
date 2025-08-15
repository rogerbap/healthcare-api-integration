# Healthcare API Integration Dashboard

A healthcare interoperability platform demonstrating API integration with Epic, Cerner, and Azure Health Data Services. Built with Python Flask and modern web technologies.

![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Flask](https://img.shields.io/badge/Flask-2.3.3-red)
![FHIR](https://img.shields.io/badge/FHIR-R4-orange)
![HL7](https://img.shields.io/badge/HL7-v2.8-purple)

## Features

- **FHIR R4 Validation** - Validate patient resources against healthcare standards
- **HL7 v2.x Processing** - Parse and transform legacy healthcare messages
- **Epic/Cerner Integration** - OAuth 2.0 authentication and API testing
- **Real-time Analytics** - Interactive charts for API performance monitoring
- **Azure Health APIs** - Cloud healthcare service integration

## Quick Start

```bash
# Clone and setup
git clone https://github.com/rogerbap/healthcare-api-integration.git
cd healthcare-api-integration

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash

# Install dependencies
pip install Flask Flask-CORS requests python-dotenv

# Run application
python server/app.py
```

Open http://localhost:5000 to view the dashboard.

## Project Structure

```
healthcare-api-integration/
├── server/app.py              # Flask backend API
├── client/
│   ├── templates/index.html   # Dashboard UI
│   └── static/
│       ├── css/styles.css     # Styling
│       └── js/                # Frontend modules
├── requirements.txt
└── README.md
```

## Technologies

- **Backend:** Python Flask, FHIR R4, HL7 v2.8
- **Frontend:** HTML5, CSS3, JavaScript ES6+, Chart.js
- **Healthcare APIs:** Epic Interconnect, Cerner PowerChart, Azure Health Data Services
- **Standards:** OAuth 2.0, SMART on FHIR, HIPAA compliance patterns

## Demo Features

1. **FHIR Validation Console** - Test patient resource validation
2. **HL7 Message Parser** - Parse ADT/ORM/ORU messages and transform to FHIR
3. **API Testing** - Live connection tests for Epic and Cerner
4. **Performance Monitoring** - Real-time charts and system health metrics

## Sample Data

**FHIR Patient Resource:**
```json
{
  "resourceType": "Patient",
  "id": "12345",
  "name": [{"family": "Doe", "given": ["John"]}],
  "gender": "male",
  "birthDate": "1990-01-01"
}
```

**HL7 ADT Message:**
```
MSH|^~\&|EPIC|HOSPITAL||LAB|202501121400||ADT^A01|12345|P|2.8
PID|1||123456789^^^MRN||DOE^JANE||19900101|F
```

## Purpose

Portfolio project demonstrating healthcare IT skills:
- Healthcare interoperability standards knowledge
- API development and integration patterns
- Full-stack development capabilities
- Understanding of Epic/Cerner EHR systems