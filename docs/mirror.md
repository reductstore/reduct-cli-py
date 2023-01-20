# Mirror data

The` rcli mirror` command allows you to copy data from a source bucket in your storage engine to a destination bucket.
This can be useful if you want to make a copy of your data for backup or to transfer data between different buckets.

To use the rcli mirror command, open a terminal and type the following, replacing `[OPTIONS]` with any optional flags
that
you want to use (see below for a list of available options), `SRC` with the source bucket that you want to copy data
from,
and `DEST` with the destination bucket where you want to save the copied data:

```
rcli mirror [OPTIONS] SRC DEST
```

`SRC` and `DEST` should be in the format `ALIAS/BUCKET_NAME`, where `ALIAS` is the alias that you created for your
storage
engine (using the rcli alias add command), and `BUCKET_NAME` is the name of the bucket.

If the destination bucket doesn't exist, it will be created with the same settings as the source bucket.

For example, to copy all data from the `mybucket` bucket in your storage engine (accessed using the `myalias` alias) to
the
`newbucket` bucket, you would type the following command:

```
rcli mirror myalias/mybucket myalias/newbucket
```

## Available options

Here is a list of the options that you can use with the rcli mirror command:

* `--start`: This option allows you to specify a starting time point for the data that you want to copy. Data with
  timestamps newer than this time point will be included in the copy. The time point should be in ISO format (e.g.,
  2022-01-01T00:00:00Z).
* `--stop`: This option allows you to specify an ending time point for the data that you want to copy. Data with
  timestamps older than this time point will be included in the copy. The time point should be in ISO format (e.g.,
  2022-01-01T00:00:00Z).
* `--entries`: With this option, you can specify the entries that you want to export. The entries should be
  specified
  as a comma-separated list of entry names (e.g., `--entries=entry1,entry2`).

You also can use the global `--parallel` option to specify the number of entries that you want to mirror in parallel:

```
rcli  --parallel 10  mirror myalias/mybucket myalias/newbucket
```

## Examples

Here are some examples of how you might use the `rcli mirror` command with the available options:

To copy all data from the `mybucket` bucket that was created after January 1, 2022 to the `newbucket` bucket:

```
rcli mirror --start 2022-01-01T00:00:00Z myalias/mybucket myalias/newbucket
```

To copy all data from the `mybucket` bucket that was created before January 1, 2022 to the `newbucket` bucket:

```
rcli mirror --stop 2022-01-01T00:00:00Z myalias/mybucket myalias/newbucket
```

To copy all data from the `mybucket` bucket that was created between January 1, 2022 and January 31, 2022 to
the `newbucket`
bucket:

```
rcli mirror --start 2022-01-01T00:00:00Z --stop 2022-01-31T00:00:00Z myalias/mybucket myalias/newbucket
```
