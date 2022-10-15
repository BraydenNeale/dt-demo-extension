# General
* Enable EEC for the OneAgents (globally or per host): https://www.dynatrace.com/support/help/shortlink/extensions-concepts#eec
* Generate an API token from your Dynatrace tenant: Managed -> Access Tokens
    * API v2 scopes: Ingest metrics, Read settings, Write settings
* Extension Framework 1 (EF1) docs: https://www.dynatrace.com/support/help/shortlink/extensions-hub
* Extension Framework 2 (EF2) docs: https://www.dynatrace.com/support/help/shortlink/extensions20
* A good guide for EF2 extensions (SNMP) is available at: https://github.com/arunkrishnan-dt/dynatrace_snmp_2.0

# EF1 - Python3.8
* `py -3.8 -m venv .venv`
* `.\.venv\Scripts\activate`
* Download oneagent sdk from your Dynatrace tenant
    * settings -> monitored technologies -> add new technology monitoring -> build oneagent extension -> download SDK
* `pip install ...extensions\lib\plugin-sdk-1.253.89.20221014-161029\plugin_sdk-1.253.89.20221014.161029-py3-none-any.whl`
* `pip install requests==2.28.1`
* `oneagent_sim -p ef1`
* `oneagent_build_plugin -p ef1 -d dist/ef1 --no_upload`
* Upload your extension zip file to the Dynatrace tenant and add it to the plugin module path on each Agent/ActiveGate
    * https://www.dynatrace.com/support/help/shortlink/deploy-custom-extension

# EF2 - Metadata
### Setup
* Install the `dt-cli`: https://github.com/dynatrace-oss/dt-cli
    * pip install dt-cli
* `$Env:DTCLI_API_TOKEN="dt0c01..."`
* `$Env:DT_TENANT="https://ENV.dynatrace.com"`
* Set up extension Schema validation. e.g. v1.249
    * `dt extension schemas 1.249.0 --tenant-url $Env:DT_TENANT`
    * VSCODE: Install Redhat YAML VSCode extension.
        * Then go to -> Settings workspace, yaml schemas and add:
        *   ```
            "yaml.schemas": {
                "C:\\Users\\...\\EF2\\schemas\\1.245.0\\extension.schema.json": "extension.yaml",
            },
            ```

### Certs
* `dt extension gencerts --no-ca-passphrase --no-dev-passphrase`
* Extension are signed with `developer.pem` and validated against `ca.pem`
* Upload ca.pem to the Dynatrace credential vault: Managed - Credential Vault
*   Also upload ca.pem to each oneagent/activegate the extension will run from
*   https://www.dynatrace.com/support/help/shortlink/sign-extension#upload

### Build and Deploy
* `dt extension assemble --src=src -o dist/extension.zip --force`
* `dt extension sign --src=dist/extension.zip -o dist/bundle.zip --key <path_to_keys>/developer.pem --force`
* `dt extension validate --tenant-url $Env:DT_TENANT --api-token $Env:DTCLI_API_TOKEN dist/bundle.zip`
* Manually upload to the UI
    * or (note: known issue for first build): `dt extension upload --tenant-url $Env:DT_TENANT --api-token $Env:DTCLI_API_TOKEN dist/bundle.zip`
* Configure your extenson from the extension UI under: Infrastruture -> Extensions -> Managed and upload

