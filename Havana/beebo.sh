#!/bin/bash
# Beebo — floating AI chat alongside Ruffle
# Starts a tiny local server and opens Beebo as a standalone app window

DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=19432

# Kill any previous instance on that port
lsof -ti tcp:$PORT | xargs kill -9 2>/dev/null

# Start minimal HTTP server
cd "$DIR"
python3 -m http.server $PORT --bind 127.0.0.1 > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server to be ready
sleep 0.6

URL="http://127.0.0.1:$PORT/beebo.html"

# Try Chrome first (best app-mode support)
if open -Ra "Google Chrome" 2>/dev/null; then
  open -a "Google Chrome" --args \
    --app="$URL" \
    --window-size=360,620 \
    --window-position=30,80 \
    --no-first-run \
    --disable-extensions \
    --disable-infobars
elif open -Ra "Chromium" 2>/dev/null; then
  open -a "Chromium" --args \
    --app="$URL" \
    --window-size=360,620 \
    --window-position=30,80
else
  # Fallback: open in default browser
  open "$URL"
fi

echo "Beebo running at $URL (PID: $SERVER_PID)"
echo "Press Ctrl+C to stop."

# Keep alive — kill server on exit
trap "kill $SERVER_PID 2>/dev/null; echo 'Beebo stopped.'" EXIT INT TERM
wait $SERVER_PID
