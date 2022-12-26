# Export Data

The `rcli export folder` command allows you to export data from a bucket in your storage engine to a local folder on
your
computer. This can be useful if you want to make a copy of your data for backup or offline access.

The `rcli export folder` command has the following syntax:

```
rcli export folder [OPTIONS] SRC DEST
```

`SRC` should be the source bucket that you want to export data from. It should be in the format `ALIAS/BUCKET_NAME`,
where
`ALIAS` is the alias that you created for your storage engine (using the `rcli alias add` command), and `BUCKET_NAME` is
the
name of the bucket.

`DEST` should be the destination folder on your computer where you want to save the exported data.

Here is an example of how you might use the `rcli export folder` command:

```
rcli export folder myalias/mybucket /Users/me/Desktop/exported-data
```

This will export all the data from the `mybucket` bucket in your storage engine (accessed using the `myalias` alias) to
the exported-data folder on your desktop.

### Available options

Here is a list of the options that you can use with the `rcli export folder` command:

* -`-start`: This option allows you to specify a starting time point for the data that you want to export. Data with
  timestamps newer than this time point will be included in the export. The time point should be in ISO format (e.g.,
  2022-01-01T00:00:00Z).

* -`-stop`: This option allows you to specify an ending time point for the data that you want to export. Data with
  timestamps older than this time point will be included in the export. The time point should be in ISO format (e.g.,
  2022-01-01T00:00:00Z).


### Examples

Here are some examples of how you might use the `rcli export folder` command with the available options:

To export all data from the `mybucket` bucket that was created after January 1, 2022:

```
rcli export folder --start 2022-01-01T00:00:00Z myalias/mybucket /Users/me/Desktop/exported-data
```

To export all data from the mybucket bucket that was created before January 1, 2022:

```
rcli export folder --stop 2022-01-01T00:00:00Z myalias/mybucket /Users/me/Desktop/exported-data
```

To export all data from the mybucket bucket that was created between January 1, 2022 and January 31, 2022:

```
rcli export folder --start 2022-01-01T00:00:00Z --stop 2022-01-31T00:00:00Z myalias/mybucket /Users/me/Desktop/exported-data
```
