# cisco-sdwan-python

## Using this repo directly
```bash
git clone https://github.com/CiscoDevNet/cisco-sdwan-python.git
cd cisco-sdwan-python
python3 -m venv env
. env/bin/activate
pip install -e .
```

## vManage Command Line Interface

Vmanage host and credentials can be specified via environment variables,
command line options, or a combination of the two:

### Environment Variables

* `VMANAGE_HOST`
* `VMANAGE_USER`
* `VMANAGE_PASSWORD`

### Command Line Options

```bash
$ vmanage --help
Usage: vmanage [OPTIONS] COMMAND [ARGS]...

Options:
  --host TEXT      vManage Host (env: VMANAGE_HOST)  [required]
  --user TEXT      vManage Username (env: VMANAGE_USER)  [required]
  --password TEXT  vManage Password (env: VMANAGE_PASSWORD)  [required]
  --help           Show this message and exit.

Commands:
  export  Export commands
  import  Import commands
  show    Show commands
```

>Note: If no password is specified, the user will be prompted for one.

### Exporting Templates

```bash
vmanage export templates --file vmanage-templates.json
```

#### To specify/override the host:

```bash
vmanage --host=192.133.178.54 export templates --file vmanage-templates.json
```

### Import Templates

```bash
vmanage import templates --file vmanage-templates.json
```

### Exporting Policy

```bash
vmanage export policy --file vmanage-policy.json
```

### Import Policy

```bash
vmanage import policy --file vmanage-policy.json
```