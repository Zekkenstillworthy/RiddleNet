"""
Networking 2 Course Content - COMPLETE RECREATION
Comprehensive structured content recreated from all modules
Date: June 11, 2025
Source: Modules 1-7 from Networking 2 folder
"""

def get_networking2_content():
    """
    Returns comprehensive content for Networking 2 course
    Organized by modules and lessons based on actual module files
    """
    return {
        # Module 1: Routing Fundamentals
        "net2_1.1": {
            "title": "Routing Fundamentals",
            "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-1.txt",
            "content": """
            <div class="lesson-content">
                <h2>Routing Fundamentals</h2>
                
                <div class="lesson-description">
                    <p>This lesson will discuss Routing fundamentals terminologies, principles, concept, application, 
                    advantages, and importance of routing in networking. Also, discuss the unfamiliar terms in networking 
                    and their functions and uses.</p>
                </div>
                
                <div class="learning-outcomes">
                    <h3>Learning Outcomes</h3>
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
                        <li>Explain what is routing</li>
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
                            <li>A routing table consists of directly connected networks and routes configured statically by the administrator or dynamically learned through a routing protocol</li>
                        </ul>
                    </div>
                    
                    <div class="lesson-section">
                        <h4>Connected and Local Routes</h4>
                        <ul>
                            <li>The administrator configures IP addresses on the router's interfaces</li>
                            <li>From IOS 15, local routes will also be added to the routing table</li>
                            <li>Local routes always have a /32 mask and show the IP address configured on the interface</li>
                        </ul>
                        
                        <div class="cli-command">
                            <h5>CLI Command</h5>
                            <code>show ip route</code>
                            <p>This command displays the current routing table</p>
                        </div>
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
                        <p>A default route is used when the router doesn't have a specific route to a destination network</p>
                    </div>
                </div>
            </div>
            """
        },
        
        # Module 2: Dynamic Routing Protocols
        "net2_2.1": {
            "title": "Dynamic Routing Protocols",
            "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-2.txt",
            "content": """
            <div class="lesson-content">
                <h2>Dynamic Routing Protocols</h2>
                
                <div class="lesson-description">
                    <p>This lesson will discuss Dynamic Routing Protocol terminologies, principles, concept, application, 
                    advantages, and importance of routing in networking. Also, discuss the unfamiliar terms in networking 
                    and their functions and uses.</p>
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
                            <li>When a routing protocol is used, routers automatically advertise their best paths to known networks to each other</li>
                            <li>Routers use this information to determine their own best path to the known destinations</li>
                            <li>When the state of the network changes, such as a link going down or a new subnet being added, the routers update each other</li>
                            <li>Routers will automatically calculate a new best path and update the routing table if the network changes</li>
                        </ul>
                    </div>
                    
                    <div class="lesson-section">
                        <h4>Summary Routes</h4>
                        <ul>
                            <li>Summary routes lead to less memory usage in routers as their routing tables contain less routes</li>
                            <li>They also lead to less CPU usage as changes in the network only affect other routers in the same area</li>
                        </ul>
                    </div>
                    
                    <div class="lesson-section">
                        <h4>Dynamic Routing Protocol Advantages</h4>
                        <ul>
                            <li>The routers automatically advertise available subnets to each other without the administrator having to manually enter every route on every router</li>
                            <li>If a subnet is added or removed the routers will automatically discover that and update their routing tables</li>
                            <li>If the best path to a subnet goes down routers automatically discover that and will calculate a new best path if one is available</li>
                        </ul>
                    </div>
                    
                    <div class="lesson-section">
                        <h4>Routing Protocol Types</h4>
                        <p>Routing protocols can be split into two main types:</p>
                        <ul>
                            <li>Interior gateway protocols (IGPs)</li>
                            <li>Exterior gateway protocols (EGPs)</li>
                        </ul>
                        
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
                            <li>A router only knows its directly connected neighbors and the lists of networks those neighbors have advertised</li>
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
        
        # Module 3: Routing Information Protocol (RIP)
        "net2_3.1": {
            "title": "Routing Information Protocol (RIP)",
            "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-3.txt",
            "content": """
            <div class="lesson-content">
                <h2>Routing Information Protocol (RIP)</h2>
                
                <div class="lesson-description">
                    <p>This lesson will discuss on RIP (Routing Information Protocol) a Distance Vector routing protocol 
                    with multiple scenarios, applicable in the real world network solution.</p>
                </div>
                
                <div class="learning-outcomes">
                    <h3>Intended Learning Outcomes</h3>
                    <p>Students should be able to meet the following intended learning outcomes:</p>
                    <ul>
                        <li>Learn and understand the Routing Information Protocol</li>
                        <li>To demonstrate the configuration of Routing Information Protocol</li>
                        <li>To identify the usage and importance of Routing Information Protocol on a corporate network</li>
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
                            <li>RIPv1 is a legacy protocol which is not typically used anymore</li>
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
                        
                        <div class="config-example">
                            <h5>Basic RIP Configuration</h5>
                            <pre><code>
Router(config)# router rip
Router(config-router)# version 2
Router(config-router)# network 192.168.1.0
Router(config-router)# network 10.0.0.0
Router(config-router)# no auto-summary
                            </code></pre>
                        </div>
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
                            <li><code>show ip protocols</code></li>
                            <li><code>show run | section rip</code></li>
                            <li><code>show ip route</code></li>
                            <li><code>show ip rip database</code></li>
                        </ul>
                    </div>
                    
                    <div class="lesson-section">
                        <h4>Passive Interfaces</h4>
                        <ul>
                            <li>Passive interfaces work differently in RIP than other routing protocols</li>
                            <li>With other routing protocols, a passive interface will not send out or listen for routing updates</li>
                            <li>In RIP, a passive interface does not send out updates but it does listen to incoming updates from other RIP speaking neighbors</li>
                            <li>The router can receive updates on the passive interface and use them in the routing table</li>
                        </ul>
                    </div>
                    
                    <div class="lesson-section">
                        <h4>RIP Default Timers</h4>
                        <ul>
                            <li><strong>Update:</strong> The router sends updates every 30 seconds</li>
                            <li><strong>Invalid:</strong> After no updates for 180 seconds the route becomes invalid</li>
                            <li><strong>Hold Down:</strong> The hold down timer is used to stabilize the network, it starts when the invalid timer completes. 180 seconds by default</li>
                            <li><strong>Flush:</strong> The route is flushed from the routing table after 240 seconds</li>
                        </ul>
                    </div>
                </div>
            </div>
            """
        },
        
        # Module 4: Enhanced Interior Gateway Routing Protocol (EIGRP)
        "net2_4.1": {
            "title": "Enhanced Interior Gateway Routing Protocol (EIGRP)",
            "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-4.txt",
            "content": """
            <div class="lesson-content">
                <h2>Enhanced Interior Gateway Routing Protocol (EIGRP)</h2>
                
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
                        <li>Understand how EIGRP achieves fast convergence time</li>
                        <li>Configure Enhanced Interior Gateway Routing Protocol</li>
                        <li>Understand the importance of Enhanced Interior Gateway Routing Protocol</li>
                        <li>Simulate different EIGRP scenarios</li>
                    </ul>
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
                        
                        <div class="config-example">
                            <h5>Basic EIGRP Configuration</h5>
                            <pre><code>
Router(config)# router eigrp 100
Router(config-router)# network 10.0.0.0 0.255.255.255
Router(config-router)# network 192.168.1.0 0.0.0.255
Router(config-router)# no auto-summary
                            </code></pre>
                        </div>
                    </div>
                    
                    <div class="lesson-section">
                        <h4>EIGRP Configuration – network</h4>
                        <ul>
                            <li>The network command uses a wildcard mask which is the inverse of a subnet mask</li>
                            <li>Subtract each octet in the subnet mask from 255 to calculate the wildcard mask</li>
                        </ul>
                        
                        <div class="wildcard-examples">
                            <h5>Wildcard Mask Examples</h5>
                            <ul>
                                <li>Subnet mask 255.255.255.0 = wildcard mask 0.0.0.255</li>
                                <li>Subnet mask 255.255.252.0 = wildcard mask 0.0.3.255</li>
                                <li>Subnet mask 255.255.255.252 = wildcard mask 0.0.0.3</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="lesson-section">
                        <h4>EIGRP Network Examples</h4>
                        
                        <div class="example-scenario">
                            <h5>Scenario 1: All interfaces fall within range</h5>
                            <ul>
                                <li>All interfaces fall within this range in our example</li>
                                <li>EIGRP will be enabled on all interfaces and the router will peer with adjacent EIGRP routers</li>
                                <li>Networks advertised: 10.1.0.0/24, 10.0.1.0/24, 10.0.2.0/24</li>
                                <li>10.0.0.0/8 is NOT advertised</li>
                            </ul>
                        </div>
                        
                        <div class="example-scenario">
                            <h5>Scenario 2: Specific interfaces</h5>
                            <ul>
                                <li>Interface FE1/0 and FE2/0 fall within this range, FE0/0 does not</li>
                                <li>EIGRP will be enabled on FE1/0 and FE2/0 and the router will peer with adjacent EIGRP routers</li>
                                <li>Networks advertised: 10.0.1.0/24, 10.0.2.0/24</li>
                                <li>10.1.0.0/24 is NOT advertised, 10.0.0.0/16 is NOT advertised</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="lesson-section">
                        <h4>EIGRP Verification Commands</h4>
                        <ul>
                            <li><code>show ip protocols</code></li>
                            <li><code>show run | section eigrp</code></li>
                            <li><code>show ip eigrp neighbors</code></li>
                            <li><code>show ip eigrp topology</code></li>
                            <li><code>show ip route</code></li>
                        </ul>
                    </div>
                    
                    <div class="lesson-section">
                        <h4>EIGRP Features</h4>
                        <ul>
                            <li><strong>DUAL Algorithm:</strong> Diffusing Update Algorithm ensures loop-free paths</li>
                            <li><strong>Composite Metric:</strong> Uses bandwidth, delay, reliability, load, and MTU</li>
                            <li><strong>Unequal Cost Load Balancing:</strong> Can balance traffic across paths of different costs</li>
                            <li><strong>Fast Convergence:</strong> Rapid response to network changes</li>
                            <li><strong>Incremental Updates:</strong> Only sends changes, not entire routing table</li>
                        </ul>
                    </div>
                </div>
            </div>
            """
        },
        
        # Module 5: Open Shortest Path First (OSPF)
        "net2_5.1": {
            "title": "Open Shortest Path First (OSPF)",
            "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-5.txt",
            "content": """
            <div class="lesson-content">
                <h2>Open Shortest Path First (OSPF)</h2>
                
                <div class="lesson-description">
                    <p>This lesson will discuss on OSPF (Open Shortest Path First) a Link State routing protocol 
                    with multiple scenarios, applicable in the real world network solution.</p>
                </div>
                
                <div class="learning-outcomes">
                    <h3>Intended Learning Outcomes</h3>
                    <p>Students should be able to meet the following intended learning outcomes:</p>
                    <ul>
                        <li>Learn and understand the Open Shortest Path First</li>
                        <li>To demonstrate the configuration of Open Shortest Path First</li>
                        <li>To identify the usage and importance of Open Shortest Path First on a corporate network</li>
                        <li>To simulate different scenarios in implementing Open Shortest Path First</li>
                    </ul>
                </div>
                
                <div class="lecture-guide">
                    <h3>Lecture Guide</h3>
                    
                    <div class="lesson-section">
                        <h4>OSPF Overview</h4>
                        <ul>
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
                            <li>It supports large networks and has always been an open standard</li>
                            <li>It is supported on all vendors equipment</li>
                            <li>EIGRP can be simpler to implement and troubleshoot</li>
                            <li>It was historically a Cisco proprietary protocol</li>
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
                            <li><strong>DBD (DataBase Description):</strong> Adjacent routers will tell each other the networks they know about with the DBD packet</li>
                            <li><strong>LSR (Link State Request):</strong> If a router is missing information about any of the networks in the received DBD, it will send the neighbour an LSR</li>
                            <li><strong>LSA (Link State Advertisement):</strong> A routing update</li>
                            <li><strong>LSU (Link State Update):</strong> Contains a list of LSA's which should be updated, used during flooding</li>
                            <li><strong>LSAck:</strong> Receiving routers acknowledge LSAs</li>
                        </ul>
                    </div>
                    
                    <div class="lesson-section">
                        <h4>OSPF Configuration – Process ID</h4>
                        <ul>
                            <li>Different interfaces on a router can run in different instances of OSPF</li>
                            <li>Different instances have different Link State Databases</li>
                            <li>Only one instance is typically configured on OSPF routers – multiple Process IDs are very rarely used</li>
                            <li>The Process ID is locally significant. It does not have to match on the neighbour router to form an adjacency</li>
                        </ul>
                        
                        <div class="config-example">
                            <h5>Basic OSPF Configuration</h5>
                            <pre><code>
Router(config)# router ospf 1
Router(config-router)# network 192.168.1.0 0.0.0.255 area 0
Router(config-router)# network 10.1.1.0 0.0.0.3 area 0
                            </code></pre>
                        </div>
                    </div>
                    
                    <div class="lesson-section">
                        <h4>OSPF Network Command</h4>
                        <p>The network command in OSPF specifies which interfaces participate in OSPF and which area they belong to.</p>
                        
                        <div class="network-examples">
                            <h5>Network Configuration Examples</h5>
                            <ul>
                                <li>OSPF will be enabled on FE1/0 and FE2/0 and the router will peer with adjacent OSPF routers</li>
                                <li>Networks advertised: 10.0.1.0/24, 10.0.2.0/24</li>
                                <li>10.1.0.0/24 is NOT advertised, 10.0.0.0/16 is NOT advertised</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="lesson-section">
                        <h4>OSPF Verification Commands</h4>
                        <ul>
                            <li><code>show run | section ospf</code></li>
                            <li><code>show ip ospf interface brief</code></li>
                            <li><code>show ip ospf neighbor</code></li>
                            <li><code>show ip ospf database</code></li>
                            <li><code>show ip route</code></li>
                        </ul>
                    </div>
                    
                    <div class="lesson-section">
                        <h4>OSPF Areas</h4>
                        <ul>
                            <li>OSPF networks can be divided into areas for better scalability</li>
                            <li>Area 0 is the backbone area</li>
                            <li>All other areas must connect to Area 0</li>
                            <li>Areas reduce the size of the Link State Database</li>
                            <li>Changes in one area don't affect other areas</li>
                        </ul>
                    </div>
                </div>
            </div>
            """
        },
        
        # Module 7: Advanced Routing Concepts
        "net2_7.1": {
            "title": "Advanced Routing Concepts",
            "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-7.txt",
            "content": """
            <div class="lesson-content">
                <h2>Advanced Routing Concepts</h2>
                
                <div class="lesson-description">
                    <p>This module covers advanced routing concepts including route redistribution, policy routing, 
                    and complex network scenarios.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Route Redistribution</h3>
                    <ul>
                        <li>Process of sharing routes between different routing protocols</li>
                        <li>Allows connectivity between networks using different IGPs</li>
                        <li>Requires careful planning to avoid routing loops</li>
                        <li>Administrative distance and metrics must be considered</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Administrative Distance</h3>
                    <p>Administrative Distance (AD) is used to rank routes from most preferred to least preferred:</p>
                    <ul>
                        <li>Connected interface: 0</li>
                        <li>Static route: 1</li>
                        <li>EIGRP: 90</li>
                        <li>OSPF: 110</li>
                        <li>RIP: 120</li>
                        <li>External EIGRP: 170</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Route Summarization</h3>
                    <ul>
                        <li>Reduces routing table size</li>
                        <li>Improves network stability</li>
                        <li>Reduces bandwidth usage for routing updates</li>
                        <li>Can be configured manually or automatically</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Load Balancing Techniques</h3>
                    
                    <div class="load-balancing-types">
                        <h4>Equal Cost Load Balancing</h4>
                        <ul>
                            <li>Traffic distributed across multiple paths with same cost</li>
                            <li>Supported by all routing protocols</li>
                            <li>Can be per-packet or per-destination</li>
                        </ul>
                        
                        <h4>Unequal Cost Load Balancing</h4>
                        <ul>
                            <li>Traffic distributed based on path metrics</li>
                            <li>Primarily supported by EIGRP</li>
                            <li>Uses variance command for configuration</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Network Troubleshooting</h3>
                    
                    <div class="troubleshooting-steps">
                        <h4>Systematic Approach</h4>
                        <ol>
                            <li>Verify physical connectivity</li>
                            <li>Check IP configuration</li>
                            <li>Test routing table entries</li>
                            <li>Verify routing protocol operation</li>
                            <li>Analyze traffic patterns</li>
                        </ol>
                    </div>
                    
                    <div class="troubleshooting-tools">
                        <h4>Common Troubleshooting Commands</h4>
                        <ul>
                            <li><code>ping</code> - Test connectivity</li>
                            <li><code>traceroute</code> - Trace packet path</li>
                            <li><code>show ip route</code> - View routing table</li>
                            <li><code>show ip protocols</code> - Check routing protocol status</li>
                            <li><code>show interfaces</code> - Verify interface status</li>
                            <li><code>debug ip routing</code> - Monitor routing updates</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Best Practices</h3>
                    <ul>
                        <li>Use consistent routing protocol throughout organization</li>
                        <li>Implement proper summarization strategies</li>
                        <li>Configure authentication for routing protocols</li>
                        <li>Monitor network performance regularly</li>
                        <li>Maintain detailed network documentation</li>
                        <li>Plan for redundancy and failover scenarios</li>
                    </ul>
                </div>
            </div>
            """
        }
    }

# Test the function
if __name__ == "__main__":
    content = get_networking2_content()
    print("Networking 2 Content Structure:")
    for key, lesson in content.items():
        print(f"- {key}: {lesson['title']}")
