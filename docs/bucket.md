# Bucket Commands

If you set an [alias](./aliases.md) for your server, you can manage its buckets by using `bucket` subcommand:

```shell
rcli bucket --help
```

## Browsing buckets

You can check a list of existing buckets on the server:

```shell
rcli bucket ls ALIAS
```

Or you can print a table with buckets and its information:

```shell
rcli bucket ls --full ALIAS
```

To show information about a certain bucket use the `show` subcommand with path `ALIAS/BUCKET_NAME`:

```shell
rcli bucket show ALIAS/BUCKET_NAME
```

You can also get the bucket's settings and entry list with flag `--full`:

```shell
rcli bucket show --full ALIAS/BUCKET_NAME
```
