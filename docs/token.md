# Token Commands

If you set an [alias](./aliases.md) for your server, you can manage its tokens by using the `token` subcommand:

```shell
rcli token --help
```

## Listing tokens

You can check a list of existing tokens on the server:

```shell
rcli token ls test-storage
```

## Creating a token

To create a token you should use command create and provide a name of the new token and its permissions:

```shell
rcli token create test-storage token-1 --full-access --read=bucket-1 --write="bucket-2,bucket-3"
```

## Showing a token

To show information about a certain token use the `show` subcommand:

```shell
rcli token show test-storage token-1
```

## Removing a token

You can remove a token with the `rm` subcommand:

```shell
rcli token rm test-storage token-1
```
