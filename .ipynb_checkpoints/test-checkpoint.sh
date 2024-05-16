RANDOM_NAME=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 10 | head -n 1)
echo $RANDOM_NAME

RANDOM_NAME=$(openssl rand -base64 12 | tr -dc 'a-z0-9' | fold -w 10 | head -n 1)

echo $RANDOM_NAME