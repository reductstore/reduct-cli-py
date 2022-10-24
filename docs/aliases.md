# Aliases

Reduct CLI client uses aliases to communicate with a storage engine, so that a user doesn't need to type its URL and
credentials for every command.

## Usage Example

You can create an alias with the following command:

```shell
reduct-cli alias add play
```

Now you can see it the new alias in list or check it URL:

```shell
reduct-cli alias ls
reduct-cli alias show play # you can add -t flag to see token
```
