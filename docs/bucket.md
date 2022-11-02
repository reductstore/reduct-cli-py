# Bucket Commands

If you set an [alias](./aliases.md) for your server, you can manage its buckets by using `bucket` subcommand:

```shell
rcli bucket --help
```

## Browsing buckets

You can check a list of existing buckets on the server:

```shell
rcli bucket ls test-storage
```

Or you can print a table with buckets and its information:

```shell
rcli bucket ls --full test-storage
```

To show information about a certain bucket use the `show` subcommand with path `ALIAS/BUCKET_NAME`:

```shell
rcli bucket show test-storage/bucket-1
```

You can also get the bucket's settings and entry list with flag `--full`:

```shell
rcli bucket show --full test-storage/bucket-1
```

## Creating a bucket

To create a bucket you should use command create and provide path to the new bucket `ALIAS/BUCKET_NAME`:

```shell
rcli bucket create test-storage/bucket-1
```

This command creates a bucket with default settings, you can specify them:

```shell
rcli bucket create --quota-type FIFO --quota-size 20Gb test-storage/bucket-1
```

## Updating settings

It's also possible to update settings of an existing bucket with command `update`:

```shell
rcli bucket update --quota-size 100Gb test-storage/bucket-1
```

Check the full list of the settings:

```shell
rcli bucket update --help
```
