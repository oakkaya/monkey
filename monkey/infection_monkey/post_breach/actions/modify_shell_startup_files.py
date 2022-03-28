import subprocess

from common.common_consts.post_breach_consts import POST_BREACH_SHELL_STARTUP_FILE_MODIFICATION
from infection_monkey.i_puppet.i_puppet import PostBreachData
from infection_monkey.post_breach.pba import PBA
from infection_monkey.post_breach.shell_startup_files.shell_startup_files_modification import (
    get_commands_to_modify_shell_startup_files,
)


class ModifyShellStartupFiles(PBA):
    """
    This PBA attempts to modify shell startup files,
    like ~/.profile, ~/.bashrc, ~/.bash_profile in linux,
    and profile.ps1 in windows.
    """

    def __init__(self):
        super().__init__(name=POST_BREACH_SHELL_STARTUP_FILE_MODIFICATION)

    def run(self):
        results = [pba.run() for pba in self.modify_shell_startup_PBA_list()]
        if not results:
            results = [
                (
                    "Modify shell startup files PBA failed: Unable to find any regular users",
                    False,
                )
            ]
        # `command` is empty here since multiple commands were run and the results
        # were aggregated to send the telemetry just once
        yield PostBreachData(self.name, "", results).send()

    def modify_shell_startup_PBA_list(self):
        return self.ShellStartupPBAGenerator().get_modify_shell_startup_pbas()

    class ShellStartupPBAGenerator:
        def get_modify_shell_startup_pbas(self):
            (cmds_for_linux, shell_startup_files_for_linux, usernames_for_linux), (
                cmds_for_windows,
                shell_startup_files_per_user_for_windows,
            ) = get_commands_to_modify_shell_startup_files()

            pbas = []

            for startup_file_per_user in shell_startup_files_per_user_for_windows:
                windows_cmds = " ".join(cmds_for_windows).format(startup_file_per_user)
                pbas.append(self.ModifyShellStartupFile(linux_cmds="", windows_cmds=windows_cmds))

            for username in usernames_for_linux:
                for shell_startup_file in shell_startup_files_for_linux:
                    linux_cmds = (
                        " ".join(cmds_for_linux).format(shell_startup_file).format(username)
                    )
                    pbas.append(self.ModifyShellStartupFile(linux_cmds=linux_cmds, windows_cmds=""))

            return pbas

        class ModifyShellStartupFile(PBA):
            def __init__(self, linux_cmds, windows_cmds):
                super().__init__(
                    name=POST_BREACH_SHELL_STARTUP_FILE_MODIFICATION,
                    linux_cmd=linux_cmds,
                    windows_cmd=windows_cmds,
                )

            def run(self):
                if self.command:
                    try:
                        output = subprocess.check_output(  # noqa: DUO116
                            self.command, stderr=subprocess.STDOUT, shell=True
                        ).decode()

                        return output, True
                    except subprocess.CalledProcessError as e:
                        # Return error output of the command
                        return e.output.decode(), False
