#! /usr/bin/env python3
import json
import click
import ipaddress
#import sys
#from collections import defaultdict
#from getpass import getpass

def fc(flexPod):

    fiAChildren =[]
    fiBChildren =[]
    FIA={}
    objectTemp = flexPod['objects']
    wwnnObject = {}
    poolChildren = []

    #convert to Native FC ports
    ports = input('# of ports to be converted to FC ports ')
    if ports:
        ports = int(ports)
        if ports <= 6:
            ports = 6
        elif ports <= 12:
            ports = 12
        elif ports <= 18:
            ports = 18
        elif ports <= 24:
            ports = 24
        elif ports <= 30:
            ports = 30
        elif ports <= 36:
            ports = 36
        elif ports <= 42:
            ports = 42
        elif ports <= 48:
            ports = 48
        FIA ={"module":"ucsmsdk.mometa.fabric.FabricFcSan","class": "FabricFcSan","properties": {"parent_mo_or_dn": "fabric/san","id": "A"},"message": "Configure UP Ports on FI-A","children": []}
        FIB ={"module":"ucsmsdk.mometa.fabric.FabricFcSan","class": "FabricFcSan","properties": {"parent_mo_or_dn": "fabric/san","id": "B"},"message": "Configure UP Ports on FI-B","children": []}
        for i  in range(1, ports + 1):
            message = 'Configure 1/' + str(i) + ' as FC port'
            fiAChildren.append({"module": "ucsmsdk.mometa.fabric.FabricFcSanEp", "class": "FabricFcSanEp","properties": {"slot_id":  str(i)},"message":  message})
            fiBChildren.append({"module": "ucsmsdk.mometa.fabric.FabricFcSanEp", "class": "FabricFcSanEp","properties": {"slot_id":  str(i)},"message":  message})
        FIA["children"]=fiAChildren
        FIB["children"]=fiBChildren

        objectTemp.append(FIA)
        objectTemp.append(FIB)

    #Fcpools
    #WWNN
    wwnnObject = {"module":"ucsmsdk.mometa.fcpool.FcpoolInitiators","class": "FcpoolInitiators","properties": {"parent_mo_or_dn": "org-root", "name":"WWNN-Pool", "assignment_order":"sequential", "purpose":"node-wwn-assignment"},"message": "Create WWN Pool","children": []}
    poolChildren.append({"module":"ucsmsdk.mometa.fcpool.FcpoolBlock","class": "FcpoolBlock","properties": {"to":"20:00:00:25:B5:00:00:FF", "r_from":"20:00:00:25:B5:00:00:00"},"message": "Create FC PoolBloock"})
    wwnnObject["children"]= poolChildren[0]
    objectTemp.append(wwnnObject)

    #WWPN -A
    poolObject = {"module":"ucsmsdk.mometa.fcpool.FcpoolInitiators","class": "FcpoolInitiators","properties": {"parent_mo_or_dn": "org-root", "name":"WWPN-Pool-A", "assignment_order":"sequential"},"message": "Create WWPN Pool For A","children": []}
    poolChildren.append({"module":"ucsmsdk.mometa.fcpool.FcpoolBlock","class": "FcpoolBlock","properties": {"to":"20:00:00:25:B5:00:0A:FF", "r_from":"20:00:00:25:B5:00:0A:00"},"message": "Create WWPN PoolBloock"})
    poolObject["children"]= poolChildren[1]
    objectTemp.append(poolObject)

    #WWPN -B
    poolObject = {"module":"ucsmsdk.mometa.fcpool.FcpoolInitiators","class": "FcpoolInitiators","properties": {"parent_mo_or_dn": "org-root", "name":"WWPN-Pool-B", "assignment_order":"sequential"},"message": "Create WWPN Pool For B","children": []}
    poolChildren.append({"module":"ucsmsdk.mometa.fcpool.FcpoolBlock","class": "FcpoolBlock","properties": {"to":"20:00:00:25:B5:00:0B:FF", "r_from":"20:00:00:25:B5:00:0B:00"},"message": "Create WWPN PoolBloock"})
    poolObject["children"]= poolChildren[2]
    objectTemp.append(poolObject)

    #VSAN
    vsanObject = {}
    vsanAChildren = []
    vsanBChildren = []
    PcPort = []

    vsanA = input("Enter the VSAN ID for A?: ")
    vsanB = input("Enter the VSAN ID for B?: ")


    if vsanA:
        vsanObject = {"module": "ucsmsdk.mometa.fabric.FabricVsan","class": "FabricVsan","properties": {"parent_mo_or_dn":"fabric/san/A", "name":"VSAN-A", "fcoe_vlan": str(vsanA), "policy_owner":"local", "fc_zone_sharing_mode":"coalesce", "zoning_state":"disabled", "id": str(vsanA)},"message": "Create VSAN on A"}
        objectTemp.append(vsanObject)

    if vsanB:
        vsanObject = {"module": "ucsmsdk.mometa.fabric.FabricVsan","class": "FabricVsan","properties": {"parent_mo_or_dn":"fabric/san/B", "name":"VSAN-B", "fcoe_vlan": str(vsanB), "policy_owner":"local", "fc_zone_sharing_mode":"coalesce", "zoning_state":"disabled", "id": str(vsanB)},"message": "Create VSAN on B"}
        objectTemp.append(vsanObject)
        #FC POrt Channel


        #FC Port Channel
    print()
    PCBoolian = click.confirm("Are the FC uplinks using a Port Channel? ", default = True )
    if PCBoolian == True:
        FcPcName = input ("Name of Port Channel: ")
        PcIdA = input ("Port Channel ID on A: ")
        PcIdB = input ("Port Channel ID on B: ")
        while True:
            PCPortInp= input("Port in Port Channel ports? [Press Enter if done]: ")
            if PCPortInp =="":
                break
            else:
                PcPort.append(PCPortInp)

        vsanObject = {"module": "ucsmsdk.mometa.fabric.FabricFcSanPc","class": "FabricFcSanPc","properties": {"parent_mo_or_dn":"fabric/san/A", "port_id": str(PcIdA)}}
        for port in PcPort:
            vsanAChildren.append({"module": "ucsmsdk.mometa.fabric.FabricFcSanPcEp","class": "FabricFcSanPcEp","properties":{"name":str(FcPcName), "admin_speed":"auto", "fill_pattern":"arbff", "auto_negotiate":"yes", "usr_lbl":"", "slot_id":"1", "admin_state":"enabled", "port_id":str(port)}, "message": "Adding port to Portchannel"})
        vsanObject["children"] =  vsanAChildren
        objectTemp.append(vsanObject)
        vsanObject = {"module": "ucsmsdk.mometa.fabric.FabricFcSanPc","class": "FabricFcSanPc","properties": {"parent_mo_or_dn":"fabric/san/B", "port_id": str(PcIdB)}}
        for port in PcPort:
            vsanBChildren.append({"module": "ucsmsdk.mometa.fabric.FabricFcSanPcEp","class": "FabricFcSanPcEp","properties":{"name":str(FcPcName), "admin_speed":"auto", "fill_pattern":"arbff", "auto_negotiate":"yes", "usr_lbl":"", "slot_id":"1", "admin_state":"enabled", "port_id":str(port)}, "message": "Adding port to Portchannel"})
        vsanObject["children"] =  vsanBChildren
        objectTemp.append(vsanObject)
        #put VSAN on PC
        vsanObject = {"module": "ucsmsdk.mometa.fabric.FabricVsan","class": "FabricVsan","properties": {"parent_mo_or_dn": "fabric/san/A","name": "VSAN-A"},"children": [{"module": "ucsmsdk.mometa.fabric.FabricFcVsanPc","class": "FabricFcVsanPc","properties": {"admin_state":"enabled", "port_id": str(PcIdA), "name":"", "descr":"", "switch_id":"A"}}]}
        objectTemp.append(vsanObject)
        vsanObject = {"module": "ucsmsdk.mometa.fabric.FabricVsan","class": "FabricVsan","properties": {"parent_mo_or_dn": "fabric/san/B","name": "VSAN-B"},"children": [{"module": "ucsmsdk.mometa.fabric.FabricFcVsanPc","class": "FabricFcVsanPc","properties": {"admin_state":"enabled", "port_id": str(PcIdB), "name":"", "descr":"", "switch_id":"B"}}]}
        objectTemp.append(vsanObject)

    #vHBA
    vnicTemplObject = {"module": "ucsmsdk.mometa.vnic.VnicSanConnTempl","class": "VnicSanConnTempl","properties": {"parent_mo_or_dn":"org-root","ident_pool_name":"WWPN-Pool-A", "templ_type":"updating-template", "name":"vHBA-Template-A"}}
    vnicTemplObject["children"] = {"module": "ucsmsdk.mometa.vnic.VnicFcIf","class": "VnicFcIf","properties":{"name":"VSAN-A"}, "message": "Create Vnic Template"}
    objectTemp.append(vnicTemplObject)
    vnicTemplObject = {"module": "ucsmsdk.mometa.vnic.VnicSanConnTempl","class": "VnicSanConnTempl","properties": {"parent_mo_or_dn":"org-root","ident_pool_name":"WWPN-Pool-B", "templ_type":"updating-template", "name":"vHBA-Template-B"}}
    vnicTemplObject["children"] = {"module": "ucsmsdk.mometa.vnic.VnicFcIf","class": "VnicFcIf","properties":{"name":"VSAN-B"}, "message": "Create Vnic Template"}
    objectTemp.append(vnicTemplObject)

    #SAN Connectivity Policies
    objectTemp.append( {"module": "ucsmsdk.mometa.vnic.VnicSanConnPolicy","class": "VnicSanConnPolicy","properties": {"parent_mo_or_dn": "org-root","name": "FC-Boot"},"message": "create vnicSANConn","children": [{"module": "ucsmsdk.mometa.vnic.VnicFcNode","class": "VnicFcNode","properties": {"ident_pool_name":"WWNN-Pool","addr":"pool-derived"},"message": "WWNN Pool"},{"module": "ucsmsdk.mometa.vnic.VnicFc","class": "VnicFc","properties": {"adaptor_profile_name":"VMWare","order":"1", "name":"Fabric-A","nw_templ_name":"vHBA-Template-A"},"message": "Add vHBA-Template-A","children": [{"module": "ucsmsdk.mometa.vnic.VnicFcIf","class": "VnicFcIf","properties": {"name":"default"},"message": "Add vHBA-Template-A"}]},{"module": "ucsmsdk.mometa.vnic.VnicFc","class": "VnicFc","properties": {"adaptor_profile_name":"VMWare","order":"2","switch_id":"B","name":"Fabric-B","nw_templ_name":"vHBA-Template-B"},"message": "Add vHBA-Template-A","children": [{"module": "ucsmsdk.mometa.vnic.VnicFcIf","class": "VnicFcIf","properties": {"name":"default"},"message": "Add vHBA-Template-A"}]}]})

    print()
    flexPod['objects'] = objectTemp

    return(flexPod)

def adminPolicies(flexPod):
    objectTemp = flexPod['objects']
    ntpIP = []
    ntpObject = {"module": "ucsmsdk.mometa.comm.CommDateTime","class": "CommDateTime","properties": {"parent_mo_or_dn": "sys/svc-ext","timezone": "America/New_York (Eastern Time)"},"message": "set timezone to America/New_York (Eastern Time)"}
    ntpChildren = []

    while True:             #get the NTP time servers
        ntpInp = input("IP address of the NTP server? [Press Enter if done]: ")   # Get the input
        if ntpInp == "":       # If it is a blank line...
            break
        else:
             ntpIP.append(ntpInp)
    for ip in ntpIP:
        ntpChildren.append({"module": "ucsmsdk.mometa.comm.CommNtpProvider","class": "CommNtpProvider","properties": {"name": str(ip)},"message": "add ntp server " + str(ip)})

    objectTemp.append({"module": "ucsmsdk.mometa.qosclass.QosclassEthBE","class": "QosclassEthBE", "properties": { "parent_mo_or_dn": "fabric/lan/classes", "mtu": "9216"},"message": "Configure Jumbo Frames"})
    objectTemp.append({"module": "ucsmsdk.mometa.storage.StorageLocalDiskConfigPolicy","class": "StorageLocalDiskConfigPolicy", "properties": { "parent_mo_or_dn": "org-root", "mode": "no-local-storage", "name": "SAN-Boot"},"message": "Local Disk Config for Boot-from SAN"})
    objectTemp.append({"module": "ucsmsdk.mometa.compute.ComputeChassisDiscPolicy","class": "ComputeChassisDiscPolicy", "properties": { "parent_mo_or_dn": "org-root", "multicast_hw_hash": "disabled", "backplane_speed_pref": "40G", "action": "1-link", "rebalance": "user-acknowledged","link_aggregation_pref": "port-channel"},"message": "configure chassis discovery policy"})
    objectTemp.append({"module": "ucsmsdk.mometa.compute.ComputeServerDiscPolicy","class": "ComputeServerDiscPolicy","properties": {"parent_mo_or_dn": "org-root","action": "immediate"},"message": "configure rack server discovery policy"})
    objectTemp.append({"module": "ucsmsdk.mometa.compute.ComputeServerMgmtPolicy","class": "ComputeServerMgmtPolicy","properties": {"parent_mo_or_dn": "org-root","action": "auto-acknowledged"},"message": "configure rack management connection policy"})
    objectTemp.append({"module": "ucsmsdk.mometa.compute.ComputePsuPolicy","class": "ComputePsuPolicy","properties": {"parent_mo_or_dn": "org-root","redundancy": "n+1"},"message": "configure power policy"})
    objectTemp.append({"module": "ucsmsdk.mometa.power.PowerMgmtPolicy","class": "PowerMgmtPolicy","properties": {"parent_mo_or_dn": "org-root","style": "intelligent-policy-driven","profiling": "no","skip_power_deploy_check": "no","skip_power_check": "no"},"message": "configure global power allocation policy"})
    objectTemp.append({"module": "ucsmsdk.mometa.nwctrl.NwctrlDefinition","class": "NwctrlDefinition","properties": {"parent_mo_or_dn": "org-root","lldp_transmit":"enabled", "cdp":"enabled","name":"Enable-CDP-LLDP", "lldp_receive":"enabled"},"message": "creat CDP policy","children": [{"module": "ucsmsdk.mometa.dpsec.DpsecMac","class": "DpsecMac","properties": {"forge":"allow", "policy_owner":"local", "name":"", "descr":""},"message": "CDP Policy"}]})
    objectTemp.append({"module": "ucsmsdk.mometa.power.PowerPolicy","class": "PowerPolicy","properties": {"parent_mo_or_dn": "org-root","name":"No-Power-Cap","prio":"no-cap"},"message": "configure power policy"})
    if ntpIP:
        ntpObject['children'] = ntpChildren
        objectTemp.append(ntpObject)
    #BIOS Policy
    objectTemp.append({"module": "ucsmsdk.mometa.bios.BiosVProfile","class": "BiosVProfile","properties": {"parent_mo_or_dn": "org-root","name":"VM-Host"},"message": "Bios Profile"})
    objectTemp.append({"module": "ucsmsdk.mometa.bios.BiosTokenSettings","class": "BiosTokenSettings","properties": {"parent_mo_or_dn": "org-root/bios-prof-VM-Host/tokn-featr-Quiet Boot/tokn-param-QuietBoot", "is_assigned":"yes", "settings_mo_rn":"Disabled"},"message": "Quiet Boot"})
    objectTemp.append({"module": "ucsmsdk.mometa.bios.BiosTokenSettings","class": "BiosTokenSettings","properties": {"parent_mo_or_dn": "org-root/bios-prof-VM-Host/tokn-featr-Consistent Device Name Control/tokn-param-cdnEnable", "is_assigned":"yes", "settings_mo_rn":"Enabled"},"message": "CDN Enabled"})

    objectTemp.append({"module": "ucsmsdk.mometa.lsmaint.LsmaintMaintPolicy","class": "LsmaintMaintPolicy","properties": {"parent_mo_or_dn": "org-root", "uptime_disr": "user-ack", "name":"default", "trigger_config": "on-next-boot"},"message": "On next boot"})


    flexPod['objects'] = objectTemp
    print()
    return (flexPod)

def ethernetPort(flexPod):
    objectTemp = flexPod['objects']
    serverPort = []
    portAObject = {}
    portBObject = {}
    portServerChildren = []
    uplinkPort = []
    portUpLinkChildren = []
    portChannelPort = []
    portChannelChildren = []

    #server Ports
    while True:
        serverPortInp = input("Enter the port # that will be a Server Port? [Press Enter if done]: ")
        if serverPortInp == "":
            break
        else:
            serverPort.append(serverPortInp)
    if serverPort:
        for port in serverPort:
            portServerChildren.append({"module": "ucsmsdk.mometa.fabric.FabricDceSwSrvEp","class": "FabricDceSwSrvEp","properties": {"slot_id": "1","port_id": str(port)},"message": "port 1/" + str(port) + " as a Server Port"})

        portAObject = {"module": "ucsmsdk.mometa.fabric.FabricDceSwSrv","class": "FabricDceSwSrv","properties": {"parent_mo_or_dn": "fabric/server","id": "A"},"message": "Server Port config on FI-A"}
        portBObject = {"module": "ucsmsdk.mometa.fabric.FabricDceSwSrv","class": "FabricDceSwSrv","properties": {"parent_mo_or_dn": "fabric/server","id": "B"},"message": "Server Port config on FI-B"}
        portAObject["children"]=portServerChildren
        portBObject["children"]=portServerChildren
        objectTemp.append(portAObject)
        objectTemp.append(portBObject)
    print ()
    #uplink Ports
    while True:
        uplinkPortInp = input("Enter the port # that will be an Uplink Port? [Press Enter if done]: ")
        if uplinkPortInp == "":
            break
        else:
            portChannelPortInp = click.confirm("Is this part of a port channel", default = True)
            if portChannelPortInp == True:
                portChannelPort.append(uplinkPortInp)
            uplinkPort.append(uplinkPortInp)
    if uplinkPort:
        for port in uplinkPort:
            portUpLinkChildren.append({"module": "ucsmsdk.mometa.fabric.FabricEthLanEp","class": "FabricEthLanEp","properties": {"slot_id": "1","port_id": str(port)},"message": "port 1/" + str(port) + " as a Uplink Port"})


        portAObject = {"module": "ucsmsdk.mometa.fabric.FabricEthLan","class": "FabricEthLan","properties": {"parent_mo_or_dn": "fabric/lan","id": "A"},"message": "Uplink Port config on FI-A"}
        portAObject["children"]=portUpLinkChildren
        portBObject = {"module": "ucsmsdk.mometa.fabric.FabricEthLan","class": "FabricEthLan","properties": {"parent_mo_or_dn": "fabric/lan","id": "B"},"message": "Uplink Port config on FI-B"}
        portBObject["children"]=portUpLinkChildren
        objectTemp.append(portAObject)
        objectTemp.append(portBObject)

    print()
    #port channels
    if portChannelPort:  #if uplinks are using a portchannel
        pcA = input("FI A portchannel ID: ")
        pcName = input ("PortChannel " + pcA + " Name: ")
        portAObject = {"module": "ucsmsdk.mometa.fabric.FabricEthLanPc","class": "FabricEthLanPc","properties": {"parent_mo_or_dn": "fabric/lan/A","port_id": str(pcA), "name": str(pcName)},"message": "portchannel on FI-A"}
        pcB = input("FI B portchannel ID: ")
        pcName = click.prompt("PortChannel " + pcA + " Name: ", default = pcName)
        portBObject = {"module": "ucsmsdk.mometa.fabric.FabricEthLanPc","class": "FabricEthLanPc","properties": {"parent_mo_or_dn": "fabric/lan/B","port_id": str(pcB), "name": str(pcName)},"message": "portchannel on FI-B"}
        for port in portChannelPort:
            portChannelChildren.append({"module": "ucsmsdk.mometa.fabric.FabricEthLanPcEp","class": "FabricEthLanPcEp","properties": {"eth_link_profile_name": "default", "name": "", "auto_negotiate": "yes", "usr_lbl": "", "slot_id": "1", "admin_state":"enabled", "port_id": str(port)},"message": "adding " + port + "to PortChannel"})
        portAObject["children"]= portChannelChildren
        portBObject["children"]= portChannelChildren
        objectTemp.append(portAObject)
        objectTemp.append(portBObject)


    flexPod['objects'] = objectTemp
    return(flexPod)

def pools(flexPod):
    objectTemp = flexPod['objects']
    objectTemp.append({"module": "ucsmsdk.mometa.macpool.MacpoolPool","class": "MacpoolPool","properties": {"parent_mo_or_dn": "org-root", "name":"MAC-Pool-A", "assignment_order":"sequential"},"message": "Create MAC-Pool-A","children": [{"module": "ucsmsdk.mometa.macpool.MacpoolBlock","class": "MacpoolBlock","properties": {"r_from": "00:25:B5:00:0A:00","to": "00:25:B5:00:0A:FF"},"message": "Add MAC address to pool"}]}) #Mac Pool
    objectTemp.append({"module": "ucsmsdk.mometa.macpool.MacpoolPool","class": "MacpoolPool","properties": {"parent_mo_or_dn": "org-root", "name":"MAC-Pool-B", "assignment_order":"sequential"},"message": "Create MAC-Pool-B","children": [{"module": "ucsmsdk.mometa.macpool.MacpoolBlock","class": "MacpoolBlock","properties": {"r_from": "00:25:B5:00:0B:00","to": "00:25:B5:00:0B:FF"},"message": "Add MAC address to pool"}]}) #Mac Pool
    objectTemp.append({"module": "ucsmsdk.mometa.uuidpool.UuidpoolPool","class": "UuidpoolPool","properties": {"parent_mo_or_dn": "org-root","name": "UUID-Pool","prefix": "derived","assignment_order": "sequential"},"message": "create uuid pool","children": [{"module": "ucsmsdk.mometa.uuidpool.UuidpoolBlock","class": "UuidpoolBlock","properties": {"r_from": "0000-000000000001","to": "0000-000000000100"},"message": "create uuid pool block"}]})
    flexPod['objects'] = objectTemp
    return(flexPod)

def vlans(flexPod, vlan):
    objectTemp = flexPod['objects']
    nativeVlan = {}
#    vlan = vlan


    while True:
        vlanInp = input("Enter VLAN ID? [Press Enter if done]: ")
        if vlanInp == "":
            break
        elif vlanInp.isdigit():
            if vlanInp not in vlan:
                vlan[vlanInp] = input("Name for VLAN?: ")
                if (click.confirm("Native Vlan?", default = False)) == False:
                    nativeVlan[vlanInp] = ("no")
                else:
                    nativeVlan[vlanInp] = ("yes")
                print()
            else:
                print("VLAN ID's need to be unique")
                print()
        else:
            print("Vlan needs to be a number")

    for key in vlan:
        objectTemp.append({"module": "ucsmsdk.mometa.fabric.FabricVlan","class": "FabricVlan","properties": {"parent_mo_or_dn":"fabric/lan", "sharing":"none", "name":str(vlan[key]), "id": str(key), "mcast_policy_name":"", "policy_owner":"local", "default_net": str(nativeVlan[key]), "pub_nw_name":"", "compression_type":"included"},"message": "Create VLAN"})


    print()
    #objectTemp.append()#add objects
    flexPod['objects'] = objectTemp
    return(flexPod)

def vnic(flexPod, vlan):
    objectTemp = flexPod['objects']
    vlanId = []
    tempVlan = vlan
    dvsChildren = []
    dvsObject= {}
    print()
    for key, vlaue in vlan.items():
        vlanId.append(key)

    #mgmt VLAN
    #mgmtVlan = vlan[input("Select the Managment Vlan: " + str(vlanId))]
    mgmtVlan = input("Select the Managment Vlan: " + str(vlanId) + "[Press Enter if None] ")
    while True:
        if mgmtVlan == "":
            break
        elif not mgmtVlan in vlanId:
            print("Vlan chosen is not a Configured Vlan")
            print()
            mgmtVlan = input("Select the Managment Vlan: " + str(vlanId) + "[Press Enter if None] ")
        else:
            objectTemp.append({"module": "ucsmsdk.mometa.vnic.VnicLanConnTempl","class": "VnicLanConnTempl","properties": {"parent_mo_or_dn": "org-root", "templ_type":"updating-template", "name":"Infra-A", "redundancy_pair_type":"primary", "ident_pool_name":"MAC-Pool-A", "mtu":"9000", "nw_ctrl_policy_name":"Enable-CDP-LLDP"},"message": "Create VNIC Template","children": [{"module": "ucsmsdk.mometa.vnic.VnicEtherIf","class": "VnicEtherIf","properties": {"default_net":"no", "name":vlan[mgmtVlan]},"message": "add Vlan to vnic tempalte"}]})
            objectTemp.append({"module": "ucsmsdk.mometa.vnic.VnicLanConnTempl","class": "VnicLanConnTempl","properties": {"parent_mo_or_dn": "org-root", "templ_type":"updating-template", "name":"Infra-B", "redundancy_pair_type":"secondary", "ident_pool_name":"MAC-Pool-B","peer_redundancy_templ_name":"Infra-A", "switch_id":"B"},"message": "Create VNIC Template" })
            try:
                vlanId.remove(mgmtVlan)
            except KeyError:
                pass
            break

    #VMotion VLAN
    vmotionVlan = input("Select the vMotion Vlan: " + str(vlanId) + "[Press Enter if None] ")
    while True:
        if vmotionVlan == "":
            break
        elif not vmotionVlan in vlanId:
            print("Vlan chosen is not a Configured Vlan")
            print()
            vmotionVlan = input("Select the vMotion Vlan: " + str(vlanId) + "[Press Enter if None] ")
        else:
            objectTemp.append({"module": "ucsmsdk.mometa.vnic.VnicLanConnTempl","class": "VnicLanConnTempl","properties": {"parent_mo_or_dn": "org-root", "templ_type":"updating-template", "name":"vMotion-A", "redundancy_pair_type":"primary", "ident_pool_name":"MAC-Pool-A", "mtu":"9000", "nw_ctrl_policy_name":"Enable-CDP-LLDP"},"message": "Create VNIC Template","children": [{"module": "ucsmsdk.mometa.vnic.VnicEtherIf","class": "VnicEtherIf","properties": {"default_net":"no", "name":vlan[vmotionVlan]},"message": "add Vlan to vnic tempalte"}]})
            objectTemp.append({"module": "ucsmsdk.mometa.vnic.VnicLanConnTempl","class": "VnicLanConnTempl","properties": {"parent_mo_or_dn": "org-root", "templ_type":"updating-template", "name":"vMotion-B", "redundancy_pair_type":"secondary", "ident_pool_name":"MAC-Pool-B","peer_redundancy_templ_name":"vMotion-A", "switch_id":"B"},"message": "Create VNIC Template"})
            try:
                vlanId.remove(vmotionVlan)
            except KeyError:
                pass
            break
    #NFS VLAN
    nfsVlan = input("Select the NFS Vlan: " + str(vlanId) + "[Press Enter if None] ")
    while True:
        if nfsVlan == "":
            break
        elif not nfsVlan in vlanId:
            print("Vlan chosen is not a Configured Vlan")
            print()
            nfsVlan = input("Select the NFS Vlan: " + str(vlanId) + "[Press Enter if None] ")
        else:
            objectTemp.append({"module": "ucsmsdk.mometa.vnic.VnicLanConnTempl","class": "VnicLanConnTempl","properties": {"parent_mo_or_dn": "org-root", "templ_type":"updating-template", "name":"NFS-A", "redundancy_pair_type":"primary", "ident_pool_name":"MAC-Pool-A", "mtu":"9000", "nw_ctrl_policy_name":"Enable-CDP-LLDP"},"message": "Create VNIC Template","children": [{"module": "ucsmsdk.mometa.vnic.VnicEtherIf","class": "VnicEtherIf","properties": {"default_net":"no", "name":vlan[nfsVlan]},"message": "add Vlan to vnic tempalte"}]})
            objectTemp.append({"module": "ucsmsdk.mometa.vnic.VnicLanConnTempl","class": "VnicLanConnTempl","properties": {"parent_mo_or_dn": "org-root", "templ_type":"updating-template", "name":"NFS-B", "redundancy_pair_type":"secondary", "ident_pool_name":"MAC-Pool-B","peer_redundancy_templ_name":"NFS-A", "switch_id":"B"},"message": "Create VNIC Template"})
            try:
                vlanId.remove(vmotionVlan)
            except KeyError:
                pass
            break
    #DVS
    dvs = []
    while True:
        dvsInp= input("Select the Data Vlan(s): [Press Enter if done] " + str(vlanId))
        if dvsInp == "":       # If it is a blank line...
            break
        elif not dvsInp in vlanId:
            print("Vlan chosen is not a Configured Vlan")
            print()
            dvsInp= input("Select the Data Vlan(s): [Press Enter if done] " + str(vlanId))
        else:
            dvs.append(vlan[dvsInp])
            try:
                vlanId.remove(dvsInp)
            except KeyError:
                pass
            if not vlanId:
                break


    for vlanName in dvs:
        dvsChildren.append({"module": "ucsmsdk.mometa.vnic.VnicEtherIf","class": "VnicEtherIf","properties": {"default_net":"no", "name":vlanName},"message": "add Vlan to vnic tempalte"})


    print (dvsChildren)

    dvsObject = {"module": "ucsmsdk.mometa.vnic.VnicLanConnTempl","class": "VnicLanConnTempl","properties": {"parent_mo_or_dn": "org-root", "templ_type":"updating-template", "name":"DVS-Template-A", "redundancy_pair_type":"primary", "ident_pool_name":"MAC-Pool-A", "mtu":"9000", "nw_ctrl_policy_name":"Enable-CDP-LLDP"},"message": "Create VNIC Template","children": []}
    dvsObject["children"]=dvsChildren
    objectTemp.append(dvsObject)#add objects
    objectTemp.append({"module": "ucsmsdk.mometa.vnic.VnicLanConnTempl","class": "VnicLanConnTempl","properties": {"parent_mo_or_dn": "org-root", "templ_type":"updating-template", "name":"DVS-Template-B", "redundancy_pair_type":"secondary", "ident_pool_name":"MAC-Pool-B","peer_redundancy_templ_name":"DVS-Template-A", "switch_id":"B"},"message": "Create VNIC Template"})

    flexPod['objects'] = objectTemp
    return(flexPod)

#def dummy(flexPod):
#    objectTemp = flexPod['objects']



#    objectTemp.append()#add objects
#    flexPod['objects'] = objectTemp
#    return(flexPod)

if __name__=='__main__':

    flexPod = {"connection": {"module": "ucsmsdk.ucshandle","class": "UcsHandle","commit-buffer": True,"properties": {"ip": "","username": "admin","password": "","secure": True}},"objects": []}
    vlan = {}
#    try:
#        ip = ipaddress.ip_address(input('what is the IP of the UCSM? ' ))
#        flexPod["connection"]["properties"]["ip"] = str(ip)
#    except ValueError:
#        print('address/netmask is invalid: %s' % ip)
#    except:
#        print('Usage : %s  ip' % ip)

#    flexPod["connection"]["properties"]["username"] = click.prompt('what is the username for the UCSM?', default = "admin" )
#    flexPod["connection"]["properties"]["password"] = input('what is the password for the UCSM? ' )

    if click.confirm('is this flexpod using FC? ', default = False):
        fc(flexPod)
    #adminPolicies(flexPod)
#    ethernetPort(flexPod)  #configure ethernet ports
#    pools(flexPod) #configure Mac/uuid Pools
#    print(vlan)
    vlans(flexPod, vlan)  #configure VLANs
    vnic(flexPod, vlan)  #configure VLANs
    print(vlan)

    with open("customFlexPod.json", "w") as write_file:
        json.dump(flexPod, write_file)
