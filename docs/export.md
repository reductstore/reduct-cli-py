# Export Data

## Export To Folder

The `rcli export folder` command allows you to export data from a bucket in your ReductStore instance to a local folder
on
your computer. This can be useful if you want to make a copy of your data for backup or offline access.

The `rcli export folder` command has the following syntax:

```
rcli export folder [OPTIONS] SRC DEST
```

`SRC` should be the source bucket that you want to export data from. It should be in the format `ALIAS/BUCKET_NAME`,
where
`ALIAS` is the alias that you created for your storage engine (using the `rcli alias add` command), and `BUCKET_NAME` is
the
name of the bucket.

`DEST` should be the destination folder on your computer where you want to save the exported data.

Here is an example of how you might use the `rcli export folder` command:

```
rcli export folder myalias/mybucket ./exported-data
```

This will export all the data from the `mybucket` bucket in your storage engine (accessed using the `myalias` alias) to
the exported-data folder on your desktop.

## Export To Bucket

The` rcli export bucket` command allows you to copy data from a source bucket in your ReductStore instance to a
destination bucket.
This can be useful if you want to make a copy of your data for backup or to transfer data between different buckets.

To use the rcli mirror command, open a terminal and type the following, replacing `[OPTIONS]` with any optional flags
that you want to use (see below for a list of available options), `SRC` with the source bucket that you want to copy
data from, and `DEST` with the destination bucket where you want to save the copied data:

```
rcli export bucket [OPTIONS] SRC DEST
```

`SRC` and `DEST` should be in the format `ALIAS/BUCKET_NAME`, where `ALIAS` is the alias that you created for your
ReductStore instance (using the `rcli alias add` command), and `BUCKET_NAME` is the name of the bucket.

If the destination bucket doesn't exist, it will be created with the same settings as the source bucket.

For example, to copy all data from the `mybucket` bucket in your ReductStore instance (accessed using the `myalias`
alias) to
the `newbucket` bucket, you would type the following command:

```
rcli mirror myalias/mybucket myalias/newbucket
```

## Available options

Here is a list of the options that you can use with the `rcli export` commands:

* `--start`: This option allows you to specify a starting time point for the data that you want to export. Data with
  timestamps newer than this time point will be included in the export. The time point should be in ISO format (e.g.,
  2022-01-01T00:00:00Z) or Unix timestamp in milliseconds (e.g., 1633046400000).

* `--stop`: This option allows you to specify an ending time point for the data that you want to export. Data with
  timestamps older than this time point will be included in the export. The time point should be in ISO format (e.g.,
  2022-01-01T00:00:00Z) or Unix timestamp in milliseconds (e.g., 1633046400000).

* `--entries`: With this option, you can specify the entries that you want to export. The entries should be specified
  as a comma-separated list of entry names (e.g., `--entries=entry1,entry2`).
  You can also use the `*` wildcard to match all entries with a certain prefix (e.g., `--entries=prefix-*`).

* `--include`: Specify the labels to include in the export. Only data with
  the specified labels will be exported. The labels should be specified as a comma-separated list of label names (e.g.,
  and values (e.g., `--include= color=red,size=big`).

* `--exclude`: Specify the labels to exclude from the export. Data with
  the specified labels will not be exported. The labels should be specified as a comma-separated list of label names (
  e.g., and values (e.g., `--exclude= color=red,size=big`).

* `--ext`: Specify the file extension that you want to use for the exported data files. If not specified, the default
  extension will be guessed based on the MIME content type of the data. Only for `rcli export folder`.

* `--with-metadata`: If this option is specified, the CLI client creates a metadata file in JSON format for each
  exported data record.
  The metadata file contains information like the timestamp, content type, size and the labels that were applied to the
  data. Only for `rcli export folder`.

* `--limit`: This option allows you to specify the maximum number of entries that you want to export. If not specified,
  all entries will be exported.

You also can use the global `--parallel` option to specify the number of entries that you want to export in parallel:

```
rcli  --parallel 10  export folder myalias/mybucket ./exported-data
```

## Examples

Here are some examples of how you might use the `rcli export` command with the available options:

To export all data from the `mybucket` bucket that was created after January 1, 2022:

```
rcli export folder --start 2022-01-01T00:00:00Z myalias/mybucket ./exported-data
```

To export all data from the `mybucket` bucket to another instance that was created before January 1, 2022:

```
rcli export bucket --stop 2022-01-01T00:00:00Z myalias/mybucket another_alias/another_bucket
```

To export all data from the mybucket bucket that was created between January 1, 2022 and January 31, 2022
for certain entries:

```
rcli export folder --start 2022-01-01T00:00:00Z --stop 2022-01-31T00:00:00Z myalias/mybucket  ./exported-data
```

To export all data from certain entries in the `mybucket` bucket:

```
rcli export bucket --entries=entry1,entry2 myalias/mybucket myalias/only_entry1_and_entry2
```
