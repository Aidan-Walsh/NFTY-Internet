"""DDoS : N-hop setup modified"""

#
# NOTE: This code was machine converted. An actual human would not
#       write code like this!
#

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Import the Emulab specific extensions.
import geni.rspec.emulab as emulab

# Create a portal object,
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()
portal.context.defineParameter("type","Type of nodes", portal.ParameterType.NODETYPE,"pc")
portal.context.defineParameter("bandwidth","Link Capacity of links", portal.ParameterType.BANDWIDTH,0)
portal.context.defineParameter("num_hops","Number of hops", portal.ParameterType.INTEGER,0)


params = portal.context.bindParameters()


# Node node-0
node_0 = request.RawPC('control')

node_0.hardware_type = params.type
# node_0.routable_control_ip = True
node_0.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
iface0_0 = node_0.addInterface('eth0', pg.IPv4Address('10.0.0.1','255.255.255.0'))

# Node node-1
node_1 = request.RawPC('client')
node_1.hardware_type = params.type
# node_1.routable_control_ip = True
node_1.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
iface1_0 = node_1.addInterface('eth0', pg.IPv4Address('10.0.0.2','255.255.255.0'))
iface1_1 = node_1.addInterface('eth1', pg.IPv4Address('192.168.0.1','255.255.255.0'))




# Node node-2
node_2 = request.RawPC('defense')
node_2.hardware_type = params.type
# node_2.routable_control_ip = True
node_2.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
iface2_0 = node_2.addInterface('eth0', pg.IPv4Address('192.168.0.2','255.255.255.0'))
iface2_1 = node_2.addInterface('eth1', pg.IPv4Address('192.168.0.3','255.255.255.0'))

 # Node node-3
'''node_3 = request.RawPC('server')

node_3.hardware_type = params.type
# node_3.routable_control_ip = True
node_3.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
iface3_0 = node_3.addInterface('eth0', pg.IPv4Address('192.168.0.4','255.255.255.0'))'''




    # Link link0
link0 = request.Link('link0')
if(params.bandwidth != 0):
    link0.bandwidth = params.bandwidth
link0.addInterface(iface0_0)
link0.addInterface(iface1_0)


# Link link1
link1 = request.Link('link1')
if(params.bandwidth != 0):
    link1.bandwidth = params.bandwidth
link1.addInterface(iface1_1)
link1.addInterface(iface2_0) 


 # Link link2
'''link2 = request.Link('link2')
if(params.bandwidth != 0):
    link2.bandwidth = params.bandwidth
link2.addInterface(iface2_1)
link2.addInterface(iface3_0)'''






    
# Print the generated rspec
pc.printRequestRSpec(request)