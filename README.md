# EF1 - Python3.8
* `py -3.8 -m venv .venv`
* `.\.venv\Scripts\activate`
* Download oneagent sdk from your Dynatrace tenant
    * settings -> monitored technologies -> add new technology monitoring -> build oneagent extension -> download SDK
* `pip install C:\Users\Brayden.Neale\Dev\extensions\lib\plugin-sdk-1.253.89.20221014-161029\plugin_sdk-1.253.89.20221014.161029-py3-none-any.whl`
* `pip install requests==2.28.1`
* `oneagent_sim`
* `oneagent_build_plugin -p ef1 -d dist --no-upload`

# EF2 - Metadata