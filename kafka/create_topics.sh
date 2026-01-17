
#!/usr/bin/env bash
set -euo pipefail
kafka-topics.sh --bootstrap-server localhost:9092 --create --topic crypto.ticks --if-not-exists --partitions 3 --replication-factor 1
