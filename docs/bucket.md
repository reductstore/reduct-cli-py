# Bucket Commands

If you set an [alias](./aliases.md) for your server, you can manage its buckets by using `bucket` subcommand:

```shell
rcli bucket --help
```

## Usage Example

You can check a list of existing buckets on the server:

```shell
rcli bucket ls ALIAS
```
Or you can print a table with buckets and its information:

```shell
rcli bucket ls --full ALIAS
```
