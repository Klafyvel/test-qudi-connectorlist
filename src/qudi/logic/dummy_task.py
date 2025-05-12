from qudi.core.scripting.moduletask import ModuleTask
from qudi.core.connector import ConnectorList

class DummyTask(ModuleTask):
    switches = ConnectorList(interface="SwitchInterface")

    def _run(self) -> None:
        for switch in self.switches:
            available = switch.available_states
            n = list(available.keys())[0]
            s = list(available[n])[-1]
            switch.set_state(n, s)

