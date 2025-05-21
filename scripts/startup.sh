# scripts/startup.sh
#!/bin/bash
# Startup script for the LiveKit Call Agent

# Load environment variables from .env file
set -a
source .env
set +a

# Check for required environment variables
required_vars=("LIVEKIT_URL" "LIVEKIT_API_KEY" "LIVEKIT_API_SECRET" "SIP_OUTBOUND_TRUNK_ID" "DEEPGRAM_API_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    missing_vars+=("$var")
  fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
  echo "Error: Missing required environment variables: ${missing_vars[*]}"
  echo "Please add them to your .env file or export them before running this script."
  exit 1
fi

# Start the application
echo "Starting LiveKit Call Agent..."
python main.py