#!/usr/bin/env python3
"""
MS-Oferta Performance Tester - Main Entry Point
Run this file to start the web dashboard
"""
import sys
import os

# Add app directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app.app import run_server

if __name__ == '__main__':
    run_server()
