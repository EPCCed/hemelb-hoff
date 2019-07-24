secrets="db_root_password
db_web_password
web_admin_password
flask_secret_key
flask_security_salt"

for secret in $secrets; do
    openssl rand -base64 12 > $secret
done
