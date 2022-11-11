# Mirror data

The CLI client provides the `mirror` command to copy data from a bucket to another one. The source and destination buckets
could belong to one or two different storage engine.

```shell
rcli  mirror server-1/bucket server-2/bucket
```

A user can also specify a time interval for mirroring data with flags `--start` and `--stop`:

```shell
rcli  mirror --start 2022-11-06T20:10:30 --stop 2022-11-06T20:14:30  server-1/bucket server-2/bucket
```
