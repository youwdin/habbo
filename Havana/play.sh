#!/bin/zsh
# Launches the Habbo Flash client in Ruffle desktop
# Usage: ./play.sh <username>

USERNAME="$1"
if [ -z "$USERNAME" ]; then
  echo "Usage: ./play.sh <your_username>"
  exit 1
fi

MYSQL="/opt/homebrew/bin/mysql"
SWF="http://localhost:8080/gordon/RELEASE39-22643-22891-200911110035_07c3a2a30713fd5bea8a8caf07e33438/Habbo.swf"
RUFFLE="/Applications/Ruffle.app/Contents/MacOS/ruffle"

# Fetch SSO ticket and figure from DB
ROW=$($MYSQL -u havana -phavana123 havana -sN -e "SELECT sso_ticket, figure, sex FROM users WHERE username='$USERNAME' LIMIT 1;")
if [ -z "$ROW" ]; then
  echo "User '$USERNAME' not found. Register at http://localhost:8080/register first."
  exit 1
fi

SSO_TICKET=$(echo "$ROW" | awk '{print $1}')
FIGURE=$(echo "$ROW" | awk '{print $2}')

if [ -z "$SSO_TICKET" ] || [ "$SSO_TICKET" = "NULL" ]; then
  echo "No SSO ticket found for '$USERNAME'. Please log in at http://localhost:8080 first, then run this script."
  exit 1
fi

echo "Launching Habbo for: $USERNAME"
echo "SSO Ticket: $SSO_TICKET"

"$RUFFLE" "$SWF" \
  -P"connection.info.host=127.0.0.1" \
  -P"connection.info.port=12323" \
  -P"sso.ticket=$SSO_TICKET" \
  -P"external.variables.txt=http://localhost:8080/flash/gamedata/external_variables.txt" \
  -P"external.texts.txt=http://localhost:8080/flash/gamedata/external_flash_texts.txt" \
  -P"client.reload.url=http://localhost:8080/client" \
  -P"client.connection.failed.url=http://localhost:8080/disconnected" \
  -P"site.url=http://localhost:8080" \
  -P"url.prefix=http://localhost:8080" \
  -P"use.sso.ticket=1"
