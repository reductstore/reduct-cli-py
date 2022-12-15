# Token Commands

The `rcli` command line client allows you to manage the access tokens for your storage engine using the `token`
subcommand. For example:

```
rcli token --help
```

You should set an [alias](./aliases.md) for your storage engine, so that you can use the alias in the `rcli token`
command to
refer to the storage engine. For example:

```shell
rcli token ls test-storage
```

## Listing Tokens

To see a list of existing access tokens on your storage engine, use the `ls` subcommand of `rcli token`, like this:

```shell
rcli token ls test-storage
```

## Creating a Token

To create a new token on your storage engine, use the `create` subcommand of `rcli token`, like this:

```shell
rcli token create test-storage token-1 --full-access --read=bucket-1 --write="bucket-2,bucket-3"
```

This command creates a new token with the given name and permissions. You can specify the permissions using the
available options, such as `--full-access` and `--read/--write` to grant or restrict access to specific buckets.

## Showing a Token

To see detailed information about a specific token, use the `show` subcommand of `rcli token`, like this:

```shell
rcli token show test-storage token-1
```

This will show the name, permissions, and other details for the specified token.

## Removing a Token

To remove a token from your storage engine, use the `rm` subcommand of `rcli token`, like this:

```shell
rcli token rm test-storage token-1
```

This will remove the token with the given name from the storage engine. Be careful when using this command, as it will
permanently delete the token and any access granted by the token will be lost.
