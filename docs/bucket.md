# Bucket Commands

The rcli command line client allows you to manage the buckets on your storage engine using the bucket subcommand. For
example:

```shell
rcli bucket --help
```

You should set an [alias](./aliases.md) for your storage engine, so that you can use the alias in the rcli bucket
command to refer to the storage engine. For example:

```shell
rcli bucket ls test-storage
```

## Browsing Buckets

To see a list of existing buckets on your storage engine, use the `ls` subcommand of rcli bucket, like this:

```shell
rcli bucket ls test-storage
```

To see more detailed information about buckets, use the `--full` flag:

```shell
rcli bucket ls --full test-storage
```

To show detailed information about a specific bucket, use the `show` subcommand with the path to the bucket in the form
`ALIAS/BUCKET_NAME, like this:

```shell
rcli bucket show test-storage/bucket-1
```

You can also use the `--full` flag to show the bucket's settings and entry list:

```shell
rcli bucket show --full test-storage/bucket-1
```

## Creating a Bucket

To create a new bucket on your storage engine, use the `create` subcommand of `rcli bucket`, like this:

```shell
rcli bucket create test-storage/bucket-1
```

This command will create a new bucket with default settings. You can specify the settings for the new bucket using the
available options, such as `--quota-type` and `--quota-size`, like this:

```shell
rcli bucket create --quota-type FIFO --quota-size 20Gb test-storage/bucket-1
```

## Updating Settings

You can update the settings of an existing bucket using the `update` subcommand of `rcli bucket`, like this:

```shell
rcli bucket update --quota-size 100Gb test-storage/bucket-1
```

To see the full list of available settings, use the `--help` flag with the `update` subcommand:

```shell
rcli bucket update --help
```

## Removing a Bucket

To remove a bucket from your storage engine, use the `rm` subcommand of `rcli bucket`, like this:

```shell
rcli bucket rm test-storage/bucket-1
```

!!!Warning
    When you remove a bucket from your storage engine, you delete all of its data. Use this command with caution.

You also can remove only selected entries from a bucket using the `--only-entries` option:

```shell
rcli bucket rm test-storage/bucket-1 --only-entries entry-1,entry-2,old-*
```
