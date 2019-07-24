
flask_user="webcompbiomed@flask"

cat <<EOF
-- Create DB
create database compbiomed;
-- Create tables etc
EOF
cat < ../database/compbiomed.sql
cat <<EOF
-- Create an account for the webservice to connect to the database
CREATE USER $flask_user
  IDENTIFIED BY '$(cat db_web_password)';

-- Authorise the user for access to the data
GRANT SELECT, INSERT, UPDATE, DELETE
  ON compbiomed.*
  TO $flask_user;

-- Create an initial superuser acount within the web service
INSERT INTO user(first_name, last_name, email, password, active)
  VALUES("admin","admin","admin","$(cat web_admin_password)",1);
INSERT INTO role(name, description)
  VALUES("superuser","superuser");
-- set the admin role
INSERT INTO roles_users(role_id, user_id)
  VALUES(1,1);
EOF


