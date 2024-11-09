# api.py
from flask import Flask, request
from flask_restx import Api, Resource, fields
from logger import log
import os

app = Flask(__name__)

# Read version from lmsh
try:
    from lmsh import __version__ as lmsh_version
except ImportError:
    lmsh_version = "unknown"

# Create API blueprint
api = Api(
    app,
    version=lmsh_version,
    title='LMS Helper API',
    description='REST API for LMS Helper automation tool',
    doc='/doc'
)

# Define namespaces
ns_classroom = api.namespace('classroom', description='Classroom operations')
ns_assignment = api.namespace('assignment', description='Assignment operations')
ns_system = api.namespace('system', description='System operations')

# Define models
classroom_model = api.model('Classroom', {
    'name': fields.String(required=True, description='Classroom name'),
    'description': fields.String(description='Classroom description'),
    'course_code': fields.String(required=True, description='Course identifier')
})

assignment_model = api.model('Assignment', {
    'classroom_id': fields.String(required=True, description='ID of the target classroom'),
    'title': fields.String(required=True, description='Assignment title'),
    'description': fields.String(description='Assignment description'),
    'due_date': fields.String(description='Due date (YYYY-MM-DD)'),
    'points': fields.Integer(description='Maximum points available')
})

grade_model = api.model('Grade', {
    'assignment_id': fields.String(required=True, description='ID of the assignment to grade'),
    'student_id': fields.String(description='Specific student ID to grade'),
    'auto': fields.Boolean(description='Enable automatic grading if available')
})

# System endpoints
@ns_system.route('/version')
class Version(Resource):
    @api.doc(responses={200: 'Success'})
    def get(self):
        """Get service version information"""
        client_ip = request.headers.get('CF-Connecting-IP', request.remote_addr)
        return {
            'version': lmsh_version,
            'client_info': {
                'ip': client_ip,
                'country': request.headers.get('CF-IPCountry', 'unknown'),
                'ray_id': request.headers.get('CF-RAY', 'unknown')
            }
        }

@ns_system.route('/health')
class Health(Resource):
    @api.doc(responses={200: 'Service is healthy'})
    def get(self):
        """Check if the service is healthy"""
        return {
            'status': 'healthy',
            'version': lmsh_version
        }

# Classroom endpoints
@ns_classroom.route('/create')
class ClassroomCreate(Resource):
    @api.expect(classroom_model)
    @api.doc(responses={
        201: 'Classroom created',
        400: 'Invalid request',
        401: 'Unauthorized'
    })
    def post(self):
        """Create a new classroom"""
        log.info('Creating classroom: %s', request.json)
        return {'message': 'create_classroom command not implemented yet'}, 201

# Assignment endpoints
@ns_assignment.route('/create')
class AssignmentCreate(Resource):
    @api.expect(assignment_model)
    @api.doc(responses={
        201: 'Assignment created',
        400: 'Invalid request',
        401: 'Unauthorized',
        404: 'Classroom not found'
    })
    def post(self):
        """Create a new assignment"""
        log.info('Creating assignment: %s', request.json)
        return {'message': 'create_assignment command not implemented yet'}, 201

@ns_assignment.route('/grade')
class AssignmentGrade(Resource):
    @api.expect(grade_model)
    @api.doc(responses={
        200: 'Grading completed',
        400: 'Invalid request',
        401: 'Unauthorized',
        404: 'Assignment not found'
    })
    def post(self):
        """Grade assignments"""
        log.info('Grading assignment: %s', request.json)
        return {'message': 'grade_assignment command not implemented yet'}, 200

if __name__ == '__main__':
    log.info('API Service started, version: %s', lmsh_version)
    app.run(debug=True)
