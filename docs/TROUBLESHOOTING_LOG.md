# 📋 Phase 3 Fixes & Troubleshooting Log
### Date: 2025-12-16

This document records the technical issues encountered during the Phase 3 Kubernetes Deployment and their resolutions.

## 1. Frontend Connectivity Issues
**Issue:** Frontend Dashboard showed "Offline" and Gitea/Backend unreachable.
**Cause:**
1.  **Direct API Routing:** The frontend was attempting to query `localhost:8000` directly. In Kubernetes (Docker), port 8000 is internal. Traffic must go through the Ingress Controller at port 80.
2.  **Service Type:** The Frontend Service was briefly switched to `LoadBalancer`, bypassing the Ingress Controller and causing Nginx to handle `/api` requests (returning 404/HTML instead of proxying to Backend).

**Fix:**
*   Modified `frontend/src/lib/api.js` to use a relative URL (`""`) in production, ensuring requests go to `/api/health` relative to the domain (handled by Ingress).
*   Reverted `infra/k8s/04-frontend.yaml` Service type to `ClusterIP`.
*   Enabled Minikube Ingress Addon (`minikube addons enable ingress`).

## 2. Gitea Repository Synchronization
**Issue:** User created a repo in Gitea, but it didn't show up in the Dashboard.
**Cause:**
*   The Backend functionality relies on fetching repositories for a specific list of *hardcoded* users.
*   The Gitea instance inside Kubernetes is ephemeral (mostly) or was reset, losing the user `matthew`.
*   The backend logs showed "user redirect does not exist", determining the Gitea user was missing.

**Fix:**
*   Updated `backend/routers/repositories.py` to include `matthew` and `matthew-test` in the scan list.
*   Provided specific instructions to re-register the user `matthew` in the ephemeral Gitea instance via port-forwarding.

## 3. Minikube Networking
**Issue:** `minikube tunnel` frequently failed or required sudo.
**Cause:**
*   Ingress requires binding to privileged port 80/443 on the host machine.
*   Stale tunnel processes prevented new ones from starting.

**Fix:**
*   Documented the strict requirement to run `sudo minikube tunnel` in a dedicated terminal.
*   Updated `deploy_k8s.sh` script paths to be robust against execution directory.

---
**Status:** All systems fully operational. Research experiments ready to proceed.
