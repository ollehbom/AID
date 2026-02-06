"""
Dev Service - GitHub App Backend

A Flask-based service that receives webhooks from the pipeline and manages
iterative development in dedicated workspaces.
"""

import os
import hmac
import hashlib
import json
import logging
from pathlib import Path
from flask import Flask, request, jsonify
from github import Github, GithubIntegration
from dev_agent import DevAgent
from build_manager import BuildManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
APP_ID = os.getenv('GITHUB_APP_ID')
PRIVATE_KEY_PATH = os.getenv('GITHUB_APP_PRIVATE_KEY_PATH')
WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')
WORKSPACE_DIR = Path(os.getenv('WORKSPACE_DIR', '/var/dev-workspaces'))
REPO_OWNER = os.getenv('GITHUB_REPO_OWNER')
REPO_NAME = os.getenv('GITHUB_REPO_NAME')

# Initialize GitHub App (only if credentials are provided)
integration = None
if APP_ID and PRIVATE_KEY_PATH and Path(PRIVATE_KEY_PATH).exists():
    with open(PRIVATE_KEY_PATH, 'r') as f:
        private_key = f.read()
    integration = GithubIntegration(APP_ID, private_key)
    logger.info("GitHub App integration initialized")
else:
    logger.warning("GitHub App credentials not configured - running in test mode")
    logger.warning("Set GITHUB_APP_ID and GITHUB_APP_PRIVATE_KEY_PATH to enable GitHub integration")


def verify_webhook_signature(payload_body, signature_header):
    """Verify that the webhook came from GitHub."""
    if not signature_header:
        return False
    
    hash_object = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)


def get_installation_client(installation_id):
    """Get authenticated GitHub client for installation."""
    if not integration:
        raise Exception("GitHub App integration not configured")
    auth = integration.get_access_token(installation_id)
    return Github(auth.token)


def update_commit_status(client, feature_id, state, description):
    """Update GitHub commit status for the feature branch."""
    repo = client.get_repo(f"{REPO_OWNER}/{REPO_NAME}")
    branch = repo.get_branch(f"feature/{feature_id}")
    commit = branch.commit
    
    repo.get_commit(commit.sha).create_status(
        state=state,  # pending, success, failure, error
        description=description,
        context="dev-service/build"
    )
    logger.info(f"Updated status for {feature_id}: {state} - {description}")


def process_dev_stage(feature_id, branch_name, installation_id):
    """Process a dev stage request."""
    logger.info(f"Processing dev stage for feature: {feature_id}")
    
    # Get authenticated client
    client = get_installation_client(installation_id)
    
    # Update status to pending
    update_commit_status(
        client, feature_id, "pending",
        "Dev service starting iterative development..."
    )
    
    try:
        # Create workspace for this feature
        workspace = WORKSPACE_DIR / feature_id
        workspace.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Workspace: {workspace}")
        
        # Clone or pull the feature branch
        repo_url = f"https://x-access-token:{client.get_repo(f'{REPO_OWNER}/{REPO_NAME}').clone_url.split('//')[1]}@github.com/{REPO_OWNER}/{REPO_NAME}.git"
        
        if (workspace / ".git").exists():
            logger.info("Pulling latest changes...")
            os.system(f"cd {workspace} && git pull origin {branch_name}")
        else:
            logger.info(f"Cloning repository...")
            os.system(f"git clone -b {branch_name} {repo_url} {workspace}")
        
        # Initialize dev agent
        dev_agent = DevAgent(workspace, feature_id)
        
        # Initialize build manager
        build_manager = BuildManager(workspace)
        
        # Read design artifacts
        logger.info("Reading design artifacts...")
        design_spec = (workspace / ".ai" / "pipeline" / f"{feature_id}.design.json")
        arch_spec = (workspace / ".ai" / "pipeline" / f"{feature_id}.architecture.json")
        
        if not design_spec.exists():
            raise Exception(f"Design spec not found: {design_spec}")
        
        # Generate initial implementation
        logger.info("Generating initial implementation...")
        update_commit_status(
            client, feature_id, "pending",
            "Generating code from specifications..."
        )
        
        dev_agent.generate_implementation(design_spec, arch_spec)
        
        # Iterative build loop
        max_attempts = int(os.getenv('MAX_BUILD_ATTEMPTS', '5'))
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            logger.info(f"Build attempt {attempt}/{max_attempts}")
            
            update_commit_status(
                client, feature_id, "pending",
                f"Building... (attempt {attempt}/{max_attempts})"
            )
            
            # Detect and install dependencies
            build_manager.install_dependencies()
            
            # Run build
            build_result = build_manager.build()
            
            if build_result['success']:
                logger.info("Build successful!")
                break
            
            logger.warning(f"Build failed: {build_result['error']}")
            
            # Analyze and fix build error
            update_commit_status(
                client, feature_id, "pending",
                f"Fixing build error (attempt {attempt}/{max_attempts})..."
            )
            
            fix_result = dev_agent.fix_build_error(build_result['error'])
            
            if not fix_result['success']:
                raise Exception(f"Could not fix build error: {build_result['error']}")
        
        if attempt >= max_attempts:
            raise Exception(f"Build failed after {max_attempts} attempts")
        
        # Run tests
        logger.info("Running tests...")
        update_commit_status(
            client, feature_id, "pending",
            "Running tests..."
        )
        
        max_test_attempts = int(os.getenv('MAX_TEST_ATTEMPTS', '3'))
        test_attempt = 0
        
        while test_attempt < max_test_attempts:
            test_attempt += 1
            logger.info(f"Test attempt {test_attempt}/{max_test_attempts}")
            
            test_result = build_manager.run_tests()
            
            if test_result['success']:
                logger.info("All tests passed!")
                break
            
            logger.warning(f"Tests failed: {test_result['error']}")
            
            # Fix test failures
            update_commit_status(
                client, feature_id, "pending",
                f"Fixing test failures (attempt {test_attempt}/{max_test_attempts})..."
            )
            
            fix_result = dev_agent.fix_test_failures(test_result['error'])
            
            if not fix_result['success']:
                logger.warning(f"Could not fix test failures automatically")
                break
        
        # Commit and push changes
        logger.info("Committing changes...")
        os.system(f"""
            cd {workspace} &&
            git config user.name "Dev Service Bot" &&
            git config user.email "dev-service@aid.local" &&
            git add -A &&
            git commit -m "🤖 Dev Service: Feature {feature_id} implementation

Generated and validated implementation:
- Build: ✓ Passing
- Tests: {'✓ Passing' if test_result.get('success') else '⚠ Check manually'}

This commit was automatically generated by the Dev Service." &&
            git push origin {branch_name}
        """)
        
        # Update status to success
        update_commit_status(
            client, feature_id, "success",
            "Implementation complete - build passing"
        )
        
        logger.info(f"✅ Feature {feature_id} completed successfully")
        
        return {
            'success': True,
            'feature_id': feature_id,
            'build_attempts': attempt,
            'test_attempts': test_attempt
        }
        
    except Exception as e:
        logger.error(f"❌ Dev stage failed: {e}", exc_info=True)
        
        # Update status to failure
        update_commit_status(
            client, feature_id, "failure",
            f"Development failed: {str(e)[:100]}"
        )
        
        return {
            'success': False,
            'feature_id': feature_id,
            'error': str(e)
        }


@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle webhook from GitHub (for future use)."""
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256')
    if WEBHOOK_SECRET and not verify_webhook_signature(request.data, signature):
        logger.warning("Invalid webhook signature")
        return jsonify({'error': 'Invalid signature'}), 401
    
    payload = request.json
    event_type = request.headers.get('X-GitHub-Event')
    
    logger.info(f"Received webhook: {event_type}")
    
    return jsonify({'status': 'ignored'}), 200


@app.route('/dev-request', methods=['POST'])
def dev_request():
    """Handle direct dev request from pipeline."""
    # Verify authorization token
    auth_header = request.headers.get('Authorization')
    expected_token = os.getenv('DEV_SERVICE_TOKEN')
    
    if expected_token and auth_header != f"Bearer {expected_token}":
        logger.warning("Invalid authorization token")
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Parse request
    data = request.json
    feature_id = data.get('feature_id')
    branch_name = data.get('branch')
    repository = data.get('repository')
    
    if not all([feature_id, branch_name]):
        return jsonify({'error': 'Missing required parameters'}), 400
    
    logger.info(f"Received dev request for feature: {feature_id}")
    
    # Get installation ID from repository (requires GitHub App setup)
    # For now, process without GitHub integration
    installation_id = None
    
    # Process in background
    import threading
    thread = threading.Thread(
        target=process_dev_stage,
        args=(feature_id, branch_name, installation_id)
    )
    thread.start()
    
    return jsonify({
        'status': 'accepted',
        'feature_id': feature_id,
        'message': 'Development started'
    }), 202


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'workspace_dir': str(WORKSPACE_DIR),
        'active_workspaces': len(list(WORKSPACE_DIR.glob('*'))) if WORKSPACE_DIR.exists() else 0
    })


@app.route('/status/<feature_id>', methods=['GET'])
def status(feature_id):
    """Get status of a feature development."""
    workspace = WORKSPACE_DIR / feature_id
    
    if not workspace.exists():
        return jsonify({'error': 'Feature not found'}), 404
    
    return jsonify({
        'feature_id': feature_id,
        'workspace': str(workspace),
        'exists': workspace.exists()
    })


if __name__ == '__main__':
    port = int(os.getenv('DEV_SERVICE_PORT', '8080'))
    app.run(host='0.0.0.0', port=port)
