"""Unit tests for export bucket command"""
import asyncio
from unittest.mock import call, ANY

import pytest
from reduct import Client, Bucket, ReductError

from tests.conftest import AsyncIter


@pytest.fixture(name="dest_bucket")
def _make_dest_bucket(mocker) -> Bucket:
    bucket = mocker.Mock(spec=Bucket)
    bucket.name = "dest_bucket"

    return bucket


@pytest.fixture(name="client")
def _make_client(mocker, src_bucket, dest_bucket) -> Client:
    kls = mocker.patch("reduct_cli.export.build_client")
    client = mocker.Mock(spec=Client)
    client.get_bucket.return_value = src_bucket
    client.create_bucket.return_value = dest_bucket

    kls.return_value = client
    return client


def walk_async_iterator(iterator: AsyncIter):
    """Walk through async iterator and return a list"""

    async def walk():
        return [data async for data in iterator]

    return asyncio.new_event_loop().run_until_complete(walk())


@pytest.mark.usefixtures("set_alias")
def test__export_bucket_ok(
    runner, conf, client, src_settings, src_bucket, dest_bucket, records
):  # pylint: disable=too-many-arguments
    """Should export data from a bucket to another one"""

    result = runner(f"-c {conf} export bucket test/src_bucket test/dest_bucket")
    assert "Entry 'entry-1' (copied 1 records (6 B)" in result.output
    assert result.exit_code == 0

    client.get_bucket.assert_called_with("src_bucket")
    client.create_bucket.assert_called_with(
        "dest_bucket", settings=src_settings, exist_ok=True
    )

    assert src_bucket.query.call_args_list[0] == call(
        "entry-1", start=1000000000, stop=5000000000, include={}, exclude={}, ttl=ANY
    )
    assert dest_bucket.write.await_args_list[0] == call(
        "entry-1",
        data=ANY,
        content_length=records[0].size,
        timestamp=records[0].timestamp,
        content_type=records[0].content_type,
        labels=records[0].labels,
    )
    assert walk_async_iterator(dest_bucket.write.await_args_list[0].kwargs["data"]) == [
        b"Hey"
    ]
    assert dest_bucket.write.await_args_list[1] == call(
        "entry-1",
        data=ANY,
        content_length=records[1].size,
        timestamp=records[1].timestamp,
        content_type=records[1].content_type,
        labels=records[1].labels,
    )
    assert walk_async_iterator(dest_bucket.write.await_args_list[1].kwargs["data"]) == [
        b"Bye"
    ]

    assert src_bucket.query.call_args_list[1] == call(
        "entry-2", start=1000000000, stop=5000000000, include={}, exclude={}, ttl=ANY
    )
    assert dest_bucket.write.await_args_list[2] == call(
        "entry-2",
        data=ANY,
        content_length=records[0].size,
        timestamp=records[0].timestamp,
        content_type=records[0].content_type,
        labels=records[0].labels,
    )


@pytest.mark.usefixtures("set_alias", "client")
def test__export_to_bucket_ok_with_interval(runner, conf, src_bucket):
    """Should export data from a bucket to another one with time interval"""
    result = runner(
        f"-c {conf} export bucket --start 2022-01-02T00:00:01.100300+02:00 "
        f"--stop 2022-02-01T00:00:00+02:00 "
        f"test/src_bucket test/dest_bucket"
    )
    assert "Entry 'entry-1' (copied 1 records (6 B)" in result.output
    assert result.exit_code == 0

    assert src_bucket.query.call_args_list[0] == call(
        "entry-1",
        start=1641074401100300,
        stop=1643666400000000,
        include={},
        exclude={},
        ttl=ANY,
    )


@pytest.mark.usefixtures("set_alias")
def test__get_error(runner, conf, client):
    """Should print error if something got wrong"""
    client.get_bucket.side_effect = RuntimeError("Oops")
    result = runner(f"-c {conf} export bucket test/src_bucket test/dest_bucket")
    assert result.output == "[RuntimeError] Oops\nAborted!\n"
    assert result.exit_code == 1


@pytest.mark.usefixtures("set_alias", "client", "src_bucket")
def test__export_bucket_409(runner, conf, dest_bucket):
    """Should skip record if it already exists in destination bucket"""
    dest_bucket.write.side_effect = ReductError(409, "Conflict")
    result = runner(f"-c {conf} export bucket test/src_bucket test/dest_bucket")
    assert result.exit_code == 0


@pytest.mark.usefixtures("set_alias", "client", "dest_bucket")
def test__export_bucket_utc_timestamp(runner, conf, src_bucket):
    """Should support Z designator for UTC timestamps"""
    result = runner(
        f"-c {conf} export bucket test/src_bucket test/dest_bucket "
        f"--start 2022-01-02T00:00:01.100300Z --stop 2022-02-01T00:00:00Z"
    )
    assert result.exit_code == 0
    assert src_bucket.query.call_args_list[0] == call(
        "entry-1",
        start=1641081601100300,
        stop=1643673600000000,
        include={},
        exclude={},
        ttl=ANY,
    )


@pytest.mark.usefixtures("set_alias", "client", "dest_bucket")
def test__export_bucket_specific_entry(runner, conf, src_bucket):
    """Should export specific entry"""
    result = runner(
        f"-c {conf} export bucket test/src_bucket test/dest_bucket --entries=entry-2"
    )
    assert result.exit_code == 0
    assert src_bucket.query.call_args_list == [
        call("entry-2", start=ANY, stop=ANY, include={}, exclude={}, ttl=ANY)
    ]


@pytest.mark.usefixtures("set_alias", "client", "dest_bucket")
def test__export_bucket_multiple_specific_entry(runner, conf, src_bucket):
    """Should export bucket multiple specific entries"""
    result = runner(
        f"-c {conf} export bucket test/src_bucket test/dest_bucket --entries=entry-*"
    )
    assert result.exit_code == 0
    assert src_bucket.query.call_args_list == [
        call("entry-1", start=ANY, stop=ANY, include={}, exclude={}, ttl=ANY),
        call("entry-2", start=ANY, stop=ANY, include={}, exclude={}, ttl=ANY),
    ]
    src_bucket.query.call_args_list = []

    result = runner(
        f"-c {conf} export bucket test/src_bucket test/dest_bucket "
        f"--entries=entry-1,some-other-entry"
    )
    assert result.exit_code == 0
    assert src_bucket.query.call_args_list == [
        call("entry-1", start=ANY, stop=ANY, include={}, exclude={}, ttl=ANY),
        call("some-other-entry", start=ANY, stop=ANY, include={}, exclude={}, ttl=ANY),
    ]
    src_bucket.query.call_args_list = []

    result = runner(
        f"-c {conf} export bucket test/src_bucket test/dest_bucket --entries=entry-1,entry-2"
    )
    assert result.exit_code == 0
    assert src_bucket.query.call_args_list == [
        call("entry-1", start=ANY, stop=ANY, include={}, exclude={}, ttl=ANY),
        call("entry-2", start=ANY, stop=ANY, include={}, exclude={}, ttl=ANY),
    ]


@pytest.mark.usefixtures("set_alias", "client", "dest_bucket")
def test__export_bucket_with_filters(runner, conf, src_bucket):
    """Should export bucket with filters"""
    result = runner(
        f"-c {conf} export bucket test/src_bucket test/dest_bucket "
        f"--include label1=value1,label2=value2 --exclude label3=value3,label4=value4"
    )
    assert result.exit_code == 0
    assert src_bucket.query.call_args_list[0] == call(
        "entry-1",
        start=ANY,
        stop=ANY,
        include={"label1": "value1", "label2": "value2"},
        exclude={"label3": "value3", "label4": "value4"},
        ttl=ANY,
    )


@pytest.mark.usefixtures("set_alias", "client", "dest_bucket")
def test__export_bucket_calc_ttl(runner, conf, src_bucket):
    """Should query bucket with calculated TTL = timeout * parallel tasks"""
    result = runner(
        f"-c {conf} -t 3 -p 2 export bucket test/src_bucket test/dest_bucket"
    )
    assert result.exit_code == 0
    assert src_bucket.query.call_args_list[0] == call(
        "entry-1", start=ANY, stop=ANY, include={}, exclude={}, ttl=6
    )
