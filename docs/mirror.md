# Mirror data

The `rcli` command line client provides the mirror command to copy data from one bucket to another, whether the buckets
are on the same storage engine or on different storage engines.

To mirror data from one bucket to another, use the following command, where `server-1/bucket` is the source bucket and
`server-2`/bucket is the destination bucket:

```shell
rcli  mirror server-1/bucket server-2/bucket
```

You can also specify a time interval for mirroring data using the `--start` and `--stop` flags, like this:

```shell
rcli  mirror --start 2022-11-06T20:10:30 --stop 2022-11-06T20:14:30  server-1/bucket server-2/bucket
```

This will only mirror data from the source bucket that was created or modified within the specified time interval. This
can be useful if you only want to mirror a specific subset of the data in the source bucket.
