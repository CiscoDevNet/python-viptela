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
* `VMANAGE_USERNAME`
* `VMANAGE_PASSWORD`

### Command Line Options

```bash
$ vmanage --help
Usage: vmanage [OPTIONS] COMMAND [ARGS]...

Options:
  --host TEXT      vManage Host (env: VMANAGE_HOST)  [required]
  --username TEXT      vManage Username (env: VMANAGE_USERNAME)  [required]
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

#### Options

* `--check`: Just check. No changes. (default=False)
* `--update`: Update if exists (default=False)
* `--diff`: Show diffs (default=False)

```bash
vmanage import templates --file vmanage-templates.json
```

### Exporting Policy

```bash
vmanage export policy --file vmanage-policy.json
```

### Import Policy

#### Options

* `--check`: Just check. No changes. (default=False)
* `--update`: Update if exists (default=False)
* `--diff`: Show diffs (default=False)

```bash
vmanage import policy --file vmanage-policy.json
```

### Show Information

#### Commands:

* control - Show control information
  * connections
  * connections-history
* device - Show device information
  * config
  * status
* omp - Show OMP information
  * peers
* policy - Show policy information
  * central
  * local
  * definition
  * list
* template - Show template information

#### Examples

##### Diff two templates:

```
vmanage show template g0/0/0-R1 --diff g0/0/0-R2
[ ( 'change',
    'templateDefinition.tunnel-interface.color.value.vipType',
    ('ignore', 'constant')),
  ( 'change',
    'templateDefinition.tunnel-interface.color.value.vipValue',
    ('default', 'custom2')),
  ( 'add',
    'templateDefinition.tunnel-interface.color.restrict',
    [('vipVariableName', 'vpn_if_tunnel_color_restrict')]),
  ( 'change',
    'templateId',
    ( '2a0481f4-a5b2-44bf-baad-59de4d3b4e99',
      '1dc123db-7a14-40f5-9653-1c87ccd5eaa2')),
  ('change', 'createdOn', (1569072320921, 1569072320260)),
  ('change', '@rid', (843, 839)),
  ( 'change',
    'templateDescription',
    ( 'G0/0/0 Interface for R1 router with TLOC extension, adds NAT',
      'G0/0/0 Interface for R2 router with TLOC extension, adds NAT, changes '
      'color to custom2')),
  ('change', 'lastUpdatedOn', (1569072320921, 1569072320260))]
```