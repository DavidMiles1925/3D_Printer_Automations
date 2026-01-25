#!/bin/bash

TOPIC="pikachupoweroutage1925"
HOSTNAME=$(hostname)
EVENT="$NOTIFYTYPE"
UPS_NAME="apcups"
UPSCMD="/usr/bin/upsc"
LOGFILE="/var/log/ups-notify.log"

get_runtime() {
    runtime=$($UPSCMD $UPS_NAME battery.runtime 2>/dev/null)
    if [[ -n "$runtime" ]]; then
        minutes=$((runtime / 60))
        echo " (~${minutes} min remaining)"
    else
        echo ""
    fi
}

send_ntfy() {
    local PRIORITY="$1"
    local MESSAGE="$2"

    /usr/local/bin/ntfy publish \
        --priority "$PRIORITY" \
        "$TOPIC" \
        "$MESSAGE"
}

# Log raw event info for debugging
{
    echo "----- $(date) -----"
    echo "EVENT=$EVENT"
    echo
} >> "$LOGFILE"

case "$EVENT" in
    ONBATT)
        send_ntfy 5 "⚠️ Power outage detected on $HOSTNAME. UPS is running on battery. $(get_runtime)"
        ;;
    ONLINE)
        send_ntfy 3 "✅ Power restored on $HOSTNAME. UPS is back on line power."
        ;;
    LOWBATT)
        send_ntfy 2 "🚨 LOW BATTERY on $HOSTNAME! This may also be cause by H2S starting up. $(get_runtime)"
        ;;
    SHUTDOWN)
        send_ntfy 4 "🛑 UPS has initiated system shutdown on $HOSTNAME."
        ;;
    *)
        send_ntfy 5 "ℹ️ Unhandled UPS event '$EVENT' on $HOSTNAME (NOTIFYTYPE=$NOTIFYTYPE)"
        ;;
esac

exit 0
