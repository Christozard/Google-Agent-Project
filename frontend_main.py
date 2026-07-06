"""
Main entry point for running the frontend.
Run with: MOOMOO_SECURITY_FIRM=FUTUSG streamlit run frontend_main.py
"""
import sys
import os

# Add project root to path (when running from project root)
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the app (it calls main() internally)
import src.frontend.app # Trigger reload
