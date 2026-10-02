set -euo pipefail
cd "$(dirname "$0")"
compose() { docker compose -f docker-compose.prod.yml "$@"; }

dump=$(mktemp)
trap 'rm -f "$dump"' EXIT

# Dump to a file first so a failed pg_dump never uploads a truncated backup.
compose exec -T postgres sh -c 'pg_dump -U "$POSTGRES_USER" -Fc "$POSTGRES_DB"' >"$dump"

compose exec -T app python -c "
import datetime, os, sys, boto3
boto3.client(
    's3',
    endpoint_url=f\"https://{os.environ['CLOUDFLARE_ACCOUNT_ID']}.r2.cloudflarestorage.com\",
    aws_access_key_id=os.environ['BACKUP_R2_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['BACKUP_R2_SECRET_ACCESS_KEY'],
    region_name='auto',
).upload_fileobj(sys.stdin.buffer, os.environ['BACKUP_R2_BUCKET'], f'postgres/{datetime.datetime.now(datetime.UTC):%Y-%m-%dT%H%M}.dump')
" <"$dump"
