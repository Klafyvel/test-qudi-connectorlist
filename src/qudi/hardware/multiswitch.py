from qudi.interface.switch_interface import SwitchInterface
from qudi.core.configoption import ConfigOption
from qudi.core.connector import ConnectorList

class MultiSwitch(SwitchInterface):
    switches = ConnectorList(interface="SwitchInterface")
    _hardware_name = ConfigOption(name='name', default=None, missing='nothing')
    _extend_hardware_name = ConfigOption(name='extend_hardware_name',
                                         default=False,
                                         missing='nothing')
    def on_activate(self):
        """ Activate the module and fill status variables.
        """
        self.log.debug(f"Activating with {len(self.switches)} switches.")
        if self._hardware_name is None:
            self._hardware_name = self.module_name

    def on_deactivate(self):
        """ Deactivate the module and clean up.
        """
        pass

    @property
    def name(self):
        """ Name of the hardware as string.

        @return str: The name of the hardware
        """
        return self._hardware_name

    @property
    def available_states(self):
        """ Names of the states as a dict of tuples.

        The keys contain the names for each of the switches. The values are tuples of strings
        representing the ordered names of available states for each switch.

        @return dict: Available states per switch in the form {"switch": ("state1", "state2")}
        """
        new_dict = dict()
        if self._extend_hardware_name:
            for switchinstance in self.switches:
                new_dict.update({
                    f'{switchinstance.name}.{switch}': states
                    for switch, states in switchinstance.available_states.items()
                })
        else:
            for switchinstance in self.switches:
                new_dict.update(switchinstance.available_states)
        return new_dict

    @property
    def number_of_switches(self):
        """ Number of switches provided by the hardware.

        @return int: number of switches
        """
        return sum(switch.number_of_switches for switch in self.switches)

    @property
    def switch_names(self):
        """ Names of all available switches as tuple.

        @return str[]: Tuple of strings of available switch names.
        """
        return tuple(self.available_states)

    @property
    def states(self):
        """ The current states the hardware is in as state dictionary with switch names as keys and
        state names as values.

        @return dict: All the current states of the switches in the form {"switch": "state"}
        """
        new_dict = dict()
        if self._extend_hardware_name:
            for switchinstance in self.switches:
                hw_name = switchinstance.name
                new_dict.update({
                    f'{hw_name}.{switch}': states
                    for switch, states in switchinstance.states.items()
                })
        else:
            for switchinstance in self.switches:
                new_dict.update(switchinstance.states)
        return new_dict

    @states.setter
    def states(self, state_dict):
        """ The setter for the states of the hardware.

        The states of the system can be set by specifying a dict that has the switch names as keys
        and the names of the states as values.

        @param dict state_dict: state dict of the form {"switch": "state"}
        """
        assert isinstance(state_dict,
                          dict), f'Property "state" must be dict type. Received: {type(state_dict)}'
        for switch, state in state_dict.items():
            switchname = ""
            hardware = None
            for hw in self.switches:
                if self._extend_hardware_name and switch.startswith(hw.name):
                    hardware = hw
                    switchname = switch[len(hw.name) + 1:]
                    break
                elif switch in hw.available_states:
                    hardware = hw
                    switchname = switch
                    break
            hardware.set_state(switchname, state)

    def get_state(self, switch):
        """ Query state of single switch by name

        @param str switch: name of the switch to query the state for
        @return str: The current switch state
        """
        assert switch in self.available_states, f'Invalid switch name: "{switch}"'
        for hw in self.switches:
            if self._extend_hardware_name and switch.startswith(hw.name):
                return hw.get_state(switch[len(hw.name) + 1:])
            elif switch in hw.available_states:
                return hw.get_state(switch)

    def set_state(self, switch, state):
        """ Query state of single switch by name

        @param str switch: name of the switch to change
        @param str state: name of the state to set
        """
        for hw in self.switches:
            if self._extend_hardware_name and switch.startswith(hw.name):
                return hw.set_state(switch[len(hw.name) + 1:], state)
            elif switch in hw.available_states:
                return hw.get_state(switch, state)
