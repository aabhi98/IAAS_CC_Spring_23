class AppTierProperties:
    REQUEST_SQS = "RequestQueue"
    RESPONSE_SQS = "ResponseQueue"

    REQUEST_S3 = "openstack-request"
    RESPONSE_S3 = "openstack-response"

    @property
    def aws_credentials(self):
        return {
            "access_key": "AKIA3M3MWZLDWSZAKT4J",
            "secret_key": "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"
        }
