#!/usr/local/bin/python
"""
Python Matter DoorLock cluster user and credential management utility.
Copyright (C) 2026 Peter Babinski

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
from asyncio import Event, create_task, get_event_loop, run
from typing import Sequence

from aiohttp import ClientSession
from chip.clusters import Objects as Clusters
from matter_server.client.client import MatterClient
from matter_server.client.models.device_types import DoorLock
from matter_server.common.helpers.json import json_dumps


"""
Examples borrowed from:
https://docs.nordicsemi.com/bundle/ncs-3.0.1/page/nrf/samples/matter/lock/README.html
"""

def set_user(
    userIndex: int, 
    userName: str,
    userUniqueID: int,
    userType: Clusters.DoorLock.Enums.UserTypeEnum,
):
    return Clusters.DoorLock.Commands.SetUser(
        operationType=Clusters.DoorLock.Enums.DataOperationTypeEnum.kAdd,
        userIndex=userIndex,
        userName=userName,
        userUniqueID=userUniqueID,
        userStatus=Clusters.DoorLock.Enums.UserStatusEnum.kOccupiedEnabled,
        userType=userType,
        credentialRule=Clusters.DoorLock.Enums.CredentialRuleEnum.kSingle,
    )

def get_user(userIndex: int):
    return Clusters.DoorLock.Commands.GetUser(userIndex=userIndex)

def clear_user(userIndex: int):
    return Clusters.DoorLock.Commands.ClearUser(userIndex=userIndex)

def set_credential(userIndex: int, credentialIndex: int, pin: str):
    return Clusters.DoorLock.Commands.SetCredential(
        operationType=Clusters.DoorLock.Enums.DataOperationTypeEnum.kAdd,
        credential=Clusters.DoorLock.Structs.CredentialStruct(
            credentialType=Clusters.DoorLock.Enums.CredentialTypeEnum.kPin, 
            credentialIndex=credentialIndex
        ),
        credentialData=pin.encode(),
        userIndex=userIndex,
    )

def get_credential(credentialIndex: int):
    return Clusters.DoorLock.Commands.GetCredentialStatus(
        credential=Clusters.DoorLock.Structs.CredentialStruct(
            credentialType=Clusters.DoorLock.Enums.CredentialTypeEnum.kPin, 
            credentialIndex=credentialIndex
        )
    )

def clear_credential(credentialIndex: int):
    return Clusters.DoorLock.Commands.ClearCredential(
        credential=Clusters.DoorLock.Structs.CredentialStruct(
            credentialType=Clusters.DoorLock.Enums.CredentialTypeEnum.kPin, 
            credentialIndex=credentialIndex
        )
    )

def enum_action(enum_class):
    """
    Slightly modified from:
    https://github.com/aatifsyed/enum-actions/blob/main/enum_actions/__init__.py
    """

    class EnumAction(argparse.Action):
        def __init__(
            self,
            option_strings,
            dest,
            nargs = None,
            const = None,
            default = None,
            type = None,
            choices = None,
            required = False,
            help = None,
            metavar = None,
        ) -> None:
            self.cls = enum_class
            super().__init__(
                option_strings,
                dest,
                nargs=nargs,
                const=const,
                default=default,
                type=type,
                choices=[variant.name for variant in enum_class],
                required=required,
                help=help,
                metavar=metavar,
            )

        def __call__(  # type: ignore
            self,
            parser,
            namespace,
            values = None,
            option_string = None,
        ) -> None:
            if not isinstance(values, str):
                raise TypeError
            setattr(namespace, self.dest, getattr(self.cls, values))

    return EnumAction


async def main(args: Sequence[str] | None = None) -> None:
    prog = argparse.ArgumentParser(description="Matter Door Lock Utility")
    prog.add_argument(
        "--nodeId",
        dest="nodeId",
        action="store",
        type=int,
        required=True,
    )
    prog.add_argument(
        "--websocketUrl",
        dest="websocketUrl",
        action="store",
        type=str,
        default="ws://localhost:5580/ws",
    )
    prog.add_argument(
        "--timeout",
        dest="timeout",
        action="store",
        type=int,
        default=5000,
    )
    subparser = prog.add_subparsers(required=True)
    set_user_parser = subparser.add_parser("set-user")
    set_user_parser.set_defaults(command=set_user)
    set_user_parser.add_argument(
        "--userIndex",
        dest="userIndex",
        action="store",
        type=int,
        required=True,
    )
    set_user_parser.add_argument(
        "--userName",
        dest="userName",
        action="store",
        type=str,
        required=True,
    )
    set_user_parser.add_argument(
        "--userUniqueID",
        dest="userUniqueID",
        action="store",
        type=int,
        required=True,
    )
    set_user_parser.add_argument(
        "--userType",
        dest="userType",
        action=enum_action(Clusters.DoorLock.Enums.UserTypeEnum),
        required=True,
    )
    get_user_parser = subparser.add_parser("get-user")
    get_user_parser.set_defaults(command=get_user)
    get_user_parser.add_argument(
        "--userIndex",
        dest="userIndex",
        action="store",
        type=int,
        required=True,
    )
    clear_user_parser = subparser.add_parser("clear-user")
    clear_user_parser.set_defaults(command=clear_user)
    clear_user_parser.add_argument(
        "--userIndex",
        dest="userIndex",
        action="store",
        type=int,
        required=True,
    )
    set_credential_parser = subparser.add_parser("set-credential")
    set_credential_parser.set_defaults(command=set_credential)
    set_credential_parser.add_argument(
        "--userIndex",
        dest="userIndex",
        action="store",
        type=int,
        required=True,
    )
    set_credential_parser.add_argument(
        "--credentialIndex",
        dest="credentialIndex",
        action="store",
        type=int,
        required=True,
    )
    set_credential_parser.add_argument(
        "--pin",
        dest="pin",
        action="store",
        type=str,
        required=True,
    )
    get_credential_parser = subparser.add_parser("get-credential")
    get_credential_parser.set_defaults(command=get_credential)
    get_credential_parser.add_argument(
        "--credentialIndex",
        dest="credentialIndex",
        action="store",
        type=int,
        required=True,
    )
    clear_credential_parser = subparser.add_parser("clear-credential")
    clear_credential_parser.set_defaults(command=clear_credential)
    clear_credential_parser.add_argument(
        "--credentialIndex",
        dest="credentialIndex",
        action="store",
        type=int,
        required=True,
    )

    namespace = vars(prog.parse_args(args)).copy()
    websocket_url = namespace.pop("websocketUrl")
    timeout = namespace.pop("timeout")
    node_id = namespace.pop("nodeId")
    command = namespace.pop("command")(**namespace)

    async with ClientSession() as session:
        client = MatterClient(websocket_url, session)
        event = Event()
        create_task(client.start_listening(event))
        await event.wait()
        for endpoint in client.get_node(node_id).endpoints.values():
            if DoorLock in endpoint.device_types:
                for cluster in endpoint.clusters.values():
                    if isinstance(cluster, Clusters.DoorLock):
                        response = await client.send_device_command(
                            node_id, 
                            endpoint.endpoint_id, 
                            command,
                            timed_request_timeout_ms=timeout,
                        )
                        print(json_dumps(response))
                        return
        raise RuntimeError(f"No DoorLock cluster found for node {node_id}")
                      

if __name__ == '__main__':
    # Run the main coroutine
    run(main())
