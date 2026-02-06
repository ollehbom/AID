"""
Build Manager - Detects project type and manages build/test execution
"""

import os
import json
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class BuildManager:
    """Manages build and test execution for different project types."""
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.project_type = self._detect_project_type()
        self.build_commands = self._load_build_commands()
    
    def _detect_project_type(self) -> str:
        """Detect the project type based on files present."""
        if (self.workspace / "package.json").exists():
            return "node"
        elif (self.workspace / "requirements.txt").exists():
            return "python"
        elif (self.workspace / "go.mod").exists():
            return "go"
        elif (self.workspace / "Cargo.toml").exists():
            return "rust"
        elif (self.workspace / "pom.xml").exists():
            return "java-maven"
        elif (self.workspace / "build.gradle").exists():
            return "java-gradle"
        else:
            return "unknown"
    
    def _load_build_commands(self) -> dict:
        """Load build commands from .build.json or use defaults."""
        build_file = self.workspace / ".ai" / "pipeline" / "*.build.json"
        build_files = list((self.workspace / ".ai" / "pipeline").glob("*.build.json"))
        
        if build_files:
            with open(build_files[0]) as f:
                return json.load(f)
        
        # Default commands based on project type
        defaults = {
            "node": {
                "install": "npm install",
                "build": "npm run build",
                "test": "npm test",
                "dev": "npm run dev",
                "working_dir": "./"
            },
            "python": {
                "install": "pip install -r requirements.txt",
                "build": "python -m py_compile $(find . -name '*.py')",
                "test": "pytest",
                "dev": "python main.py",
                "working_dir": "./"
            },
            "go": {
                "install": "go mod download",
                "build": "go build ./...",
                "test": "go test ./...",
                "dev": "go run .",
                "working_dir": "./"
            },
            "rust": {
                "install": "cargo fetch",
                "build": "cargo build",
                "test": "cargo test",
                "dev": "cargo run",
                "working_dir": "./"
            }
        }
        
        return defaults.get(self.project_type, {})
    
    def _run_command(self, command: str, working_dir: str = None) -> dict:
        """Run a shell command and capture output."""
        if not command:
            return {'success': True, 'output': 'No command specified'}
        
        work_dir = self.workspace / (working_dir or self.build_commands.get('working_dir', './'))
        
        logger.info(f"Running: {command} in {work_dir}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            output = result.stdout + result.stderr
            
            if result.returncode == 0:
                logger.info(f"Command succeeded")
                return {
                    'success': True,
                    'output': output,
                    'exit_code': result.returncode
                }
            else:
                logger.warning(f"Command failed with exit code {result.returncode}")
                return {
                    'success': False,
                    'error': output,
                    'exit_code': result.returncode
                }
        
        except subprocess.TimeoutExpired:
            logger.error("Command timed out")
            return {
                'success': False,
                'error': 'Command timed out after 5 minutes'
            }
        
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def install_dependencies(self) -> dict:
        """Install project dependencies."""
        logger.info(f"Installing dependencies for {self.project_type} project...")
        command = self.build_commands.get('install', '')
        
        if not command:
            logger.info("No install command specified, skipping")
            return {'success': True}
        
        return self._run_command(command)
    
    def build(self) -> dict:
        """Build the project."""
        logger.info("Building project...")
        command = self.build_commands.get('build', '')
        
        if not command:
            logger.warning("No build command specified")
            return {'success': True, 'output': 'No build command'}
        
        return self._run_command(command)
    
    def run_tests(self) -> dict:
        """Run project tests."""
        logger.info("Running tests...")
        command = self.build_commands.get('test', '')
        
        if not command:
            logger.warning("No test command specified")
            return {'success': True, 'output': 'No tests configured'}
        
        return self._run_command(command)
    
    def get_package_manager(self) -> str:
        """Detect the package manager being used."""
        if self.project_type == "node":
            if (self.workspace / "package-lock.json").exists():
                return "npm"
            elif (self.workspace / "yarn.lock").exists():
                return "yarn"
            elif (self.workspace / "pnpm-lock.yaml").exists():
                return "pnpm"
            else:
                return "npm"
        
        return self.project_type
    
    def analyze_error(self, error_output: str) -> dict:
        """Analyze error output to extract useful information."""
        analysis = {
            'error_type': 'unknown',
            'missing_dependencies': [],
            'syntax_errors': [],
            'type_errors': [],
            'suggestions': []
        }
        
        # Detect missing dependencies
        if "Cannot find module" in error_output or "Module not found" in error_output:
            analysis['error_type'] = 'missing_dependency'
            # Extract module names
            import re
            modules = re.findall(r"Cannot find module ['\"]([^'\"]+)['\"]", error_output)
            modules += re.findall(r"Module not found.*['\"]([^'\"]+)['\"]", error_output)
            analysis['missing_dependencies'] = list(set(modules))
        
        # Detect invalid package names
        if "Invalid package name" in error_output:
            analysis['error_type'] = 'invalid_package_name'
            # Extract the invalid package
            import re
            matches = re.findall(r"Invalid package name \"([^\"]+)\"", error_output)
            if matches:
                analysis['suggestions'].append(
                    f"Check if scoped package: should '{matches[0]}' be '@{matches[0]}'?"
                )
        
        # Detect TypeScript errors
        if "error TS" in error_output:
            analysis['error_type'] = 'typescript_error'
            import re
            ts_errors = re.findall(r"error (TS\d+):", error_output)
            analysis['type_errors'] = list(set(ts_errors))
        
        return analysis
