# Aliases

The ReductStore CLI client uses aliases to simplify communication with a storage engine. This way, users don't have to
type the URL and credentials for the storage engine each time they want to use it.
Creating an alias

To create an alias, use the following rcli command:

You can create an alias with the following command:

```shell
rcli alias add play
```

Alternatively, you can provide the URL and API token for the storage engine as options:

```shell
rcli alias  add -L  https://play.reduct.store -t reduct play
```

## Browsing aliases

Once you've created an alias, you can use the rcli alias command to view it in a list or check its URL:

```shell
rcli alias ls
rcli alias show play # you can add the -t flag to see the token
```

## Removing an alias

To remove an alias, use the rm subcommand of rcli alias:

```shell
rcli alias rm play
```
