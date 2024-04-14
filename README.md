# ReductStore CLI

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/reduct-storage/reduct-cli)](https://pypi.org/project/reduct-cli)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/reduct-cli)](https://pypi.org/project/reduct-cli)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/reductstore/reduct-cli/ci.yml?branch=main)](https://github.com/reductstore/reduct-cli/actions)

The ReductStore CLI is a command line client for [ReductStore](https://www.reduct.store), a time series database for
blob data. It is written in Python and uses the [ReductStore Client SDK for Python](https://py.reduct.store/).

**DEPRECATED**:

We don't maintain this repository anymore, consider using the Rust version of the CLI: https://github.com/reductstore/reduct-cli

## Features

* Support for ReductStore API v1.8
* Easy management of buckets, tokens and replications
* Ability to check the status of a storage engine
* Aliases for storing server credentials
* Export and mirror data

## Requirements

* Python >= 3.9
* pip

## Installing

To install the ReductStore CLI, simply use pip:

```
pip install reduct-cli
```

## Usage

Check with our [demo server](https://play.reduct.store):

```shell
rcli alias add -L  https://play.reduct.store -t reduct play
rcli server status play
rcli bucket ls --full play
rcli export folder play/data . --inlcude size=big
```

## Links

* [Project Homepage](https://www.reduct.store)
* [Documentation](https://cli.reduct.store)
* [ReductStore Client SDK for Python](https://github.com/reductstore/reduct-py)
* [ReductStore](https://github.com/reductstore/reductstore)
