# ansible-viptela

An Ansible Role for automating a Viptela Overlay Network.  This is a hybrid role that provided both role tasks and
modules.

This role can perform the following functions:
- Add Controllers
- Set Organization Name
- Set vBond
- Set Enterprise Root CA
- Get Controller CSR
- Install Controller Certificate
- Install Serial File
- Export Templates
- Import Templates
- Add/Change/Delete Templates
- Attach Templates
- Export Policy
- Import Policy
- Add/Change/Delete Policy
- Activate Policy
- Get Template facts
- Get Device facts


#### Common Attributes
* `host`: IP address or FQDN of vManage
* `user`: Username used to log in to vManage
* `password`: Password used to log into vManage

### Set vManage Setting

```yaml
  - name: vManage Settings
    vmanage_settings:
      host: "{{ vmanage_ip }}"
      user: "{{ vmanage_user }}"
      password: "{{ vmanage_password }}"
      organization: "{{ organization_name }}"
      vbond: 1.2.3.4
      ca_type: enterprise
      root_cert: "{{lookup('file', '{{ viptela_cert_dir }}/myCA.pem')}}"
```

#### Arguments:
* `organization`: Organization name
* `vbond`: vBond
* `vbond_port`: vBond port
* `ca_type`: CA type
* `root_cert`: CA root certificate

### Add device

```yaml
- vmanage_device:
    host: "{{ vmanage_ip }}"
    user: "{{ vmanage_user }}"
    password: "{{ vmanage_pass }}"
    device_username: admin
    device_password: admin
    name: "{{ item }}"
    personality: "{{ hostvars[item].viptela.personality }}"
    system_ip: "{{ hostvars[item].viptela.transport_ip }}"
```

#### Arguments:
* `device_username`: Username of the device being added
* `device_password`: Password of the user specified
* `name`: Name of the device being added
* `system_ip`: The System IP of the device
* `personality`: Personality of the device
* `state`: `present` or `absent` (default: `present`)

### Generate device CSR

```yaml
- name: vmanage_device_certificate:
    host: "{{ vmanage_ip }}"
    user: "{{ vmanage_user }}"
    password: "{{ vmanage_pass }}"
    name: "{{ item }}"
    system_ip: "{{ hostvars[item].viptela.transport_ip }}"
    state: csr
  register: control_devices
```

#### Arguments:

* `name`: Name of the device being added (required for `present` and `csr`)
* `system_ip`: The System IP of the device
* `cert`: The certificate to install when state is `present`
* `state`:
  * `present`: Add certificate vmanage
  * `csr`: Generate CSR (CSR passed in results)
  * `push`: Push certificates to controllers

### Get device bootstrap information

```yaml
- vmanage_device_bootstrap:
    host: "{{ vmanage_ip }}"
    user: "{{ vmanage_user }}"
    password: "{{ vmanage_pass }}"
    uuid: "{{ viptela.uuid }}"
  register: result
```

#### Arguments:

* `uuid`: UUID of the device


### Get Device Template Facts
```yaml
- vmanage_device_template_facts:
    user: "{{ ansible_user }}"
    host: "{{ vmanage_ip }}"
    password: "{{ ansible_password }}"
    factory_default: no
```

Retrieves device template facts from vManange

#### Arguments:
* `factory_default`: Include factory default templates

#### Returns:
* `device_templates`: The device templates defined in vManage
* `attached_devices`: The devices current attached to the template
* `input`: Variables required by template

### Feature Template Facts:
```yaml
- vmanage_feature_template_facts:
    user: "{{ ansible_user }}"
    host: "{{ vmanage_ip }}"
    password: "{{ ansible_password }}"
    factory_default: no
```

Retrieves feature template facts from vManange

#### Arguments:
* `factory_default`: Include factory default templates

#### Returns:
* `feature_templates`: The feature templates defined in vManage

### Feature template operations
```yaml
- vmanage_feature_template:
    user: "{{ ansible_user }}"
    host: "{{ vmanage_ip }}"
    password: "{{ ansible_password }}"
    state: present
    aggregate: "{{ vmanage_templates.feature_templates }}"
```

Create or delete a feature template

#### Arguments
 * `name`: Name of the feature template
 * `description`: Description of the feature template
 * `definition`: Feature template definition
 * `type`: Type of feature temaplate
 * `device_type`: Device type to which the the template can be applied
 * `template_min_version`: Minimum version of vManage required for template
 * `factory_default`: Factory default template
 * `aggregate`: A list of items composed of the arguments above

### Device template operations
```yaml
- vmanage_device_template:
    user: "{{ ansible_user }}"
    host: "{{ vmanage_ip }}"
    password: "{{ ansible_password }}"
    state: present
    aggregate: "{{ vmanage_templates.device_templates }}"
```

Create or delete a device template

#### Arguments
 * `name`: Name of the device template
 * `description`: Description of the device template
 * `templates`: Feature templates includes in the device template
 * `config_type`: Template type: `template` or `cli`
 * `device_type`: Device type to which the the template can be applied
 * `template_min_version`: Minimum version of vManage required for template
 * `factory_default`: Factory default template
 * `aggregate`: A list of items composed of the arguments above

### Attach template to device:
```yaml
- vmanage_device_attachment:
    user: "{{ ansible_user }}"
    host: "{{ vmanage_ip }}"
    password: "{{ ansible_password }}"
    device: site1-vedge1
    template: colo_vedge
    variables:
      vpn11_ipv4_address: 172.22.2.1/24
      vpn10_ipv4_address: 172.22.1.1/24
      vpn0_internet_ipv4_address: 172.16.22.2/24
      vpn0_default_gateway: 172.16.22.1
    wait: yes
    state: "{{ state }}"
```

Attach/Detach template to/from device

#### Arguments:
* `state`: The state of the attachment: `absent` or `present`
* `device`: The name of the device to which
* `template`: The name of the template to apply
* `variables`: The variable required by the template.  (See vmanage_device_template_facts for required variables)
* `wait`: Wait for the application of the template to succeed or fail.

### Policy Lists
```yaml
- vmanage_policy_list:
    user: "{{ ansible_user }}"
    host: "{{ vmanage_ip }}"
    password: "{{ ansible_password }}"
    name: blocked_prefixes
    description: Blocked Prefixes
    type: dataPrefix
    entries:
      - ipPrefix: 10.0.1.0/24
      - ipPrefix: 10.0.2.0/24
      - ipPrefix: 10.0.3.0/24
    state: present
    aggregate: "{{ item.value }}"
```

#### Arguments:
* `name`: Policy List name
* `description`: Policy List description
* `type`: Policy List type
* `entries`: The list entries appropriate to the type
* `state`: absent or present
* `aggregate`: A list of items composed of the arguments above

### Policy List Facts:
```yaml
- vmanage_policy_list_facts:
    user: "{{ ansible_user }}"
    host: "{{ vmanage_ip }}"
    password: "{{ ansible_password }}"
  register: policy_list_facts
```

Retrieve policy list facts

#### Returns:
* `policy_lists`: The policy lists currently defined in vManage

### Policy definition
```yaml
- vmanage_policy_definition:
    user: "{{ ansible_user }}"
    host: "{{ vmanage_ip }}"
    password: "{{ ansible_password }}"
    type: "{{ item.key }}"
    state: present
    aggregate: "{{ item.value }}"
```

#### Arguments:
* `state`: absent or present
* `name`: Policy List name
* `description`: Policy List description
* `type`: Policy List type (`cflowd`, `dnssecurity`, `control`, `hubandspoke`, `acl`, `vpnmembershipgroup`, `mesh`, `rewriterule`, `data`,`rewriterule`, `aclv6`)
* `sequences`: Policy definition sequences
* `default_action`: Default policy action (e.g. `drop`)
* `aggregate`: A list of items composed of the arguments above

### Policy Definition Facts:
```yaml
- vmanage_policy_definition_facts:
    user: "{{ ansible_user }}"
    host: "{{ vmanage_ip }}"
    password: "{{ ansible_password }}"
  register: policy_definition_facts
```

Retrieve policy definition facts

#### Returns:
* `policy_definitions`: The policy definitions currently defined in vManage

### Central Policy
#### Add Central Policy
```yaml
- vmanage_central_policy:
    user: "{{ ansible_user }}"
    host: "{{ vmanage_ip }}"
    password: "{{ ansible_password }}"
    state: present
    aggregate: "{{ vmanage_policy.vmanage_central_policies }}"
```

#### Activate Central Policy
```yaml
- vmanage_central_policy:
    user: "{{ ansible_user }}"
    host: "{{ vmanage_ip }}"
    password: "{{ ansible_password }}"
    state: activated
    name: central_policy
    wait: yes
  register: policy_facts
```

#### Arguments:
* `state`: State (`absent`, `present`, `activated`, `deactivated`)
>Note: `activated`, `deactivated` must be separate invocations of the module
* `name`: Central Policy name
* `description`: Central Policy description
* `type`: Policy type
* `definition`: Policy definition
* `wait`: Wait for the application of the template to succeed or fail.

### Central Policy Facts:
```yaml
- vmanage_central_policy_facts:
    user: "{{ ansible_user }}"
    host: "{{ vmanage_ip }}"
    password: "{{ ansible_password }}"
  register: central_policy_facts
```

Retrieve policy definition facts

#### Returns:
* `policy_definitions`: The policy definitions currently defined in vManage


### Get status of a device action:
```yaml
- vmanage_device_action_status:
    user: "{{ ansible_user }}"
    host: "{{ vmanage_ip }}"
    password: "{{ ansible_password }}"
    id: "{{ attachment_results.action_id }}"
```

Retrieve status of device action


### Get device facts:
```yaml
- vmanage_device_facts:
    user: "{{ ansible_user }}"
    host: "{{ ansible_host }}"
    password: "{{ ansible_password }}"
```

Retrieve device facts

### Upload serial number file:
```yaml
- vmanage_fileupload:
    host: "{{ vmanage_ip }}"
    user: "{{ ansible_user }}"
    password: "{{ ansible_password }}"
    file: 'licenses/serialFile.viptela'
```

#### Arguments:
* `file`: name of the serial file

### Ping from vEdge
```yaml
- vmanage_nping:
    user: "{{ ansible_user }}"
    host: "{{ vmanage_ip }}"
    password: "{{ ansible_password }}"
    dst_ip: 1.2.3.4
    vedge: site1-vedge1
    vpn: 10
```

#### Arguments:
* `vedge`: Name of the vedge from which to ping
* `dst_ip`: The IP to ping
* `vpn`: The VPN number in which to ping
* `src_interface`: The source interface on the vedge from which to ping
* `count`: The number of packets to send
* `rapid`: Whether to do a rapid ping

## License

CISCO SAMPLE CODE LICENSE
