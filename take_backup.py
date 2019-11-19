import typing
from argparse import Namespace

import click
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption, Snapshot, CreationData, Disk
from loguru import logger
from uuid import uuid4

logger.level("TRACE")

__version__ = (0, 0, 1)


@click.group("backup")
@click.pass_context
@click.option("--resource-group-name")
@click.option("-y", "--yes", is_flag=True, default=False)
def backup_group(ctx, resource_group_name, yes):
    ctx.ensure_object(Namespace)

    logger.info("Acquiring Azure login credentials from az cli...")
    # Create a management client from our Azure CLI credentials
    compute_client = get_client_from_cli_profile(ComputeManagementClient)
    ctx.obj.compute_client = compute_client
    ctx.obj.confirm = yes
    ctx.obj.resource_group_name = resource_group_name
    logger.debug("context.obj := {}", ctx.obj)


@backup_group.command("capture")
@click.pass_obj
def take_backup(obj):
    logger.info("enumerating disks....")
    # get all the disks we know of
    disks: typing.List[Disk] = list(obj.compute_client.disks.list())
    logger.debug([disk.id for disk in disks])

    # in-flight API calls
    futures = []

    logger.info("creating snapshots...")
    # generate Shapshot options
    for disk in disks:
        logger.debug("creating snapshot for disk.id := {}\tdisk.name:={}", disk.id, disk.name)
        # create creation data for the new snapshot, using the current disk's id as a base (snapshot `disk`)
        creation_data = CreationData(create_option=DiskCreateOption.copy, source_resource_id=disk.id)
        # create the snapshot object itself
        snapshot = Snapshot(location=disk.location, creation_data=creation_data)
        snapshot_name = f"{disk.name.split('OsDisk')[0]}{uuid4()}"
        logger.info(f"creating snapshot with name '{snapshot_name}'...")
        if not obj.confirm:
            click.confirm("do API actions?", abort=True)

        # once the snapshot object is built, we need to invoke the API call to get Azure to actually make the snapshot
        logger.debug("invoking API call...")

        future = obj.compute_client.snapshots.create_or_update(obj.resource_group_name, snapshot_name, snapshot)
        futures.append(future)

    logger.info("gathering responses...")
    logger.info([future.result() for future in futures])

    logger.info("all done ~^.^~ ")


if __name__ == '__main__':
    logger.info("Azure snapshot management tool. v{}", __version__)
    backup_group()
