# Reduct CLI

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/reduct-storage/reduct-cli)](https://pypi.org/project/reduct-cli)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/reduct-cli)](https://pypi.org/project/reduct-cli)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/reduct-storage/reduct-cli/ci)](https://github.com/reduct-storage/reduct-cli/actions)

The Reduct CLI is a command line client for [Reduct Storage](https://reduct-storage.dev), a self-hosted, open-source,
time-series blob storage.

## Features

* Support for Reduct Storage API v1.1
* Easy management of buckets and tokens
* Ability to check the status of a storage engine
* Aliases for storing server credentials
* Data mirroring between buckets

## Requirements

* Python >= 3.8
* pip

## Installing

To install the Reduct CLI, simply use pip:

```
pip install reduct-cli
```

## Usage

Check with our [demo server](https://play.reduct-storage.dev):

```shell
rcli alias add -L  https://play.reduct-storage.dev -t reduct play
rcli server status play
rcli bucket ls --full play
```

## Links

* [Project Homepage](https://reduct-storage.dev)
* [Documentation](https://reduct-cli.readthedocs.io/)
* [Reduct Client SDK for Python](https://github.com/reduct-storage/reduct-py)
* [Reduct Storage](https://github.com/reduct-storage/reduct-storage)
