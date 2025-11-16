#!/bin/bash
#
# Cron Job Setup for Pain Point Discovery Engine
#
# This script sets up a daily cron job to run all collectors.
#

PROJECT_DIR="/home/kwaldman/pain-point-discovery-engine"
VENV_DIR="$PROJECT_DIR/venv"
SCRIPT="$PROJECT_DIR/scripts/collect_all.py"
LOG_DIR="$PROJECT_DIR/logs"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Cron job entry (runs at 2 AM daily)
CRON_JOB="0 2 * * * cd $PROJECT_DIR && source $VENV_DIR/bin/activate && python3 $SCRIPT >> $LOG_DIR/collection.log 2>&1"

echo "============================================================"
echo "PAIN POINT DISCOVERY ENGINE - Cron Job Setup"
echo "============================================================"
echo ""
echo "This will add a daily cron job that:"
echo "  - Runs at 2:00 AM every day"
echo "  - Collects pain points from all sources"
echo "  - Logs output to: $LOG_DIR/collection.log"
echo ""
echo "Cron job command:"
echo "$CRON_JOB"
echo ""
echo "============================================================"
echo ""

# Ask for confirmation
read -p "Add this cron job? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]
then
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

    echo "✅ Cron job added successfully!"
    echo ""
    echo "To view your crontab:"
    echo "  crontab -l"
    echo ""
    echo "To edit your crontab:"
    echo "  crontab -e"
    echo ""
    echo "To remove this cron job:"
    echo "  crontab -e"
    echo "  (then delete the line)"
    echo ""
    echo "To view logs:"
    echo "  tail -f $LOG_DIR/collection.log"
else
    echo "❌ Cron job not added."
    echo ""
    echo "To add manually, run:"
    echo "  crontab -e"
    echo ""
    echo "Then add this line:"
    echo "$CRON_JOB"
fi

echo "============================================================"
