import asyncio
from typing import List, Dict, Tuple, Optional, Any

from bluesky_queueserver.manager.profile_ops import devices_from_nspace, load_worker_startup_code  # type: ignore
import zmq

from bluesky.protocols import Checkable, Flyable, Hinted, Movable, Pausable, Readable, Stageable, Stoppable, Subscribable

class HardwareProxy:
    def __init__(self, *, startup_dir: Optional[str]=None, startup_script_path: Optional[str]=None, startup_module_name: Optional[str]=None):
        super().__init__()
        self.startup_dir = startup_dir
        self.startup_script_path = startup_script_path
        self.startup_module_name = startup_module_name
        self._zmq_ip_server = "tcp://*:60620"
        #TODO config port?

        self.namespace: Dict[str, "Readable"] = {}
        self.reload()

    def reload(self):
        self.namespace = devices_from_nspace(load_worker_startup_code(startup_dir=self.startup_dir, startup_script_path=self.startup_script_path, startup_module_name=self.startup_module_name))

    def list(self, protocol: Optional[str]=None) -> List[str]:
        if protocol is None:
            return list(self.namespace.keys())
        elif protocol.lower() == "checkable":
            return [k for k in self.namespace.keys() if isinstance(self.namespace[k], Checkable)]
        elif protocol.lower() == "flyable":
            return [k for k in self.namespace.keys() if isinstance(self.namespace[k], Flyable)]
        elif protocol.lower() == "hinted":
            return [k for k in self.namespace.keys() if isinstance(self.namespace[k], Hinted)]
        elif protocol.lower() == "movable":
            return [k for k in self.namespace.keys() if isinstance(self.namespace[k], Movable)]
        elif protocol.lower() == "pausable":
            return [k for k in self.namespace.keys() if isinstance(self.namespace[k], Pausable)]
        elif protocol.lower() == "readable":
            return [k for k in self.namespace.keys() if isinstance(self.namespace[k], Readable)]
        elif protocol.lower() == "stageable":
            return [k for k in self.namespace.keys() if isinstance(self.namespace[k], Stageable)]
        elif protocol.lower() == "stoppable":
            return [k for k in self.namespace.keys() if isinstance(self.namespace[k], Stoppable)]
        elif protocol.lower() == "subscribable":
            return [k for k in self.namespace.keys() if isinstance(self.namespace[k], Subscribable)]
        else:
            raise ValueError(f"'{protocol}' not recognized as a valid protocol")

    def read(self, device: str) -> Dict[str, Dict[str, Any]]:
        return self.namespace[device].read()

    def describe(self, device: str) -> Dict[str, Dict[str, Any]]:
        return self.namespace[device].describe()

    def read_configuration(self, device: str) -> Dict[str, Dict[str, Any]]:
        return self.namespace[device].read_configuration()

    def describe_configuration(self, device: str) -> Dict[str, Dict[str, Any]]:
        return self.namespace[device].describe_configuration()

    def check_value(self, device: str, value: Any) -> bool:
        try:
            self.namespace[device].check_value(value)
            return True
        except AttributeError:
            raise
        except:
            return False

    def hints(self, device: str) -> Dict[str, Any]:
        return self.namespace[device].hints

    def component_names(self, device: str) -> Tuple[str, ...]:
        return self.namespace[device].component_names

    async def zmq_server_comm(self):
        """
        This function is supposed to be executed by asyncio.run() to start the manager.
        """
        self._ctx = zmq.asyncio.Context()
        self._loop = asyncio.get_running_loop()

        self._zmq_socket = self._ctx.socket(zmq.REP)
        self._zmq_socket.bind(self._zmq_ip_server)
        while True:
            msg_in = await self._zmq_socket.recv_json()
            # TODO call methods, raise if invalid
            try:
                method = msg_in["method"]
                if method == "close":
                    self._zmq_socket.close()
                    break
                params = msg_in.get("params", {})
                ret = getattr(self, method)(**params)
                self._zmq_socket.send_json({"success": True, "return": ret})
            except AttributeError:
                self._zmq_socket.send_json({"success": False, "msg": f"Unknown method '{method}'"})
            except Exception as e:
                self._zmq_socket.send_json({"success": False, "msg": repr(e)})
