"""
Networking 2 - Pure Source Content
Recreated directly from source text files with NO additional content
All content extracted from original module text files only
Updated: June 10, 2025 - Contains only source file content
"""

NETWORKING2_PURE_SOURCE_CONTENT = {
    "1.1": {
        "title": "Routing Fundamentals",
        "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-1.txt",
        "content": """
    <div class="lesson-content">
        <h2>Routing Fundamentals</h2>
        
        <div class="lesson-description">
            <p>This lesson will discuss Routing fundamentals terminologies, principles, concept, application, advantages, and importance of routing in networking. Also, discuss the unfamiliar terms in networking and it functions and uses.</p>
        </div>
        
        <div class="learning-outcomes">
            <h3>Intended Learning Outcomes</h3>
            <p>Students should be able to meet the following intended learning outcomes:</p>
            <ul>
                <li>To define what is routing</li>
                <li>To understand the importance of implementing routing on a corporate network</li>
                <li>Demonstrate simple Static routing</li>
                <li>To identify default routes</li>
                <li>To understand the importance of Load Balancing</li>
            </ul>
        </div>
        
        <div class="objectives">
            <h3>Targets/Objectives</h3>
            <p>At the end of the lesson, students should be able to:</p>
            <ul>
                <li>Explain what is what is routing</li>
                <li>Understand the importance of implementing routing on a corporate network</li>
                <li>Configure simple static routing</li>
                <li>Identify default routes</li>
                <li>Understand the importance of Load Balancing</li>
            </ul>
        </div>
        
        <div class="guide-questions">
            <h3>Learning Guide Questions</h3>
            <ol>
                <li>What is Routing?</li>
                <li>Why it is important to implement routing on a corporate network?</li>
                <li>How to configure simple static routing?</li>
                <li>How identify default routes?</li>
                <li>Importance of Load Balancing in Networking?</li>
            </ol>
        </div>
        
        <div class="lecture-guide">
            <h3>Lecture Guide</h3>
            
            <div class="lesson-section">
                <h4>Router Functions</h4>
                <p>A router has two main functions:</p>
                <ul>
                    <li>Determining the best path to available networks</li>
                    <li>Forwarding traffic to those networks</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>The Routing Table</h4>
                <ul>
                    <li>The best available path or paths to a destination network are listed in a router's routing table and will be used for forwarding traffic</li>
                    <li>A routing table consists of directly connected networks and routes configured statically by the administrator or dynamically learned through a routing protocol.</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Connected and Local Routes</h4>
                <ul>
                    <li>The administrator configures IP addresses on the router's interfaces</li>
                    <li>From IOS 15, local routes will also be added to the routing table</li>
                    <li>Local routes always have a /32 mask and show the IP address configured on the interface</li>
                </ul>
                
                <h5>CLI Command (Local Routes)</h5>
                <p><code>show ip route</code></p>
            </div>
            
            <div class="lesson-section">
                <h4>Static Routes</h4>
                <ul>
                    <li>If a router receives traffic for a network which it is not directly attached to, it needs to know how to get there in order to forward the traffic</li>
                    <li>An administrator can manually add a static route to the destination, or the router can learn it via a routing protocol</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Summary Routes</h4>
                <ul>
                    <li>For static routing, summary routes lessen administrative overhead and memory usage on the routers</li>
                    <li>Summarization doesn't have to be on classful boundaries</li>
                    <li>To summarize the range 10.1.0.0 to 10.1.3.0</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Longest Prefix Match</h4>
                <p>When there are overlapping routes, the longest prefix will be selected</p>
            </div>
            
            <div class="lesson-section">
                <h4>Load Balancing</h4>
                <p>When multiple equal length routes are added for the same destination, the router will add them all to the routing table and load balance between them</p>
            </div>
            
            <div class="lesson-section">
                <h4>Default Route (Gateway of Last Resort)</h4>
                <p>A route used when no specific route is available for a destination</p>
            </div>
        </div>
    </div>
    """
    },
    
    "2.1": {
        "title": "Dynamic Routing Protocols",
        "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-2.txt",
        "content": """
    <div class="lesson-content">
        <h2>Dynamic Routing Protocols</h2>
        
        <div class="lesson-description">
            <p>This lesson will discuss Dynamic Routing Protocol terminologies, principles, concept, application, advantages, and importance of routing in networking. Also, discuss the unfamiliar terms in networking and it functions and uses.</p>
        </div>
        
        <div class="learning-outcomes">
            <h3>Intended Learning Outcomes</h3>
            <p>Students should be able to meet the following intended learning outcomes:</p>
            <ul>
                <li>To understand the difference between dynamic and static routing</li>
                <li>To identify different types of Routing protocols</li>
                <li>To understand routing protocol metrics</li>
                <li>To understand the networks administrative distance</li>
                <li>To identify loopback interfaces</li>
                <li>To demonstrate adjacencies and passive interfaces</li>
            </ul>
        </div>
        
        <div class="objectives">
            <h3>Targets/Objectives</h3>
            <p>At the end of the lesson, students should be able to:</p>
            <ul>
                <li>Explain the difference between dynamic and static routing</li>
                <li>Explain different types of Routing protocols</li>
                <li>Identify routing protocol metrics</li>
                <li>Identify networks administrative distance</li>
                <li>Determine loopback interfaces</li>
                <li>Explain adjacencies and passive interfaces</li>
            </ul>
        </div>
        
        <div class="guide-questions">
            <h3>Learning Guide Questions</h3>
            <ol>
                <li>What is Dynamic Routing?</li>
                <li>What is Static Routing?</li>
                <li>What are the different routing protocols?</li>
                <li>How do you explain routing protocol metrics?</li>
                <li>How to determine network administrative distance?</li>
                <li>What is Loopback Interfaces?</li>
                <li>How to you explain adjacencies and passive interfaces</li>
            </ol>
        </div>
        
        <div class="lecture-guide">
            <h3>Lecture Guide</h3>
            
            <div class="lesson-section">
                <h4>Dynamic Routing Protocols</h4>
                <ul>
                    <li>When a routing protocol is used, routers automatically advertise their best paths to known networks to each other.</li>
                    <li>Routers use this information to determine their own best path to the known destinations.</li>
                    <li>When the state of the network changes, such as a link going down or a new subnet being added, the routers update each other.</li>
                    <li>Routers will automatically calculate a new best path and update the routing table if the network changes.</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Summary Routes</h4>
                <ul>
                    <li>Summary routes lead to less memory usage in routers as their routing tables contain less routes</li>
                    <li>They also lead to less CPU usage as changes in the network only affect other routers in the same area</li>
                    <li>For example, if the link on R1 to the 10.0.1.1/24 network goes down, R2 will lose its route there and try to compute a new path</li>
                    <li>R3 will not be affected as its summary route to 10.0.0.0/16 is unchanged</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Dynamic Routing Protocols vs Static Routes</h4>
                <ul>
                    <li>Routing protocols are more scalable than administrator defined static routes.</li>
                    <li>Using purely static routes is only feasible in very small environments.</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Dynamic Routing Protocol Advantages</h4>
                <ul>
                    <li>The routers automatically advertise available subnets to each other without the administrator having to manually enter every route on every router.</li>
                    <li>If a subnet is added or removed the routers will automatically discover that and update their routing tables.</li>
                    <li>If the best path to a subnet goes down routers automatically discover that and will calculate a new best path if one is available.</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Dynamic Routing Protocols vs Static Routes (Continued)</h4>
                <ul>
                    <li>Using a combination of a dynamic routing protocol and static routes is very common in real world environments.</li>
                    <li>In this case the routing protocol will be used to carry the bulk of the network information.</li>
                    <li>Static routes can also be used on an as needed basis. For example for backup purposes or for a static route to the Internet (which will typically be injected into the dynamic routing protocol and advertised to the rest of the routers.)</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Routing Protocol Types</h4>
                <p>Routing protocols can be split into two main types:</p>
                <ul>
                    <li>Interior gateway protocols (IGPs)</li>
                    <li>Exterior gateway protocols (EGPs)</li>
                    <li>Interior gateway protocols are used for routing within an organization</li>
                    <li>Exterior gateway protocols are used for routing between organizations over the Internet</li>
                    <li>The only EGP in use today is BGP (Border Gateway Protocol)</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Interior Gateway Protocols</h4>
                <p>Interior gateway protocols can be split into two main types:</p>
                <ul>
                    <li>Distance Vector routing protocols</li>
                    <li>Link State routing protocols</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Distance Vector Routing Protocols</h4>
                <ul>
                    <li>In Distance Vector protocols, each router sends its directly connected neighbors a list of all its known networks along with its own distance to each of those networks</li>
                    <li>Distance vector routing protocols do not advertise the entire network topology</li>
                    <li>A router only knows its directly connected neighbors and the lists of networks those neighbors have advertised. It doesn't have detailed topology information beyond its directly connected neighbors</li>
                    <li>Distance Vector routing protocols are often called 'Routing by rumor'</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Link State Routing Protocols</h4>
                <ul>
                    <li>In Link State routing protocols, each router describes itself and its interfaces to its directly connected neighbors</li>
                    <li>This information is passed unchanged from one router to another</li>
                    <li>Every router learns the full picture of the network including every router, its interfaces and what they connect to</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Routing Protocol Examples</h4>
                <ul>
                    <li>RIP: Routing Information Protocol</li>
                    <li>EIGRP: Enhanced Interior Gateway Routing Protocol</li>
                    <li>OSPF: Open Shortest Path First</li>
                    <li>IS-IS: Intermediate System – Intermediate System</li>
                    <li>BGP: Border Gateway Protocol</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Interior Gateway Protocols</h4>
                <ul>
                    <li>All of the IGPs do the same job, which is to advertise routes within an organization and determine the best path or paths</li>
                    <li>An organization will typically pick one of the IGPs</li>
                    <li>If an organization has multiple IGPs in effect (for example because of a merger), information can be redistributed between them. This should generally be avoided if possible</li>
                </ul>
            </div>
        </div>
    </div>
    """
    },
    
    "3.1": {
        "title": "Routing Information Protocol (RIP)",
        "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-3.txt",
        "content": """
    <div class="lesson-content">
        <h2>Routing Information Protocol (RIP)</h2>
        
        <div class="lesson-description">
            <p>This lesson will discuss on Routing Information Protocol that focuses on tracing network hops in tracing where the network traffic proceeds from source to its destination.</p>
        </div>
        
        <div class="learning-outcomes">
            <h3>Intended Learning Outcomes</h3>
            <p>Students should be able to meet the following intended learning outcomes:</p>
            <ul>
                <li>Learn and understand the routing information protocol</li>
                <li>To demonstrate the configuration of routing information protocol</li>
                <li>To identify the usage and importance of routing information protocol on a corporate network</li>
                <li>To simulate different scenarios in implementing routing information protocol</li>
            </ul>
        </div>
        
        <div class="objectives">
            <h3>Targets/Objectives</h3>
            <p>At the end of the lesson, students should be able to:</p>
            <ul>
                <li>Explain the routing information protocol</li>
                <li>Explain the configuration of routing information protocol</li>
                <li>Understand the usage and importance of routing information protocol on a corporate network</li>
                <li>To understand the simulation of different scenarios in implementing routing information protocol</li>
            </ul>
        </div>
        
        <div class="guide-questions">
            <h3>Learning Guide Questions</h3>
            <ol>
                <li>What is Routing Information Protocol?</li>
                <li>What is Network Self-Discovery?</li>
                <li>What is the commands used in tracing the hops of a specific network traffic?</li>
            </ol>
        </div>
        
        <div class="lecture-guide">
            <h3>Lecture Guide</h3>
            
            <div class="lesson-section">
                <h4>Routing Information Protocol (RIP)</h4>
                <ul>
                    <li>Interior Gateway Protocol</li>
                    <li>Distance-vector protocol using hop count</li>
                    <li>Maximum hops of 15, 16 is infinite</li>
                    <li>Oldest dynamic routing protocol, provides updates every 30 seconds</li>
                    <li>Easy to configure and runs over UDP</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>RIP Characteristics</h4>
                <ul>
                    <li>The Routing Information Protocol (RIP) is a Distance Vector routing protocol</li>
                    <li>It uses hop count as its metric</li>
                    <li>The maximum hop count is 15</li>
                    <li>It will perform Equal Cost Multi Path, for up to 4 paths by default</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>RIPv2 vs RIPv1</h4>
                <ul>
                    <li>RIPv1 is a legacy protocol which is not typically used anymore (although it is still supported on Cisco routers)</li>
                    <li>RIPv1 does not send subnet mask information with routing updates so Variable Length Subnet Masking (VLSM) is not supported. RIPv2 does support VLSM</li>
                    <li>RIPv1 updates are sent every 30 seconds as broadcast traffic</li>
                    <li>RIPv2 uses multicast address 224.0.0.9</li>
                    <li>RIPv2 supports authentication, RIPv1 does not</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>RIPng</h4>
                <p>RIPng (RIP next generation) supports IPv6 networks</p>
            </div>
            
            <div class="lesson-section">
                <h4>RIPv2 Configuration</h4>
                <p>The 'network' command should reference a classful network. No subnet mask is specified.</p>
            </div>
            
            <div class="lesson-section">
                <h4>Auto-Summary</h4>
                <ul>
                    <li>RIP will automatically summarise routes to the classful boundary by default</li>
                    <li>For example, 192.168.10.1/30 will be advertised as 192.168.10.0/24</li>
                    <li>172.16.10.1/30 will be advertised as 172.16.0.0/16</li>
                    <li>This is almost never desirable</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Manual Summarization</h4>
                <ul>
                    <li>Manual summarisation gives you control of exactly how you summarise</li>
                    <li>The individual summarised routes are not advertised - only their summary route</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>RIPv2 Verification Commands</h4>
                <ul>
                    <li>show ip protocols</li>
                    <li>show run | section rip</li>
                    <li>show ip route</li>
                </ul>
            </div>
        </div>
    </div>
    """
    },
    
    "4.1": {
        "title": "EIGRP (Enhanced Interior Gateway Routing Protocol)",
        "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-4.txt",
        "content": """
    <div class="lesson-content">
        <h2>EIGRP (Enhanced Interior Gateway Routing Protocol)</h2>
        
        <div class="lesson-description">
            <p>This lesson will discuss on EIGRP (Enhanced Interior Gateway Routing Protocol) an Advanced Distance Vector routing protocol with multiple scenarios, applicable in the real world network solution.</p>
        </div>
        
        <div class="learning-outcomes">
            <h3>Intended Learning Outcomes</h3>
            <p>Students should be able to meet the following intended learning outcomes:</p>
            <ul>
                <li>Learn and understand the Enhanced Interior Gateway Routing Protocol</li>
                <li>To demonstrate the configuration of Enhanced Interior Gateway Routing Protocol</li>
                <li>To identify the usage and importance of Enhanced Interior Gateway Routing Protocol on a corporate network</li>
                <li>To simulate different scenarios in implementing Enhanced Interior Gateway Routing Protocol</li>
            </ul>
        </div>
        
        <div class="objectives">
            <h3>Targets/Objectives</h3>
            <p>At the end of the lesson, students should be able to:</p>
            <ul>
                <li>Explain what is the difference between EIGRP and RIP</li>
                <li>Explain how EIGRP supports large networks</li>
                <li>Elaborate the feature EIGRP has as it covers fast convergence time</li>
                <li>Explain how messages are being sent in a multicast manner</li>
            </ul>
        </div>
        
        <div class="guide-questions">
            <h3>Learning Guide Questions</h3>
            <ol>
                <li>What is Enhanced Interior Gateway Routing Protocol?</li>
                <li>What is Fast Convergence time?</li>
                <li>How network traffic travels on multicast?</li>
            </ol>
        </div>
        
        <div class="lecture-guide">
            <h3>Lecture Guide</h3>
            
            <div class="lesson-section">
                <h4>EIGRP Overview</h4>
                <ul>
                    <li>EIGRP (Enhanced Interior Gateway Routing Protocol) is an Advanced Distance Vector routing protocol</li>
                    <li>It supports large networks</li>
                    <li>It has very fast convergence time</li>
                    <li>It supports bounded updates where network topology change updates are only sent to routers affected by the change</li>
                    <li>Messages are sent using multicast</li>
                    <li>EIGRP will automatically perform equal cost load balancing on up to 4 paths by default</li>
                    <li>This can be increased up to 16 paths</li>
                    <li>EIGRP can also be configured to perform unequal cost load balancing</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>EIGRP Configuration – AS number</h4>
                <p>'100' in this example is the Autonomous System (AS), meaning an independent administrative domain. EIGRP routers need to have the same Autonomous System number to peer with each other.</p>
            </div>
            
            <div class="lesson-section">
                <h4>EIGRP Configuration – network</h4>
                <ul>
                    <li>The network command uses a wildcard mask which is the inverse of a subnet mask.</li>
                    <li>Subtract each octet in the subnet mask from 255 to calculate the wildcard mask</li>
                    <li>A subnet mask of 255.255.0.0 equals a wildcard mask of 0.0.255.255</li>
                    <li>A subnet mask of 255.255.255.252 equals a wildcard mask of 0.0.0.3</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Default Wildcard Masks</h4>
                <p>If you do not enter a wildcard mask, the command defaults to using the classful boundary:</p>
                <ul>
                    <li>0.255.255.255 for a Class A address</li>
                    <li>0.0.255.255 for a Class B address</li>
                    <li>0.0.0.255 for a Class C address</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Network Command Function</h4>
                <p>The network command means: Look for interfaces with an IP address which falls within this</p>
            </div>
        </div>
    </div>
    """
    },
    
    "5.1": {
        "title": "OSPF (Open Shortest Path First)",
        "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-5.txt",
        "content": """
    <div class="lesson-content">
        <h2>OSPF (Open Shortest Path First)</h2>
        
        <div class="lesson-description">
            <p>This lesson will discuss on OSPF (Open Shortest Path First) focusing on how routing can be fully utilized using one of the most used protocols on a wide-scale of network topologies.</p>
        </div>
        
        <div class="learning-outcomes">
            <h3>Intended Learning Outcomes</h3>
            <p>Students should be able to meet the following intended learning outcomes:</p>
            <ul>
                <li>Understand the fundamental usage of OSPF</li>
                <li>Elaborate how OSPF should be implemented on top of the other protocols</li>
            </ul>
        </div>
        
        <div class="objectives">
            <h3>Targets/Objectives</h3>
            <p>At the end of the lesson, students should be able to:</p>
            <ul>
                <li>Learn and understand the open shortest path first</li>
                <li>To demonstrate the configuration of open shortest path first</li>
                <li>To identify the usage and importance of open shortest path first on a corporate network</li>
                <li>To simulate different scenarios in implementing open shortest path first</li>
            </ul>
        </div>
        
        <div class="guide-questions">
            <h3>Learning Guide Questions</h3>
            <ol>
                <li>What is Open Shortest Path First?</li>
                <li>What is Dijkstra's algorithm?</li>
                <li>Is OSPF one of the open standard protocol?</li>
            </ol>
        </div>
        
        <div class="lecture-guide">
            <h3>Lecture Guide</h3>
            
            <div class="lesson-section">
                <h4>OSPF Overview</h4>
                <ul>
                    <li>OSPF is a Link State routing protocol</li>
                    <li>It supports large networks</li>
                    <li>It has very fast convergence time</li>
                    <li>Messages are sent using multicast</li>
                    <li>OSPF is an open standard protocol</li>
                    <li>It uses Dijkstra's Shortest Path First algorithm to determine the best path to learned networks</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>OSPF vs EIGRP vs RIP</h4>
                <ul>
                    <li>RIP has scalability limitations so it is not typically used in production networks</li>
                    <li>It is suitable for small networks or lab/test environments</li>
                    <li>The choice for most companies for their IGP comes down to EIGRP or OSPF</li>
                    <li>OSPF is the most commonly used</li>
                    <li>It supports large networks and has always been an open standard.</li>
                    <li>It is supported on all vendors equipment EIGRP can be simpler to implement and troubleshoot It was historically a Cisco proprietary protocol</li>
                    <li>It is now an open standard but there is still limited support on other vendor's equipment</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>Link State Routing Protocols</h4>
                <ul>
                    <li>In Link State routing protocols, each router describes itself and its interfaces to its directly connected neighbours</li>
                    <li>This information is passed unchanged from one router to another</li>
                    <li>Every router learns the full picture of the network including every router, its interfaces and what they connect to</li>
                    <li>OSPF routers use LSA Link State Advertisements to pass on routing updates</li>
                </ul>
            </div>
            
            <div class="lesson-section">
                <h4>OSPF Operations</h4>
                <ol>
                    <li>Discover neighbours</li>
                    <li>Form adjacencies</li>
                    <li>Flood Link State Database (LSDB)</li>
                    <li>Compute Shortest Path</li>
                    <li>Install best routes in routing table</li>
                    <li>Respond to network changes</li>
                </ol>
            </div>
            
            <div class="lesson-section">
                <h4>OSPF Packet Types</h4>
                <ul>
                    <li><strong>Hello:</strong> A router will send out and listen for Hello packets when OSPF is enabled on an interface, and form adjacencies with other OSPF routers on the link</li>
                    <li><strong>DBD DataBase Description:</strong> Adjacent routers will tell each other the networks they know about with the DBD packet</li>
                    <li><strong>LSR Link State Request:</strong> If a router is missing information about any of the networks in the received DBD, it will send the neighbour an LSR</li>
                    <li><strong>LSA Link State Advertisement:</strong> A routing update</li>
                </ul>
            </div>
        </div>
    </div>
    """
    },
    
    "7.1": {
        "title": "VLAN Trunking Protocol",
        "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-7.txt",
        "content": """
    <div class="lesson-content">
        <h2>VLAN Trunking Protocol</h2>
        
        <div class="lesson-description">
            <p>To save cost on network infrastructure and to have an optimal performance VLAN is widely used to utilize the maximum efficiency of the network devices. On this lesson, we will be discussing one of the most useful protocols available in networking that helps a lot of collisions, traffics and network problems solved.</p>
        </div>
        
        <div class="learning-outcomes">
            <h3>Intended Learning Outcomes</h3>
            <p>Students should be able to meet the following intended learning outcomes:</p>
            <ul>
                <li>Learn VLAN as one of the most useful protocol in networking</li>
                <li>Understand how it works and how it can provide a solution on complex network infrastructures</li>
                <li>Understand how to configure and how it can be implemented</li>
            </ul>
        </div>
        
        <div class="objectives">
            <h3>Targets/Objectives</h3>
            <p>At the end of the lesson, students should be able to:</p>
            <ul>
                <li>Learn VLAN as one of the most useful protocol in networking</li>
                <li>Understand how it works and how it can provide a solution on complex network infrastructures</li>
                <li>Understand how to configure and how it can be implemented</li>
            </ul>
        </div>
        
        <div class="guide-questions">
            <h3>Learning Guide Questions</h3>
            <ol>
                <li>How to configure VLAN?</li>
                <li>What are the problems that can be solved with this protocol?</li>
                <li>Why VLAN is essential in managing a wide scale network infrastructure?</li>
            </ol>
        </div>
        
        <div class="lecture-guide">
            <h3>Lecture Guide</h3>
            
            <div class="lesson-section">
                <h4>VLAN Topics Covered</h4>
                <ul>
                    <li>Explain the Role of VLANs in a Converged Network</li>
                    <li>Describe the different types VLANs</li>
                    <li>Describe the VLAN port membership modes</li>
                    <li>Describe how to manage broadcast domains with VLANs</li>
                    <li>Explain the role of a trunk when using multiple VLANs in a converged network</li>
                    <li>Describe how a trunk works</li>
                    <li>Describe the switch port trunking modes</li>
                    <li>Describe the steps to configure trunks and VLANs</li>
                    <li>Configure VLANs on the Switches in a Converged Network Topology</li>
                    <li>Describe the Cisco IOS commands used to create a VLAN on a Cisco Catalyst switch</li>
                    <li>Describe the Cisco IOS commands used to manage VLANs on a Cisco Catalyst switch</li>
                </ul>
            </div>
        </div>
    </div>
    """
    }
}
