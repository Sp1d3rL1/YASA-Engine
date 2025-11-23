# -*- coding: utf-8 -*-

"""
Result Manager for PASA-ENGINE.

This module provides the ResultManager class, which is responsible for
collecting, storing, and formatting the findings reported by various checkers.
It ensures that findings are properly structured and can be easily converted
into formats like SARIF. This is the Python counterpart to `result-manager.js`
in the YASA-Engine.
"""

import logging
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)


class ResultManager:
    """
    Manages the collection and storage of analysis findings.
    """

    def __init__(self):
        """
        Initializes the ResultManager.
        """
        # Findings are stored in a dictionary where keys are the finding type (ruleId)
        # and values are a list of finding objects.
        self.findings = defaultdict(list)

    def add_finding(self, finding_obj):
        """
        Adds a new finding to the collection.

        Args:
            finding_obj: A dictionary or object representing the finding.
                         It must contain a 'type' key.
        """
        finding_type = finding_obj.get("type")
        if not finding_type:
            logger.warning("Attempted to add a finding without a 'type'.")
            return

        if self.is_new_finding(finding_obj):
            finding_obj["id"] = str(uuid.uuid4())
            self.findings[finding_type].append(finding_obj)
            logger.debug(f"New finding of type '{finding_type}' added.")
        else:
            logger.debug(f"Duplicate finding of type '{finding_type}' ignored.")

    def is_new_finding(self, new_finding):
        """
        Checks if a finding is a duplicate of an existing one.

        Args:
            new_finding: The new finding to check.

        Returns:
            True if the finding is new, False otherwise.
        """
        # TODO: Implement a more sophisticated duplication check based on
        # location, trace, and other relevant fields, similar to YASA.
        # For now, we perform a basic check.
        finding_type = new_finding.get("type")
        if finding_type in self.findings:
            for existing_finding in self.findings[finding_type]:
                # Simple check: same type, same line number, same file
                if (existing_finding.get("line") == new_finding.get("line") and
                        existing_finding.get("sourcefile") == new_finding.get("sourcefile")):
                    return False
        return True

    def get_findings(self):
        """
        Returns all collected findings.
        """
        return self.findings

    def get_sarif_format(self):
        """
        Converts all findings into the SARIF format.
        """
        # TODO: Implement the conversion to SARIF format.
        logger.info("Converting findings to SARIF format (not yet implemented).")
        # This will involve iterating through self.findings and building the
        # structure required by the SARIF standard.
        return {
            "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {"driver": {"name": "PASA-ENGINE"}},
                    "results": []
                }
            ]
        }