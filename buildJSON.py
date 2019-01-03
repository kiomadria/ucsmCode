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
            portChannelChildren.append({"module": "ucsmsdk.mometa.fabric.FabricEthLanPcEp","class": "FabricEthLanPcEp","properties": {"eth_link_profile_name": "default", "name": "", "auto_negotiate": "yes", "usr_lbl": "", "slot_id": "1", "admin_state":"enabled", "port_id": str(port)},"message": "adding " + port + " to PortChannel"})
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

    print("###################################")
    print("#         Input Vlans             #")
    print("###################################")
    print()
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

def vnic(flexPod, vlan, datastore):
    objectTemp = flexPod['objects']
    vlanId = []
    tempVlan = vlan
    dvsChildren = []
    dvsObject= {}

    print()
    for key, vlaue in vlan.items():
        vlanId.append(key)

    if datastore["fc"] == False:
        print("###################################")
        print("#      Datastore Selection        #")
        print("###################################")
        print()
        datastoreInp = click.prompt("Is the Datastore NFS or iSCSI: ", default = "NFS")

        while True:
            if datastoreInp ==  "":
                print ("No datastore method slected")
                break
            elif datastoreInp.lower() == "nfs": # or datastoreInp == "NFS":
                datastore["nfs"]= True
                break
            elif datastoreInp.lower() == "isci":
                datastore["isci"]
                break
            else:
                print("A valid entry is needed")
    #mgmt VLAN
    #mgmtVlan = vlan[input("Select the Managment Vlan: " + str(vlanId))]
    print()
    print("###################################")
    print("#        Vlans Selection          #")
    print("###################################")
    print()
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
    nfsVlan = ""
    if datastore["nfs"] == True:
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
                    vlanId.remove(nfsVlan)
                except KeyError:
                    pass
                break
    #iSCSI vlan
    iscsiVlan = ""
    if datastore["iscsi"] == True:
        iscsiVlan =  input("Select the iSCSI Vlan: " + str(vlanId) + "[Press Enter if None] ")
        while True:
            if iscsiVlan == "":
                break
            elif not iscsiVlan in vlanId:
                print("Vlan chosen is not a Configured Vlan")
                print()
                iscsiVlan = input("Select the iSCSI Vlan: " + str(vlanId) + "[Press Enter if None] ")
            else:
                #objectTemp.append()
                print("this part isn't done yet")
                try:
                    vlanId.remove(iscsiVlan)
                except KeyError:
                    pass
                break

    #DVS
    dvs= []
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

    if dvs:
        for vlanName in dvs:
            dvsChildren.append({"module": "ucsmsdk.mometa.vnic.VnicEtherIf","class": "VnicEtherIf","properties": {"default_net":"no", "name":vlanName},"message": "add Vlan to vnic tempalte"})


    #print (dvsChildren)

    dvsObject = {"module": "ucsmsdk.mometa.vnic.VnicLanConnTempl","class": "VnicLanConnTempl","properties": {"parent_mo_or_dn": "org-root", "templ_type":"updating-template", "name":"DVS-Template-A", "redundancy_pair_type":"primary", "ident_pool_name":"MAC-Pool-A", "mtu":"9000", "nw_ctrl_policy_name":"Enable-CDP-LLDP"},"message": "Create VNIC Template","children": []}
    dvsObject["children"]=dvsChildren
    objectTemp.append(dvsObject)#add objects
    objectTemp.append({"module": "ucsmsdk.mometa.vnic.VnicLanConnTempl","class": "VnicLanConnTempl","properties": {"parent_mo_or_dn": "org-root", "templ_type":"updating-template", "name":"DVS-Template-B", "redundancy_pair_type":"secondary", "ident_pool_name":"MAC-Pool-B","peer_redundancy_templ_name":"DVS-Template-A", "switch_id":"B"},"message": "Create VNIC Template"})

    #LAN Conn policy
    lanConnPolicyChildren = []
    order = 0
    connPolcyObject = {"module": "ucsmsdk.mometa.vnic.VnicLanConnPolicy","class": "VnicLanConnPolicy","properties": {"parent_mo_or_dn": "org-root", "name":"FC-Boot"},"message": "Create Lan Connectivity Policy","children": []}
    if mgmtVlan:
        lanConnPolicyChildren.append({"module": "ucsmsdk.mometa.vnic.VnicEther","class": "VnicEther","properties": {"adaptor_profile_name":"VMWare", "order":order,"name":"0" + str(order) + "-Infra-A", "nw_templ_name":"Infra-A"},"message": "add to Lan Conn Policy"})
        order = order + 1
        lanConnPolicyChildren.append({"module": "ucsmsdk.mometa.vnic.VnicEther","class": "VnicEther","properties": {"adaptor_profile_name":"VMWare", "order":order,"switch_id":"B", "name":"0" + str(order) + "-Infra-B", "nw_templ_name":"Infra-B"},"message": "add to Lan Conn Policy"})
        order = order + 1
    if vmotionVlan:
        lanConnPolicyChildren.append({"module": "ucsmsdk.mometa.vnic.VnicEther","class": "VnicEther","properties": {"adaptor_profile_name":"VMWare", "order":order,"name":"0" + str(order) + "-vMotion-A", "nw_templ_name":"vMotion-A"},"message": "add to Lan Conn Policy"})
        order = order + 1
        lanConnPolicyChildren.append({"module": "ucsmsdk.mometa.vnic.VnicEther","class": "VnicEther","properties": {"adaptor_profile_name":"VMWare", "order":order,"switch_id":"B", "name":"0" + str(order) + "-vMotion-B", "nw_templ_name":"vMotion-B"},"message": "add to Lan Conn Policy"})
        order = order + 1
    if dvs:
        lanConnPolicyChildren.append({"module": "ucsmsdk.mometa.vnic.VnicEther","class": "VnicEther","properties": {"adaptor_profile_name":"VMWare", "order":order,"name":"0" + str(order) + "-DVS-Template-A", "nw_templ_name":"DVS-Template-A"},"message": "add to Lan Conn Policy"})
        order = order + 1
        lanConnPolicyChildren.append({"module": "ucsmsdk.mometa.vnic.VnicEther","class": "VnicEther","properties": {"adaptor_profile_name":"VMWare", "order":order,"switch_id":"B", "name":"0" + str(order) + "-DVS-Template-B", "nw_templ_name":"DVS-Template-B"},"message": "add to Lan Conn Policy"})
        order = order + 1
    if nfsVlan:
        lanConnPolicyChildren.append({"module": "ucsmsdk.mometa.vnic.VnicEther","class": "VnicEther","properties": {"adaptor_profile_name":"VMWare", "order":order,"name":"0" + str(order) + "-NFS-A", "nw_templ_name":"NFS-A"},"message": "add to Lan Conn Policy"})
        order = order + 1
        lanConnPolicyChildren.append({"module": "ucsmsdk.mometa.vnic.VnicEther","class": "VnicEther","properties": {"adaptor_profile_name":"VMWare", "order":order,"switch_id":"B", "name":"0" + str(order) + "-NFS-B", "nw_templ_name":"NFS-B"},"message": "add to Lan Conn Policy"})
        order = order + 1
    if iscsiVlan:
        lanConnPolicyChildren.append({"module": "ucsmsdk.mometa.vnic.VnicEther","class": "VnicEther","properties": {"adaptor_profile_name":"VMWare", "order":order,"name":"0" + str(order) + "-iSCSI-A", "nw_templ_name":"iSCSI-A"},"message": "add to Lan Conn Policy"})
        order = order + 1
        lanConnPolicyChildren.append({"module": "ucsmsdk.mometa.vnic.VnicEther","class": "VnicEther","properties": {"adaptor_profile_name":"VMWare", "order":order,"switch_id":"B", "name":"0" + str(order) + "-iSCSI-B", "nw_templ_name":"iSCSI-B"},"message": "add to Lan Conn Policy"})
        order = order + 1

    #Boot Policy
    objectTemp.append({"module":"ucsmsdk.mometa.lsboot.LsbootPolicy","class":"LsbootPolicy","properties":{"parent_mo_or_dn":"org-root","name":"Boot-Local-Drive"},"message":"create Boot Policy","children":[{"module":"ucsmsdk.mometa.lsboot.LsbootStorage","class":"LsbootStorage","properties":{"order":"3"},"message":"Boot Policy","children":[{"module":"ucsmsdk.mometa.lsboot.LsbootStorage","class":"LsbootStorage","message":"Boot Policy","children":[{"module":"ucsmsdk.mometa.lsboot.LsbootEmbeddedLocalDiskImage","class":"LsbootEmbeddedLocalDiskImage","properties":{"order":"2"},"message":"Boot Policy"},{"module":"ucsmsdk.mometa.lsboot.LsbootUsbFlashStorageImage","class":"LsbootUsbFlashStorageImage","properties":{"order":"3"},"message":"Boot Policy"},{"module":"ucsmsdk.mometa.lsboot.LsbootLocalDiskImage","class":"LsbootLocalDiskImage","properties":{"order":"4"},"message":"Boot Policy","children":[{"module":"ucsmsdk.mometa.lsboot.LsbootLocalDiskImagePath","class":"LsbootLocalDiskImagePath","properties":{"type":"primary"},"message":"Boot Policy"}]}]}]}]})

    #Serivce Profile template
    objectTemp.append({"module":"ucsmsdk.mometa.ls.LsServer","class":"LsServer","properties":{"parent_mo_or_dn":"org-root","name":"VM-Host-Infra","boot_policy_name":"Boot-Local-Drive","ext_ip_state":"pooled","bios_profile_name":"VM-Host","power_policy_name":"No-Power-Cap","maint_policy_name":"default","host_fw_policy_name":"not_defalt","ident_pool_name":"UUID-Pool","type":"updating-template"},"message":"create Serivce Profile Template","children":[{"module":"ucsmsdk.mometa.storage.StorageLocalDiskConfigDef","class":"StorageLocalDiskConfigDef","properties":{"protect_config":"yes","name":"","descr":"","flex_flash_raid_reporting_state":"enable","flex_flash_state":"enable","policy_owner":"local","mode":"raid-striped","flex_flash_removable_state":"no-change"}},{"module":"ucsmsdk.mometa.vnic.VnicConnDef","class":"VnicConnDef","properties":{"san_conn_policy_name":"FC-Boot","lan_conn_policy_name":"FC-Boot"}},{"module":"ucsmsdk.mometa.vnic.VnicEther","class":"VnicEther","properties":{"cdn_prop_in_sync":"yes","nw_ctrl_policy_name":"","admin_host_port":"ANY","admin_vcon":"any","stats_policy_name":"default","admin_cdn_name":"","switch_id":"A","pin_to_group_name":"","name":"00-Infra-A","order":"1","qos_policy_name":"","adaptor_profile_name":"","ident_pool_name":"","cdn_source":"vnic-name","mtu":"1500","nw_templ_name":"","addr":"derived"}},{"module":"ucsmsdk.mometa.vnic.VnicEther","class":"VnicEther","properties":{"cdn_prop_in_sync":"yes","nw_ctrl_policy_name":"","admin_host_port":"ANY","admin_vcon":"any","stats_policy_name":"default","admin_cdn_name":"","switch_id":"A","pin_to_group_name":"","name":"01-Infra-B","order":"2","qos_policy_name":"","adaptor_profile_name":"","ident_pool_name":"","cdn_source":"vnic-name","mtu":"1500","nw_templ_name":"","addr":"derived"}},{"module":"ucsmsdk.mometa.vnic.VnicEther","class":"VnicEther","properties":{"cdn_prop_in_sync":"yes","nw_ctrl_policy_name":"","admin_host_port":"ANY","admin_vcon":"any","stats_policy_name":"default","admin_cdn_name":"","switch_id":"A","pin_to_group_name":"","name":"02-vMotion-A","order":"3","qos_policy_name":"","adaptor_profile_name":"","ident_pool_name":"","cdn_source":"vnic-name","mtu":"1500","nw_templ_name":"","addr":"derived"}},{"module":"ucsmsdk.mometa.vnic.VnicEther","class":"VnicEther","properties":{"cdn_prop_in_sync":"yes","nw_ctrl_policy_name":"","admin_host_port":"ANY","admin_vcon":"any","stats_policy_name":"default","admin_cdn_name":"","switch_id":"A","pin_to_group_name":"","name":"03-vMotion-B","order":"4","qos_policy_name":"","adaptor_profile_name":"","ident_pool_name":"","cdn_source":"vnic-name","mtu":"1500","nw_templ_name":"","addr":"derived"}},{"module":"ucsmsdk.mometa.vnic.VnicEther","class":"VnicEther","properties":{"cdn_prop_in_sync":"yes","nw_ctrl_policy_name":"","admin_host_port":"ANY","admin_vcon":"any","stats_policy_name":"default","admin_cdn_name":"","switch_id":"A","pin_to_group_name":"","name":"04-DVS-A","order":"5","qos_policy_name":"","adaptor_profile_name":"","ident_pool_name":"","cdn_source":"vnic-name","mtu":"1500","nw_templ_name":"","addr":"derived"}},{"module":"ucsmsdk.mometa.vnic.VnicEther","class":"VnicEther","properties":{"cdn_prop_in_sync":"yes","nw_ctrl_policy_name":"","admin_host_port":"ANY","admin_vcon":"any","stats_policy_name":"default","admin_cdn_name":"","switch_id":"A","pin_to_group_name":"","name":"05-DVS-B","order":"6","qos_policy_name":"","adaptor_profile_name":"","ident_pool_name":"","cdn_source":"vnic-name","mtu":"1500","nw_templ_name":"","addr":"derived"}},{"module":"ucsmsdk.mometa.vnic.VnicFcNode","class":"VnicFcNode","properties":{"ident_pool_name":"node-default","addr":"pool-derived"}},{"module":"ucsmsdk.mometa.vnic.VnicFc","class":"VnicFc","properties":{"cdn_prop_in_sync":"yes","addr":"derived","admin_host_port":"ANY","admin_vcon":"any","stats_policy_name":"default","admin_cdn_name":"","switch_id":"A","pin_to_group_name":"","pers_bind":"disabled","order":"7","pers_bind_clear":"no","qos_policy_name":"","adaptor_profile_name":"","ident_pool_name":"","cdn_source":"vnic-name","max_data_field_size":"2048","nw_templ_name":"","name":"Fabric-A"}},{"module":"ucsmsdk.mometa.vnic.VnicFc","class":"VnicFc","properties":{"cdn_prop_in_sync":"yes","addr":"derived","admin_host_port":"ANY","admin_vcon":"any","stats_policy_name":"default","admin_cdn_name":"","switch_id":"A","pin_to_group_name":"","pers_bind":"disabled","order":"8","pers_bind_clear":"no","qos_policy_name":"","adaptor_profile_name":"","ident_pool_name":"","cdn_source":"vnic-name","max_data_field_size":"2048","nw_templ_name":"","name":"Fabric-B"}},{"module":"ucsmsdk.mometa.fabric.FabricVCon","class":"FabricVCon","properties":{"placement":"physical","fabric":"NONE","share":"shared","select":"all","transport":"ethernet,fc","id":"1","inst_type":"auto"}},{"module":"ucsmsdk.mometa.fabric.FabricVCon","class":"FabricVCon","properties":{"placement":"physical","fabric":"NONE","share":"shared","select":"all","transport":"ethernet,fc","id":"1","inst_type":"auto"}},{"module":"ucsmsdk.mometa.fabric.FabricVCon","class":"FabricVCon","properties":{"placement":"physical","fabric":"NONE","share":"shared","select":"all","transport":"ethernet,fc","id":"2","inst_type":"auto"}},{"module":"ucsmsdk.mometa.fabric.FabricVCon","class":"FabricVCon","properties":{"placement":"physical","fabric":"NONE","share":"shared","select":"all","transport":"ethernet,fc","id":"3","inst_type":"auto"}},{"module":"ucsmsdk.mometa.fabric.FabricVCon","class":"FabricVCon","properties":{"placement":"physical","fabric":"NONE","share":"shared","select":"all","transport":"ethernet,fc","id":"4","inst_type":"auto"}},{"module":"ucsmsdk.mometa.ls.LsPower","class":"LsPower","properties":{"state":"admin-down"}},{"module":"ucsmsdk.mometa.mgmt.MgmtInterface","class":"MgmtInterface","properties":{"ip_v4_state":"none","mode":"in-band","ip_v6_state":"none"},"children":[{"module":"ucsmsdk.mometa.mgmt.MgmtVnet","class":"MgmtVnet","properties":{"id":"1","name":""}}]}]})


    flexPod['objects'] = objectTemp
    return(flexPod, datastore)

#def dummy(flexPod):
#    objectTemp = flexPod['objects']



#    objectTemp.append()#add objects
#    flexPod['objects'] = objectTemp
#    return(flexPod)

if __name__=='__main__':

    flexPod = {"connection": {"module": "ucsmsdk.ucshandle","class": "UcsHandle","commit-buffer": True,"properties": {"ip": "","username": "admin","password": "","secure": True}},"objects": []}
    vlan = {}
    datastore = {
      "nfs": False,
      "iscsi": False,
      "fc": False
    }

#    ip =  ipaddress.ip_address(input('what is the IP of the UCSM? ' ))
#    flexPod["connection"]["properties"]["ip"] = str(ip)

    try:
        ip = ipaddress.ip_address(input('what is the IP of the UCSM? ' ))
        flexPod["connection"]["properties"]["ip"] = str(ip)
    except ValueError:
        print('address/netmask is invalid: %s' % ip)
    except:
        print('Usage : %s  ip' % ip)

    flexPod["connection"]["properties"]["username"] = click.prompt('what is the username for the UCSM?', default = "admin" )
    flexPod["connection"]["properties"]["password"] = input('what is the password for the UCSM? ' )

    if click.confirm('is this flexpod using FC? ', default = False):
        datastore["fc"] = True
        fc(flexPod)
    adminPolicies(flexPod)
    ethernetPort(flexPod)  #configure ethernet ports
    pools(flexPod) #configure Mac/uuid Pools
    vlans(flexPod, vlan)  #configure VLANs
    vnic(flexPod, vlan, datastore)  #configure VLANs


    with open("customFlexPod.json", "w") as write_file:
        json.dump(flexPod, write_file)
