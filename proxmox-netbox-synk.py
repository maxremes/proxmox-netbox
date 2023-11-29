import requests
import json
from proxmoxer import ProxmoxAPI
import urllib3
import threading

# Disable SSL warnings (use with caution)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Proxmox Configuration
proxmox_host = '<host>'
proxmox_username = '<user>@pam'
proxmox_password = '<password>'
proxmox = ProxmoxAPI(proxmox_host, user=proxmox_username, password=proxmox_password, verify_ssl=False)

# Netbox Configuration
netbox_api_url = 'netboxhost'
netbox_api_token = 'api-user-key'

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

    vmid = vm_info.get('vmid')  # VM ID for both VM and LXC

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
        'disk': disk_in_gb,
        'custom_fields': {'VMID': vmid}
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
            return {**vm_config, **vm_status}
        elif type == 'lxc':
            lxc_config = proxmox.nodes(node['node']).lxc(vm_or_lxc_id).config.get()
            lxc_status = proxmox.nodes(node['node']).lxc(vm_or_lxc_id).status.current.get()
            return {**lxc_config, **lxc_status}
    except Exception as e:
        print(f"Error getting info for {type} {vm_or_lxc_id} on node {node['node']}: {e}")
        return None

def get_all_vm_names_from_netbox():
    url = netbox_api_url + 'virtualization/virtual-machines/'
    headers = {'Authorization': 'Token ' + netbox_api_token}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        vms = response.json()['results']
        return [vm['name'] for vm in vms]
    else:
        print(f"Error fetching VMs from Netbox: {response.text}")
        return []

def decommission_vm_in_netbox(vm_name):
    get_url = netbox_api_url + 'virtualization/virtual-machines/'
    headers = {
        'Authorization': 'Token ' + netbox_api_token,
        'Content-Type': 'application/json'
    }
    get_response = requests.get(get_url + '?name=' + vm_name, headers=headers)

    if get_response.status_code == 200 and get_response.json()['count'] > 0:
        vm_id = get_response.json()['results'][0]['id']
        patch_url = netbox_api_url + f'virtualization/virtual-machines/{vm_id}/'
        patch_data = {'status': 'decommissioning'}
        patch_response = requests.patch(patch_url, headers=headers, data=json.dumps(patch_data))

        if patch_response.status_code == 200:
            print(f"VM {vm_name} set to Decommissioning in Netbox.")
        else:
            print(f"Error setting VM {vm_name} to Decommissioning in Netbox: {patch_response.text}")
    else:
        print(f"VM {vm_name} not found in Netbox.")

# Parallelize VM and LXC sync
def handle_vm_or_lxc(node, vm_or_lxc_id, vm_type):
    vm_info = get_vm_or_lxc_info(node, vm_or_lxc_id, vm_type)
    if vm_info:
        update_or_create_vm_in_netbox(vm_info, vm_type)

threads = []
for node in proxmox.nodes.get():
    for vm in proxmox.nodes(node['node']).qemu.get():
        t = threading.Thread(target=handle_vm_or_lxc, args=(node, vm['vmid'], 'qemu'))
        t.start()
        threads.append(t)

    for lxc in proxmox.nodes(node['node']).lxc.get():
        t = threading.Thread(target=handle_vm_or_lxc, args=(node, lxc['vmid'], 'lxc'))
        t.start()
        threads.append(t)

for t in threads:
    t.join()

# Check and handle VMs that no longer exist in Proxmox
netbox_vm_names = get_all_vm_names_from_netbox()
proxmox_vm_lxc_names = [vm['name'] for node in proxmox.nodes.get() for vm in (proxmox.nodes(node['node']).qemu.get() + proxmox.nodes(node['node']).lxc.get())]

for vm_name in netbox_vm_names:
    if vm_name not in proxmox_vm_lxc_names:
        decommission_vm_in_netbox(vm_name)
