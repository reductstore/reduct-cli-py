# Replication Commands

The `rcli` command line client allows you to manage the replication settings for your storage engine using
the `replication` subcommand. For example:

```
rcli replication --help
```

You should set an [alias](./aliases.md) for your storage engine, so that you can use the alias in the `rcli replication`
command to refer to the storage engine. For example:

```
rcli replication ls test-storage
```

## Listing Replications

To see a list of existing replications on your storage engine, use the `ls` subcommand of `rcli replication`, like this:

```
rcli replication ls test-storage
```

You can also use the `--full` flag to show status information about each replication:

```
rcli replication ls --full test-storage

┏━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃        Name ┃ Active ┃ Provisioned ┃ Pending Records ┃
┡━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ stress_test │ True   │ True        │ 0               │
└─────────────┴────────┴─────────────┴─────────────────┘
```

## Showing Details for a Replication

To see detailed information about a specific replication, use the `show` subcommand of `rcli replication`, like this:

```
rcli replication show test-storage stress_test

╭──────────── State ─────────────╮╭─────────── Settings ────────────╮
│ Name:                          ││ Source Bucket:                  │
│ stress_test                    ││ stress_test                     │
│ Active:                        ││ Destination Bucket:    demo     │
│ True                           ││ Destination Server:             │
│ Provisioned:                   ││ https://play.reduct.store/      │
│ True                           ││ Entries:               []       │
╰────────────────────────────────╯╰─────────────────────────────────╯
                          Errors last hour
┏━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Error Code ┃ Count ┃ Last Message                                 ┃
┡━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│        425 │ 1     │ Record with timestamp 1706741353382000 is    │
│            │       │ still being written                          │
└────────────┴───────┴──────────────────────────────────────────────┘
```

## Creating a Replication

To create a new replication on your storage engine, use the `create` subcommand of `rcli replication`, like this:

```
rcli replication create test-storage replication-name src_bucket  dest_bucket  https://play.reduct.store/
```

This command will create a new replication with default settings. You can specify the settings for the new replication
using the available options:

* `--dst-token:` access token with write permissions to the destination bucket
* `--entries`: list of entries separated by comma. If not specified, all entries will be replicated. Use * to replicate
  all entries with a certain prefix (e.g., --entries=prefix-*)
* `--include`: This is an optional argument. It specifies the labels which a record must have in order to be included in
  the replication. If not specified, all records will be included. A record must have all the specified labels
* `--exclude`: This is an optional argument. It specifies the labels which a record must not have in order to be included
  in the replication. If not specified, all records will be included. A record must not have any of the specified
  labels.

## Updating Settings

You can update the settings of an existing replication using the `update` subcommand of `rcli replication`, like this:

```
rcli replication update test-storage replication-name src_bucket  new_dest_bucket  https://play.reduct.store/
```

It has the same options as the `create` subcommand.

## Removing a Replication

To remove a replication from your storage engine, use the `rm` subcommand of `rcli replication`, like this:

```
rcli replication rm test-storage replication-name
```
