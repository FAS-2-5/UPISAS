from UPISAS.exemplar import Exemplar


class RAMSES(Exemplar):
    """Runs the challenge scenario against RAMSES through the interface on port 50000."""

    def __init__(self, auto_start=False):
        docker_config = {
            "name": "simulation-scenario",
            "image": "giamburrasca/scenario1:amd64",
            "network": "ramses-sas-net",
            "environment": {
                "ADAPT": "0",
                "FAILURE_INJECTION_1_START": "120",
                "JAVA_TOOL_OPTIONS": "-XX:-UseContainerSupport",
            },
        }
        super().__init__("http://localhost:50000", docker_config, auto_start)

    def start_run(self):
        self.start_container()
