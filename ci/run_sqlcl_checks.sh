#!/usr/bin/env bash
set -euo pipefail

DB_USER="$1"
DB_PASS="$2"
DB_CONNECT="$3"
SQL_DIR="${4:-sql}"

echo "Deploying PL/SQL to target ${DB_CONNECT} from ${SQL_DIR}..."

sql "${DB_USER}/${DB_PASS}@${DB_CONNECT}" <<EOF
SET SERVEROUTPUT ON
SET FEEDBACK ON
SET ECHO ON

-- Example: run your deployment script(s) in order
@${SQL_DIR}/10_schema_changes.sql
@${SQL_DIR}/20_packages.sql
@${SQL_DIR}/30_post_deploy_checks.sql

EXIT
EOF

echo "Deployment completed successfully."
