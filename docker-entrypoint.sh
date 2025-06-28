#!/bin/sh
set -e

# Run database migrations
alembic upgrade head

# Execute the main container command passed as arguments
exec "$@" 