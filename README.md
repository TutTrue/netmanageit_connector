# OpenCTI NetManageIT Connector

This connector imports observables and indicators from an OpenCTI NetManageIT instance into another OpenCTI platform. It fetches all observables first, then indicators, and creates relationships between them based on their standard_id references.

## Features

- Fetches observables from OpenCTI NetManageIT GraphQL API
- Fetches indicators with their associated observables
- Creates STIX 2.1 objects for all data types (IPv4, IPv6, Domain, URL, Email, MAC, AS, Process, User Account)
- Establishes relationships between indicators and observables using standard_id
- Supports batch processing for efficient data transfer
- Preserves metadata including labels, markings, and external references

Table of Contents

- [OpenCTI External Ingestion Connector Template](#opencti-external-ingestion-connector-template)
  - [Introduction](#introduction)
  - [Installation](#installation)
    - [Requirements](#requirements)
  - [Configuration variables](#configuration-variables)
    - [OpenCTI environment variables](#opencti-environment-variables)
    - [Base connector environment variables](#base-connector-environment-variables)
    - [Connector extra parameters environment variables](#connector-extra-parameters-environment-variables)
  - [Deployment](#deployment)
    - [Docker Deployment](#docker-deployment)
      - [Using Pre-built Image from GitHub Container Registry](#using-pre-built-image-from-github-container-registry)
      - [Building Your Own Image](#building-your-own-image)
      - [GitHub Actions CI/CD Setup](#github-actions-cicd-setup)
    - [Manual Deployment](#manual-deployment)
  - [Usage](#usage)
  - [Behavior](#behavior)
  - [Debugging](#debugging)
  - [Additional information](#additional-information)

## Introduction

## Installation

### Requirements

- OpenCTI Platform >= 6...

## Configuration variables

There are a number of configuration options, which are set either in `docker-compose.yml` (for Docker) or
in `config.yml` (for manual deployment).

### OpenCTI environment variables

Below are the parameters you'll need to set for OpenCTI:

| Parameter     | config.yml | Docker environment variable | Mandatory | Description                                          |
|---------------|------------|-----------------------------|-----------|------------------------------------------------------|
| OpenCTI URL   | url        | `OPENCTI_URL`               | Yes       | The URL of the OpenCTI platform.                     |
| OpenCTI Token | token      | `OPENCTI_TOKEN`             | Yes       | The default admin token set in the OpenCTI platform. |

### Base connector environment variables

Below are the parameters you'll need to set for running the connector properly:

| Parameter       | config.yml | Docker environment variable | Default         | Mandatory | Description                                                                              |
|-----------------|------------|-----------------------------|-----------------|-----------|------------------------------------------------------------------------------------------|
| Connector ID    | id         | `CONNECTOR_ID`              | /               | Yes       | A unique `UUIDv4` identifier for this connector instance.                                |
| Connector Type  | type       | `CONNECTOR_TYPE`            | EXTERNAL_IMPORT | Yes       | Should always be set to `EXTERNAL_IMPORT` for this connector.                            |
| Connector Name  | name       | `CONNECTOR_NAME`            |                 | Yes       | Name of the connector.                                                                   |
| Connector Scope | scope      | `CONNECTOR_SCOPE`           |                 | Yes       | The scope or type of data the connector is importing, either a MIME type or Stix Object. |
| Log Level       | log_level  | `CONNECTOR_LOG_LEVEL`       | info            | Yes       | Determines the verbosity of the logs. Options are `debug`, `info`, `warn`, or `error`.   |

### Connector extra parameters environment variables

Below are the parameters you'll need to set for the OpenCTI NetManageIT connector:

| Parameter                    | config.yml              | Docker environment variable    | Default | Mandatory | Description                                                                 |
|------------------------------|-------------------------|--------------------------------|---------|-----------|-----------------------------------------------------------------------------|
| OpenCTI NetManageIT URL      | url                     | `OPENCTI_NETMANAGEIT_URL`      |         | Yes       | The URL of the source OpenCTI NetManageIT instance (e.g., https://opencti.netmanageit.com) |
| OpenCTI NetManageIT Token    | token                   | `OPENCTI_NETMANAGEIT_TOKEN`    |         | Yes       | The API token for accessing the source OpenCTI NetManageIT instance        |

## Deployment

### Docker Deployment

#### Using Pre-built Image from GitHub Container Registry

The easiest way to deploy this connector is using the pre-built image from GitHub Container Registry:

```shell
# Pull the latest image
docker pull ghcr.io/yourusername/netmanageit-connector:latest

# Run with docker-compose
GITHUB_REPOSITORY_OWNER=yourusername docker-compose up -d
```

#### Building Your Own Image

If you need to build the image yourself:

```shell
# Build the image locally
docker build . -t ghcr.io/yourusername/netmanageit-connector:latest

# Push to your GitHub Container Registry (optional)
docker push ghcr.io/yourusername/netmanageit-connector:latest
```

#### GitHub Actions CI/CD Setup

This repository includes automated Docker image building and publishing to GitHub Container Registry via GitHub Actions.

**Required GitHub Secrets:**

The workflow automatically uses the built-in `GITHUB_TOKEN` secret, so no additional secrets are required! The workflow will:

- Automatically authenticate using your repository's GitHub token
- Push images to `ghcr.io/yourusername/netmanageit-connector`
- Use your GitHub username and repository name automatically

**Note:** Make sure your repository has the "Packages" feature enabled in Settings → General → Features.

**Automated Builds:**

The GitHub Actions workflow will automatically:
- Build multi-platform images (AMD64 and ARM64)
- Push images to GitHub Container Registry on every push to `main` branch
- Create versioned tags when you create Git tags (e.g., `v1.0.0`)
- Use Docker layer caching for faster builds

**Manual Trigger:**

You can also manually trigger the build process:
1. Go to your repository → Actions → "Build and Push to GitHub Container Registry"
2. Click "Run workflow" → "Run workflow"

Make sure to replace the environment variables in `docker-compose.yml` with the appropriate configurations for your
environment. Then, start the docker container with the provided docker-compose.yml

```shell
# Set your GitHub username and start the container
GITHUB_REPOSITORY_OWNER=yourusername docker-compose up -d
```

### Manual Deployment

Create a file `config.yml` based on the provided `config.yml.sample`.

Replace the configuration variables (especially the "**ChangeMe**" variables) with the appropriate configurations for
you environment.

Install the required python dependencies (preferably in a virtual environment):

```shell
pip3 install -r requirements.txt
```

Then, start the connector from recorded-future/src:

```shell
python3 main.py
```

## Usage

After Installation, the connector should require minimal interaction to use, and should update automatically at a regular interval specified in your `docker-compose.yml` or `config.yml` in `duration_period`.

However, if you would like to force an immediate download of a new batch of entities, navigate to:

`Data management` -> `Ingestion` -> `Connectors` in the OpenCTI platform.

Find the connector, and click on the refresh button to reset the connector's state and force a new
download of data by re-running the connector.

## Behavior

The connector operates in two phases:

1. **Observable Import Phase**: 
   - Fetches all observables from the source OpenCTI NetManageIT instance
   - Converts them to STIX 2.1 objects preserving all metadata
   - Creates a mapping of standard_id to observable ID for relationship creation
   - Sends observables in batches of 100

2. **Indicator Import Phase**:
   - Fetches all indicators from the source OpenCTI NetManageIT instance
   - Converts them to STIX 2.1 indicators with all metadata
   - Creates relationships between indicators and their associated observables using standard_id
   - Sends indicators and relationships in batches of 100

**Important Considerations**:
- The connector uses standard_id as the primary identifier for creating relationships
- All metadata (labels, markings, external references) is preserved during import
- The connector processes data in batches to handle large datasets efficiently
- Relationships are only created if the observable standard_id exists in the mapping


## Debugging

The connector can be debugged by setting the appropiate log level.
Note that logging messages can be added using `self.helper.connector_logger,{LOG_LEVEL}("Sample message")`, i.
e., `self.helper.connector_logger.error("An error message")`.

<!-- Any additional information to help future users debug and report detailed issues concerning this connector -->

## Additional information

**Data Types Supported**:
- IPv4 Address
- IPv6 Address  
- Domain Name
- URL
- Email Address
- MAC Address
- Autonomous System
- Process
- User Account

**Metadata Preserved**:
- Labels and their colors
- Object markings (TLP, etc.)
- External references
- Creation and modification timestamps
- OpenCTI scores and descriptions
- Creator information

**Performance Notes**:
- The connector fetches data in batches of 1000 from the source
- Sends data in batches of 100 to the destination
- Includes cooldown periods to avoid overwhelming the source API
- Uses pagination to handle large datasets efficiently

**Security Considerations**:
- Ensure proper authentication tokens are configured
- Consider network security between source and destination instances
- Review data sensitivity and marking levels before import
