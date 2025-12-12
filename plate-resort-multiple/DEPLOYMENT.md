# Deployment Notes

## Quick Pi Setup

1. **Clone and Install:**
   ```bash
   git clone https://github.com/AccelerationConsortium/plate-RESORT.git
   cd plate-RESORT/plate-resort-multiple
   python3 -m venv plate-resort-env
   source plate-resort-env/bin/activate
   pip install -e .
   ```

2. **Generate API Key:**
   ```bash
   plate-resort-keygen --generate --update-config --create-env
   export PLATE_API_KEY=$(grep PLATE_API_KEY .env | cut -d'=' -f2)
   ```

3. **Start Services:**
   ```bash
   # REST API Server
   plate-resort-rest-server
   
   # OR Prefect Worker
   plate-resort-prefect-worker
   ```

4. **REST API Client Usage:**
   ```bash
   # Available commands: connect, disconnect, status, position, activate
   plate-resort-rest-client connect
   plate-resort-rest-client status
   plate-resort-rest-client position
   plate-resort-rest-client activate A
   plate-resort-rest-client disconnect
   ```

## Auto-activation Setup
```bash
echo "cd ~/plate-RESORT/plate-resort-multiple && source plate-resort-env/bin/activate" >> ~/.bashrc
```

## Fixed Issues
- ✅ File corruption in cli_rest.py and keygen_rest.py 
- ✅ API key configuration for REST server
- ✅ Environment variable precedence in wrapper.py
- ✅ Console script naming and paths
- ✅ Dual interface architecture (REST + Prefect)