#!/bin/bash

LOG_FILE="/home/ankit/project/ircc_rag_agent/notebook/generate.log"
SCRIPT="/home/ankit/project/ircc_rag_agent/notebook/generate_gold.py"

echo "Starting resilient job runner..." | tee -a "$LOG_FILE"

while true; do
    echo "----------------------------------------" | tee -a "$LOG_FILE"
    echo "Running generator at $(date)..." | tee -a "$LOG_FILE"
    
    # Run the script
    /usr/bin/python3 "$SCRIPT" >> "$LOG_FILE" 2>&1
    
    # Capture exit code
    EXIT_CODE=$?
    
    # If exit code is 0 (Success), we are done.
    if [ $EXIT_CODE -eq 0 ]; then
        echo "Job finished successfully at $(date)!" | tee -a "$LOG_FILE"
        break
    else
        echo "Job crashed with exit code $EXIT_CODE. Restarting in 10 seconds..." | tee -a "$LOG_FILE"
        sleep 10
    fi
done
