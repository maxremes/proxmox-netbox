import requests
import json
from proxmoxer import ProxmoxAPI
import urllib3

# Disable SSL warnings (use with caution)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Proxmox configuration
proxmox_host = 'proxmox_host'
username = 'username'
password = 'password'
proxmox = ProxmoxAPI(proxmox_host, user=username, password=password, verify_ssl=False)

# Netbox configuration
netbox_api_url = 'netbox_api_url'
netbox_api_token = 'netbox_api_token'

def update_or_create_vm_in_netbox(vm_info, vm_type):
    url = netbox_api_url + 'virtualization/virtual-machines/'
    headers = {'Authorization': 'Token ' + netbox_api_token, 'Content-Type': 'application/json'}

    status = 'active' if vm_info.get('status') == 'running' else 'offline'
    role_id = 1 if vm_type == 'qemu' else 5  # ID for 'virtual-machine' and 'lxc'

    disk_in_gb = 0
    if vm_type == 'lxc':
        disk_size_str = vm_info.get('rootfs', '').split(',')[1] if 'rootfs' in vm_info and ',' in vm_info['rootfs'] else ''
        disk_in_gb = int(disk_size_str.replace('size=', '').replace('G', '')) if 'size=' in disk_size_str else 0
    else:
        disk_in_gb = min(vm_info.get('maxdisk', 0) / (1024 ** 3), 2147483647)

    data = {
        'name': vm_info['name'],
        'status': status,
        'site': 1,
        'cluster': 1,
        'platform': 1,
        'role': role_id,
        'tenant': 1,
        'vcpus': vm_info.get('cores'),
        'memory': vm_info.get('memory'),
        'disk': disk_in_gb
    }

    response = requests.get(url + '?name=' + vm_info['name'], headers=headers)
    if response.status_code == 200 and response.json()['count'] > 0:
        vm_id = response.json()['results'][0]['id']
        put_response = requests.put(url + str(vm_id) + '/', headers=headers, data=json.dumps(data))
        print(f"Updating {vm_type} {vm_info['name']}: Status {put_response.status_code}, Response: {put_response.text}")
    else:
        post_response = requests.post(url, headers=headers, data=json.dumps(data))
        print(f"Creating {vm_type} {vm_info['name']}: Status {post_response.status_code}, Response: {post_response.text}")

def get_vm_or_lxc_info(node, vm_or_lxc_id, type='qemu'):
    try:
        if type == 'qemu':
            vm_config = proxmox.nodes(node['node']).qemu(vm_or_lxc_id).config.get()
            vm_status = proxmox.nodes(node['node']).qemu(vm_or_lxc_id).status.current.get()
            return {**vm_config, **vm_status}  # Combine config and status data for VM
        elif type == 'lxc':
            lxc_config = proxmox.nodes(node['node']).lxc(vm_or_lxc_id).config.get()
            lxc_status = proxmox.nodes(node['node']).lxc(vm_or_lxc_id).status.current.get()
            return {**lxc_config, **lxc_status}  # Combine config and status data for LXC
    except Exception as e:
        print(f"Error getting info for {type} {vm_or_lxc_id} on node {node['node']}: {e}")
        return None

# Fetch list of VMs and LXCs from Proxmox
for node in proxmox.nodes.get():
    for vm in proxmox.nodes(node['node']).qemu.get():
        vm_info = get_vm_or_lxc_info(node, vm['vmid'], 'qemu')
        if vm_info:
            update_or_create_vm_in_netbox(vm_info, 'qemu')

    for lxc in proxmox.nodes(node['node']).lxc.get():
        lxc_info = get_vm_or_lxc_info(node, lxc['vmid'], 'lxc')
        if lxc_info:
            update_or_create_vm_in_netbox(lxc_info, 'lxc')
