from pytest import fixture  # type: ignore


@fixture
def initial_add_device(scope="function") -> str:
    # Device, self signed, first entry so hash is all 0s

    return (
        "dUJoqn66lPaov7Rn0Vgjtv8M3ZGtZckUrW3MLms9em4cmKxleZ3AQSkw1ZtvMAW93v3J175k0Yao68dtkZSVAXsic3RhdGVtZW50Ijogey"
        "JkZXZpY2VfaWQiOiAiIiwgImtpbmQiOiAidGVzdCIsICJuYW1lIjogInRlc3QgZm9yIGJhZCBzaWduYXR1cmUiLCAia2lkIjogIjkxMWNm"
        "ZjVmOTFiZjU2NWQ3YzAxZDJlMDNlNTc5YTc1N2VjNGU4N2IxNTRjMzRmOWYwOWE3ZDllOTJiYzMzZTYiLCAic3RhdGVtZW50X3R5cGUiOi"
        "Aic2VsZi1zaWduZWQtZGV2aWNlIn0sICJhdXRob3JpdHkiOiB7ImtpZCI6ICI5MTFjZmY1ZjkxYmY1NjVkN2MwMWQyZTAzZTU3OWE3NTdl"
        "YzRlODdiMTU0YzM0ZjlmMDlhN2Q5ZTkyYmMzM2U2IiwgInVzZXJuYW1lIjogInRlc3QifSwgInByZXYiOiAiMDAwMDAwMDAwMDAwMDAwMD"
        "AwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMCIsICJzZXEiOiAwfQ=="
    )
