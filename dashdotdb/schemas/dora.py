
def dora_schema():
    return {
        "type": "object",
        "properties": {
            "deployments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "trigger_reason": {
                            "type": "string",
                            # TODO: Maybe relax pattern?
                            "pattern": r'https://gitlab\.cee\.redhat\.com/service/.*/commit/.*'
                            },
                        "finish_timestamp": {
                            "type": "string",
                            # RFC 3339, optional 'T' separator
                            "pattern": r'^((?:(\d{4}-\d{2}-\d{2})(T| )(\d{2}:\d{2}:\d{2}(?:\.\d+)?))(Z|[\+-]\d{2}:\d{2})?)$'
                            },
                        "app_name": {"type": "string"},
                        "env_name": {"type": "string"},
                        "pipeline": {"type": "string"},
                        "commits": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "revision": {
                                        "type": "string",
                                        "pattern": r'[a-f0-9]{40}',
                                        },
                                    "timestamp": {
                                        "type": "string",
                                        "pattern": r'^((?:(\d{4}-\d{2}-\d{2})(T| )(\d{2}:\d{2}:\d{2}(?:\.\d+)?))(Z|[\+-]\d{2}:\d{2})?)$'
                                        },
                                    "repo": {
                                        "type": "string",
                                        # TODO: Maybe relax pattern?
                                        "pattern": r'https://git.*\.com/.*/.*',
                                        },
                                    "lttc": { "type": "integer" },
                                    }
                                }
                            },
                        }
                    },
                }
            }
        }
