"""
Enterprise Integration & API Platform for NeuroPulse
Provides SSO integration, API gateway, LRS compliance, and enterprise directory services
"""

import json
import os
import uuid
import jwt
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlencode
import requests

class EnterpriseIntegrationManager:
    def __init__(self):
        self.sso_configs_file = 'sso_configurations.json'
        self.api_keys_file = 'api_keys_data.json'
        self.oauth_tokens_file = 'oauth_tokens_data.json'
        self.directory_sync_file = 'directory_sync_data.json'
        self.lrs_records_file = 'learning_records_store.json'
        
        self.load_data()
    
    def load_data(self):
        """Load enterprise integration data"""
        self.sso_configs = self._load_json_file(self.sso_configs_file, {})
        self.api_keys = self._load_json_file(self.api_keys_file, {})
        self.oauth_tokens = self._load_json_file(self.oauth_tokens_file, {})
        self.directory_sync = self._load_json_file(self.directory_sync_file, {})
        self.lrs_records = self._load_json_file(self.lrs_records_file, {})
    
    def _load_json_file(self, filename: str, default: dict) -> dict:
        """Load JSON file with fallback to default"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default
    
    def _save_json_file(self, filename: str, data: dict):
        """Save data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def configure_sso_provider(self, institution_id: str, provider_config: dict) -> str:
        """Configure SSO provider for institution"""
        config_id = str(uuid.uuid4())
        
        sso_config = {
            'config_id': config_id,
            'institution_id': institution_id,
            'provider_type': provider_config['provider_type'],  # saml, oauth2, oidc
            'provider_name': provider_config['provider_name'],
            'enabled': True,
            'configuration': self._process_provider_config(provider_config),
            'attribute_mapping': provider_config.get('attribute_mapping', self._get_default_attribute_mapping()),
            'auto_provisioning': provider_config.get('auto_provisioning', True),
            'default_role': provider_config.get('default_role', 'student'),
            'created_at': datetime.now().isoformat(),
            'last_tested': None,
            'test_results': {}
        }
        
        self.sso_configs[config_id] = sso_config
        self._save_json_file(self.sso_configs_file, self.sso_configs)
        
        return config_id
    
    def _process_provider_config(self, config: dict) -> dict:
        """Process and validate provider configuration"""
        provider_type = config['provider_type']
        
        if provider_type == 'saml':
            return {
                'entity_id': config['entity_id'],
                'sso_url': config['sso_url'],
                'slo_url': config.get('slo_url'),
                'certificate': config['certificate'],
                'signature_algorithm': config.get('signature_algorithm', 'RSA_SHA256'),
                'digest_algorithm': config.get('digest_algorithm', 'SHA256'),
                'name_id_format': config.get('name_id_format', 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress')
            }
        
        elif provider_type == 'oauth2' or provider_type == 'oidc':
            return {
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'authorization_url': config['authorization_url'],
                'token_url': config['token_url'],
                'user_info_url': config.get('user_info_url'),
                'scope': config.get('scope', 'openid profile email'),
                'redirect_uri': f"{config.get('base_url', 'https://app.neuropulse.com')}/auth/callback/{provider_type}"
            }
        
        elif provider_type == 'ldap':
            return {
                'server_url': config['server_url'],
                'bind_dn': config['bind_dn'],
                'bind_password': config['bind_password'],
                'user_search_base': config['user_search_base'],
                'user_search_filter': config.get('user_search_filter', '(mail={username})'),
                'group_search_base': config.get('group_search_base'),
                'use_ssl': config.get('use_ssl', True),
                'port': config.get('port', 636 if config.get('use_ssl', True) else 389)
            }
        
        return config
    
    def _get_default_attribute_mapping(self) -> dict:
        """Get default attribute mapping for SSO"""
        return {
            'user_id': 'sub',
            'email': 'email',
            'first_name': 'given_name',
            'last_name': 'family_name',
            'display_name': 'name',
            'groups': 'groups',
            'department': 'department',
            'title': 'job_title'
        }
    
    def initiate_sso_login(self, config_id: str, return_url: str = None) -> dict:
        """Initiate SSO login process"""
        if config_id not in self.sso_configs:
            return {'error': 'SSO configuration not found'}
        
        config = self.sso_configs[config_id]
        provider_type = config['provider_type']
        
        if provider_type == 'saml':
            return self._initiate_saml_login(config, return_url)
        elif provider_type in ['oauth2', 'oidc']:
            return self._initiate_oauth_login(config, return_url)
        else:
            return {'error': 'Unsupported provider type'}
    
    def _initiate_saml_login(self, config: dict, return_url: str) -> dict:
        """Initiate SAML login"""
        # Generate SAML AuthnRequest
        request_id = str(uuid.uuid4())
        
        authn_request = {
            'id': request_id,
            'destination': config['configuration']['sso_url'],
            'assertion_consumer_service_url': f"https://app.neuropulse.com/auth/saml/callback",
            'issuer': 'https://app.neuropulse.com',
            'name_id_format': config['configuration']['name_id_format'],
            'created_at': datetime.now().isoformat()
        }
        
        # Store request for validation
        self.oauth_tokens[request_id] = {
            'type': 'saml_request',
            'config_id': config['config_id'],
            'return_url': return_url,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(minutes=10)).isoformat()
        }
        
        self._save_json_file(self.oauth_tokens_file, self.oauth_tokens)
        
        return {
            'redirect_url': config['configuration']['sso_url'],
            'request_id': request_id,
            'method': 'POST',
            'form_data': self._build_saml_request(authn_request)
        }
    
    def _initiate_oauth_login(self, config: dict, return_url: str) -> dict:
        """Initiate OAuth2/OIDC login"""
        state = str(uuid.uuid4())
        nonce = str(uuid.uuid4())
        
        # Store state for validation
        self.oauth_tokens[state] = {
            'type': 'oauth_state',
            'config_id': config['config_id'],
            'return_url': return_url,
            'nonce': nonce,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(minutes=10)).isoformat()
        }
        
        self._save_json_file(self.oauth_tokens_file, self.oauth_tokens)
        
        # Build authorization URL
        params = {
            'client_id': config['configuration']['client_id'],
            'response_type': 'code',
            'scope': config['configuration']['scope'],
            'redirect_uri': config['configuration']['redirect_uri'],
            'state': state,
            'nonce': nonce
        }
        
        auth_url = f"{config['configuration']['authorization_url']}?{urlencode(params)}"
        
        return {
            'redirect_url': auth_url,
            'state': state,
            'method': 'GET'
        }
    
    def _build_saml_request(self, request_data: dict) -> dict:
        """Build SAML AuthnRequest form data"""
        # Simplified SAML request building
        saml_request = f"""
        <samlp:AuthnRequest
            ID="{request_data['id']}"
            Version="2.0"
            IssueInstant="{request_data['created_at']}"
            Destination="{request_data['destination']}"
            AssertionConsumerServiceURL="{request_data['assertion_consumer_service_url']}"
            xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
            <saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">{request_data['issuer']}</saml:Issuer>
        </samlp:AuthnRequest>
        """
        
        # Base64 encode the request
        encoded_request = base64.b64encode(saml_request.encode()).decode()
        
        return {
            'SAMLRequest': encoded_request,
            'RelayState': request_data.get('return_url', '')
        }
    
    def process_sso_callback(self, provider_type: str, callback_data: dict) -> dict:
        """Process SSO callback and authenticate user"""
        if provider_type == 'saml':
            return self._process_saml_callback(callback_data)
        elif provider_type in ['oauth2', 'oidc']:
            return self._process_oauth_callback(callback_data)
        else:
            return {'error': 'Unsupported provider type'}
    
    def _process_oauth_callback(self, callback_data: dict) -> dict:
        """Process OAuth2/OIDC callback"""
        state = callback_data.get('state')
        code = callback_data.get('code')
        
        if not state or state not in self.oauth_tokens:
            return {'error': 'Invalid state parameter'}
        
        token_data = self.oauth_tokens[state]
        config = self.sso_configs[token_data['config_id']]
        
        # Exchange code for token
        token_response = self._exchange_oauth_code(config, code)
        
        if 'error' in token_response:
            return token_response
        
        # Get user info
        user_info = self._get_oauth_user_info(config, token_response['access_token'])
        
        if 'error' in user_info:
            return user_info
        
        # Map attributes and create/update user
        mapped_user = self._map_user_attributes(user_info, config['attribute_mapping'])
        user_result = self._provision_user(mapped_user, config)
        
        # Clean up state
        del self.oauth_tokens[state]
        self._save_json_file(self.oauth_tokens_file, self.oauth_tokens)
        
        return {
            'success': True,
            'user': user_result,
            'return_url': token_data.get('return_url', '/'),
            'session_token': self._generate_session_token(user_result['user_id'])
        }
    
    def _exchange_oauth_code(self, config: dict, code: str) -> dict:
        """Exchange OAuth authorization code for access token"""
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': config['configuration']['redirect_uri'],
            'client_id': config['configuration']['client_id'],
            'client_secret': config['configuration']['client_secret']
        }
        
        try:
            response = requests.post(
                config['configuration']['token_url'],
                data=token_data,
                headers={'Accept': 'application/json'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'Token exchange failed: {response.text}'}
                
        except requests.RequestException as e:
            return {'error': f'Token exchange request failed: {str(e)}'}
    
    def _get_oauth_user_info(self, config: dict, access_token: str) -> dict:
        """Get user information from OAuth provider"""
        user_info_url = config['configuration'].get('user_info_url')
        
        if not user_info_url:
            return {'error': 'User info URL not configured'}
        
        try:
            response = requests.get(
                user_info_url,
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'User info request failed: {response.text}'}
                
        except requests.RequestException as e:
            return {'error': f'User info request failed: {str(e)}'}
    
    def _map_user_attributes(self, user_data: dict, mapping: dict) -> dict:
        """Map SSO user attributes to internal user model"""
        mapped_user = {}
        
        for internal_attr, external_attr in mapping.items():
            if external_attr in user_data:
                mapped_user[internal_attr] = user_data[external_attr]
        
        return mapped_user
    
    def _provision_user(self, user_data: dict, config: dict) -> dict:
        """Provision or update user from SSO"""
        user_id = user_data.get('user_id') or user_data.get('email')
        
        if not user_id:
            return {'error': 'No valid user identifier found'}
        
        # Check if user exists
        # In production, this would integrate with your user management system
        user_record = {
            'user_id': user_id,
            'email': user_data.get('email'),
            'first_name': user_data.get('first_name'),
            'last_name': user_data.get('last_name'),
            'display_name': user_data.get('display_name'),
            'institution_id': config['institution_id'],
            'role': self._determine_user_role(user_data, config),
            'sso_provider': config['provider_name'],
            'last_login': datetime.now().isoformat(),
            'created_via_sso': True
        }
        
        return {'user_id': user_id, 'user_data': user_record}
    
    def _determine_user_role(self, user_data: dict, config: dict) -> str:
        """Determine user role based on SSO attributes"""
        groups = user_data.get('groups', [])
        
        # Role mapping based on groups
        if 'administrators' in groups or 'admin' in groups:
            return 'admin'
        elif 'instructors' in groups or 'faculty' in groups:
            return 'instructor'
        elif 'teaching_assistants' in groups or 'ta' in groups:
            return 'teaching_assistant'
        else:
            return config['default_role']
    
    def _generate_session_token(self, user_id: str) -> str:
        """Generate JWT session token"""
        payload = {
            'user_id': user_id,
            'iat': datetime.now(),
            'exp': datetime.now() + timedelta(hours=8)
        }
        
        # In production, use a proper secret key
        secret_key = os.environ.get('JWT_SECRET_KEY', 'development-secret')
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    def generate_api_key(self, user_id: str, institution_id: str, permissions: List[str]) -> str:
        """Generate API key for external integrations"""
        api_key_id = str(uuid.uuid4())
        api_key = self._generate_secure_api_key()
        
        api_key_data = {
            'api_key_id': api_key_id,
            'api_key_hash': hashlib.sha256(api_key.encode()).hexdigest(),
            'user_id': user_id,
            'institution_id': institution_id,
            'permissions': permissions,
            'created_at': datetime.now().isoformat(),
            'last_used': None,
            'usage_count': 0,
            'rate_limit': {
                'requests_per_hour': 1000,
                'current_usage': 0,
                'reset_time': datetime.now().isoformat()
            },
            'active': True
        }
        
        self.api_keys[api_key_id] = api_key_data
        self._save_json_file(self.api_keys_file, self.api_keys)
        
        return api_key
    
    def _generate_secure_api_key(self) -> str:
        """Generate cryptographically secure API key"""
        import secrets
        return f"np_{secrets.token_urlsafe(32)}"
    
    def validate_api_key(self, api_key: str) -> dict:
        """Validate API key and return permissions"""
        api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        for key_id, key_data in self.api_keys.items():
            if key_data['api_key_hash'] == api_key_hash and key_data['active']:
                # Check rate limiting
                if self._is_rate_limited(key_data):
                    return {'error': 'Rate limit exceeded'}
                
                # Update usage
                key_data['last_used'] = datetime.now().isoformat()
                key_data['usage_count'] += 1
                key_data['rate_limit']['current_usage'] += 1
                
                self._save_json_file(self.api_keys_file, self.api_keys)
                
                return {
                    'valid': True,
                    'user_id': key_data['user_id'],
                    'institution_id': key_data['institution_id'],
                    'permissions': key_data['permissions'],
                    'rate_limit_remaining': key_data['rate_limit']['requests_per_hour'] - key_data['rate_limit']['current_usage']
                }
        
        return {'valid': False, 'error': 'Invalid API key'}
    
    def _is_rate_limited(self, key_data: dict) -> bool:
        """Check if API key is rate limited"""
        rate_limit = key_data['rate_limit']
        reset_time = datetime.fromisoformat(rate_limit['reset_time'])
        
        # Reset counter if hour has passed
        if datetime.now() > reset_time + timedelta(hours=1):
            rate_limit['current_usage'] = 0
            rate_limit['reset_time'] = datetime.now().isoformat()
            return False
        
        return rate_limit['current_usage'] >= rate_limit['requests_per_hour']
    
    def record_learning_activity(self, user_id: str, activity_data: dict) -> str:
        """Record learning activity in xAPI format for LRS compliance"""
        statement_id = str(uuid.uuid4())
        
        # Build xAPI statement
        xapi_statement = {
            'id': statement_id,
            'actor': {
                'mbox': f"mailto:{activity_data.get('user_email', 'unknown@example.com')}",
                'name': activity_data.get('user_name', 'Unknown User')
            },
            'verb': {
                'id': activity_data.get('verb_id', 'http://adlnet.gov/expapi/verbs/experienced'),
                'display': {'en-US': activity_data.get('verb_display', 'experienced')}
            },
            'object': {
                'id': activity_data.get('object_id', f"https://app.neuropulse.com/activities/{uuid.uuid4()}"),
                'definition': {
                    'name': {'en-US': activity_data.get('activity_name', 'Learning Activity')},
                    'description': {'en-US': activity_data.get('activity_description', '')},
                    'type': activity_data.get('activity_type', 'http://adlnet.gov/expapi/activities/lesson')
                }
            },
            'timestamp': datetime.now().isoformat() + 'Z',
            'stored': datetime.now().isoformat() + 'Z',
            'authority': {
                'mbox': 'mailto:system@neuropulse.com',
                'name': 'NeuroPulse Learning Platform'
            }
        }
        
        # Add result if provided
        if 'result' in activity_data:
            xapi_statement['result'] = activity_data['result']
        
        # Add context if provided
        if 'context' in activity_data:
            xapi_statement['context'] = activity_data['context']
        
        # Store the statement
        self.lrs_records[statement_id] = xapi_statement
        self._save_json_file(self.lrs_records_file, self.lrs_records)
        
        return statement_id
    
    def sync_with_directory(self, institution_id: str, directory_config: dict) -> dict:
        """Sync users with enterprise directory (LDAP/Active Directory)"""
        sync_id = str(uuid.uuid4())
        
        sync_result = {
            'sync_id': sync_id,
            'institution_id': institution_id,
            'started_at': datetime.now().isoformat(),
            'status': 'in_progress',
            'users_processed': 0,
            'users_created': 0,
            'users_updated': 0,
            'users_deactivated': 0,
            'errors': []
        }
        
        try:
            # In production, this would connect to actual LDAP/AD
            # For now, simulate directory sync
            directory_users = self._simulate_directory_fetch(directory_config)
            
            for directory_user in directory_users:
                try:
                    result = self._sync_directory_user(directory_user, institution_id)
                    sync_result['users_processed'] += 1
                    
                    if result['action'] == 'created':
                        sync_result['users_created'] += 1
                    elif result['action'] == 'updated':
                        sync_result['users_updated'] += 1
                    elif result['action'] == 'deactivated':
                        sync_result['users_deactivated'] += 1
                        
                except Exception as e:
                    sync_result['errors'].append({
                        'user': directory_user.get('username', 'unknown'),
                        'error': str(e)
                    })
            
            sync_result['status'] = 'completed'
            sync_result['completed_at'] = datetime.now().isoformat()
            
        except Exception as e:
            sync_result['status'] = 'failed'
            sync_result['error'] = str(e)
            sync_result['completed_at'] = datetime.now().isoformat()
        
        # Store sync result
        self.directory_sync[sync_id] = sync_result
        self._save_json_file(self.directory_sync_file, self.directory_sync)
        
        return sync_result
    
    def _simulate_directory_fetch(self, config: dict) -> List[dict]:
        """Simulate fetching users from directory service"""
        # In production, this would use ldap3 or similar library
        return [
            {
                'username': 'john.doe',
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'department': 'Engineering',
                'title': 'Senior Developer',
                'groups': ['developers', 'engineers'],
                'active': True
            },
            {
                'username': 'jane.smith',
                'email': 'jane.smith@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'department': 'Education',
                'title': 'Instructor',
                'groups': ['instructors', 'faculty'],
                'active': True
            }
        ]
    
    def _sync_directory_user(self, directory_user: dict, institution_id: str) -> dict:
        """Sync individual user from directory"""
        user_id = directory_user['username']
        
        # Check if user exists in our system
        # In production, this would check your user database
        
        user_data = {
            'user_id': user_id,
            'email': directory_user['email'],
            'first_name': directory_user['first_name'],
            'last_name': directory_user['last_name'],
            'department': directory_user.get('department'),
            'title': directory_user.get('title'),
            'institution_id': institution_id,
            'directory_groups': directory_user.get('groups', []),
            'active': directory_user.get('active', True),
            'last_directory_sync': datetime.now().isoformat()
        }
        
        # Determine action (created/updated/deactivated)
        return {'action': 'updated', 'user_data': user_data}
    
    def get_integration_health(self, institution_id: str) -> dict:
        """Get health status of all integrations for institution"""
        health_status = {
            'institution_id': institution_id,
            'overall_status': 'healthy',
            'checked_at': datetime.now().isoformat(),
            'sso_status': {},
            'api_usage': {},
            'directory_sync': {},
            'lrs_status': {}
        }
        
        # Check SSO configurations
        institution_sso = [config for config in self.sso_configs.values() 
                          if config['institution_id'] == institution_id]
        
        for sso_config in institution_sso:
            health_status['sso_status'][sso_config['provider_name']] = {
                'enabled': sso_config['enabled'],
                'last_tested': sso_config.get('last_tested'),
                'status': 'active' if sso_config['enabled'] else 'inactive'
            }
        
        # Check API usage
        institution_apis = [key for key in self.api_keys.values() 
                           if key['institution_id'] == institution_id]
        
        health_status['api_usage'] = {
            'total_keys': len(institution_apis),
            'active_keys': len([k for k in institution_apis if k['active']]),
            'total_requests_today': sum(k['usage_count'] for k in institution_apis)
        }
        
        # Check recent directory syncs
        recent_syncs = [sync for sync in self.directory_sync.values() 
                       if sync['institution_id'] == institution_id]
        
        if recent_syncs:
            latest_sync = max(recent_syncs, key=lambda x: x['started_at'])
            health_status['directory_sync'] = {
                'last_sync': latest_sync['started_at'],
                'status': latest_sync['status'],
                'users_processed': latest_sync['users_processed']
            }
        
        # Check LRS activity
        institution_records = [record for record in self.lrs_records.values() 
                              if 'neuropulse.com' in record.get('object', {}).get('id', '')]
        
        health_status['lrs_status'] = {
            'total_statements': len(institution_records),
            'statements_today': len([r for r in institution_records 
                                   if r['timestamp'][:10] == datetime.now().strftime('%Y-%m-%d')])
        }
        
        return health_status

# Initialize global enterprise integration manager
enterprise_manager = EnterpriseIntegrationManager()