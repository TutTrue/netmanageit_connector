import os
from pathlib import Path

import yaml
from pycti import get_config_variable
from dotenv import load_dotenv


class Config:
    def __init__(self):
        """
        Initialize the connector with necessary configurations
        """

        self.load = self._load_config()
        self._initialize_configurations()

    @staticmethod
    def _load_config() -> dict:
        """
        Load the configuration from the YAML file
        :return: Configuration dictionary
        """
        parent_dir = Path(__file__).parents[2]
        config_file_path = parent_dir.joinpath("config.yml")
        print(f"Loading .env from the following path :::: {parent_dir} ")
        load_dotenv(parent_dir.joinpath(".env"))
        config = (
            yaml.load(open(config_file_path), Loader=yaml.FullLoader)
            if os.path.isfile(config_file_path)
            else {}
        )

        return config

    def _initialize_configurations(self) -> None:
        """
        Connector configuration variables
        :return: None
        """
        # OpenCTI configurations
        self.duration_period = get_config_variable(
            "CONNECTOR_DURATION_PERIOD",
            ["connector", "duration_period"],
            self.load,
        )

        # Connector extra parameters
        self.api_base_url = get_config_variable(
            "GITHUB_API_BASE_URL",
            ["github", "api_base_url"],
            self.load,
        )

        self.github_token = get_config_variable(
            "GITHUB_TOKEN",
            ["github", "github_token"],
            self.load,
        )

        # OpenCTI NetManageIT configurations
        self.netmanageit_url = get_config_variable(
            "OPENCTI_NETMANAGEIT_URL",
            ["opencti_netmanageit", "url"],
            self.load,
        )

        self.netmanageit_token = get_config_variable(
            "OPENCTI_NETMANAGEIT_TOKEN",
            ["opencti_netmanageit", "token"],
            self.load,
        )

        # Connector behavior flags
        process_observables_raw = get_config_variable(
            "PROCESS_OBSERVABLES",
            ["connector_flags", "process_observables"],
            self.load,
            default="true",
        )
        # Handle both string values and boolean values
        if isinstance(process_observables_raw, bool):
            self.process_observables = process_observables_raw
        else:
            self.process_observables = str(process_observables_raw).lower() in ('true', '1', 'yes', 'on')

        process_indicators_raw = get_config_variable(
            "PROCESS_INDICATORS",
            ["connector_flags", "process_indicators"],
            self.load,
            default="true",
        )
        # Handle both string values and boolean values
        if isinstance(process_indicators_raw, bool):
            self.process_indicators = process_indicators_raw
        else:
            self.process_indicators = str(process_indicators_raw).lower() in ('true', '1', 'yes', 'on')
