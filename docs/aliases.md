# Aliases

Reduct CLI client uses aliases to communicate with a storage engine, so that a user doesn't need to type its URL and
credentials for every command.

## Creating an alias

You can create an alias with the following command:

```shell
rcli alias add play
```

You can also provide a URL and API token as options:

```shell
rcli alias  add -L  https://play.reduct-storage.dev -t reduct play
```

## Browsing aliases

Now you can see it the new alias in list or check it URL:

```shell
rcli alias ls
rcli alias show play # you can add -t flag to see token
```

## Removing an alias

To remove an alias, use command `rm`:

```shell
rcli alias rm play
```
