# This project contains the code and configuration for a simple
# Model Context Protocol (MCP) server using FastMCP.
#
# File Structure:
# ├── mcp_joke_server.py  # The main Python application using FastMCP.
# ├── requirements.txt    # Python dependencies.
# ├── Dockerfile          # Dockerfile to containerize the application.
# └── k8s-deployment.yaml # Kubernetes manifests for Deployment and Service.
#
# How to Run:
#
# 1. Local Development:
#    - pip install -r requirements.txt
#    - uvicorn mcp_joke_server:app --host 0.0.0.0 --port 8000
#    - Access the docs at http://localhost:8000/docs
#    - Access the MCP endpoint at http://localhost:8000/mcp/v1alpha1/models/joke-context
#
# 2. Docker Build:
#    - docker build -t mcp-joke-server .
#
# 3. Kubernetes Deployment:
#    - (Ensure your Docker image is pushed to a registry accessible by your cluster)
#    - (Update the image name in k8s-deployment.yaml)
#    - kubectl apply -f k8s-deployment.yaml
#    - kubectl get service mcp-joke-service # Find the external IP

# ----------------------------------------------------------------------
# mcp_joke_server.py
# ----------------------------------------------------------------------
