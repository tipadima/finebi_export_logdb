# FineBI logdb ElasticSearch to MySQL Exporter

## Overview
This script copies data from ElasticSearch `logdb` indices to a MySQL database.  
**Compatibility**: FineBI 6.1.1+, MySQL 5.4+

Key features:
- Automatically creates MySQL tables matching ElasticSearch indices
- Incremental sync (only transfers new records)
- Configurable batch processing

## Project Structure
.
├── docker/
│ └── Dockerfile # Container configuration
├── example/
│ └── config.json # Sample configuration
├── requirements.txt # Python dependencies
├── connect.py # ElasticSearch/MySQL connector
└── main.py # Main script

## Quick Start

### 1. Build Docker Image

```
docker build -f docker/Dockerfile -t finebi_export_logdb .
```

### 2. Prepare MySQL

Create the target database specified in your config.

### 3. Run the Exporter

Using config file:
```
docker run --rm \
  -v /path/to/config.json:/opt/app/config.json \
  finebi_export_logdb:latest
```

Using environment variables:
```
docker run --rm \
  -e elasticsearch.address='http://elasticsearch:9200' \
  -e elasticsearch.username=elastic \
  -e elasticsearch.password=elastic \
  -e mysql.address='mysql:3306' \
  -e mysql.database=logdb \
  -e mysql.username=root \
  -e mysql.password=root \
  finebi_export_logdb:latest
```

### 4. Schedule Regular Syncs (Cron)
```
# Run every minute:
*/1 * * * * /usr/bin/docker run --rm -v /opt/finebi_export_logdb/config.json:/opt/app/config.json finebi_export_logdb:latest
```

## Configuration

config.json example:
```
{
  "elasticsearch": {
    "address": "http://elasticsearch:9200",
    "username": "elastic",
    "password": "elastic"
  },
  "mysql": {
    "address": "mysql:3306",
    "database": "logdb",
    "username": "root",
    "password": "root",
    "batch_size": 1000
  },
  "log_level": "INFO"
}
```

### Configuration Options
batch_size - Records per insert batch   default: 1000
log_level - Logging level (DEBUG/INFO)  default: INFO

## How It Works

- Detects ElasticSearch indices
- Creates corresponding MySQL tables if missing
- Identifies newest record in MySQL
- Transfers all newer records from ElasticSearch
