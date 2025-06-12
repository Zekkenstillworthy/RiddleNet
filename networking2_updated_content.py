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
            "description": "Comprehensive introduction to routing terminologies, principles, and concepts including static routing, load balancing, and corporate network implementation",
            "estimated_time": 90,
            "difficulty": "intermediate",
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
            "description": "Understanding dynamic routing protocols, types, metrics, and comparison with static routing implementations",
            "estimated_time": 75,
            "difficulty": "intermediate",
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
        
        # Module 6: Network Security and VPN
        "net2_6.1": {
            "title": "Network Security and VPN",
            "description": "Advanced network security fundamentals including CIA triad, firewall technologies, VPN implementations, and intrusion detection systems",
            "estimated_time": 150,
            "difficulty": "advanced",
            "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-6.txt",
            "content": """
            <div class="lesson-content">
                <h2>Network Security and VPN</h2>
                
                <div class="lesson-description">
                    <p>This lesson will discuss network security fundamentals, firewall implementations, VPN technologies, 
                    and intrusion detection systems for secure network communications.</p>
                </div>
                
                <div class="learning-outcomes">
                    <h3>Learning Outcomes</h3>
                    <p>Students should be able to meet the following intended learning outcomes:</p>
                    <ul>
                        <li>Understand network security principles and the CIA triad</li>
                        <li>Learn about different types of firewalls and their implementations</li>
                        <li>Explore VPN technologies and their applications</li>
                        <li>Understand intrusion detection and prevention systems</li>
                    </ul>
                </div>
                
                <div class="objectives">
                    <h3>Targets/Objectives</h3>
                    <p>At the end of the lesson, students should be able to:</p>
                    <ul>
                        <li>Explain fundamental network security concepts</li>
                        <li>Configure and implement firewall rules and policies</li>
                        <li>Set up and configure VPN connections</li>
                        <li>Deploy and monitor intrusion detection systems</li>
                        <li>Implement comprehensive network security strategies</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Network Security Fundamentals</h3>
                    
                    <h4>The CIA Triad</h4>
                    <p>The foundation of network security is built on three core principles:</p>
                    
                    <div class="subsection">
                        <h5>1. Confidentiality</h5>
                        <ul>
                            <li>Ensures that information is accessible only to authorized users</li>
                            <li>Implemented through encryption, access controls, and authentication</li>
                            <li>Protects sensitive data from unauthorized disclosure</li>
                        </ul>
                    </div>
                    
                    <div class="subsection">
                        <h5>2. Integrity</h5>
                        <ul>
                            <li>Maintains the accuracy and completeness of data</li>
                            <li>Prevents unauthorized modification of information</li>
                            <li>Uses digital signatures, hash functions, and checksums</li>
                        </ul>
                    </div>
                    
                    <div class="subsection">
                        <h5>3. Availability</h5>
                        <ul>
                            <li>Ensures that authorized users have access to information when needed</li>
                            <li>Protects against denial of service attacks</li>
                            <li>Implements redundancy and backup systems</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Security Threats and Vulnerabilities</h3>
                    <h4>Common Network Threats:</h4>
                    <ul>
                        <li>Malware (viruses, worms, trojans)</li>
                        <li>Denial of Service (DoS) attacks</li>
                        <li>Man-in-the-middle attacks</li>
                        <li>Social engineering</li>
                        <li>Password attacks</li>
                        <li>Network sniffing</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Firewall Technologies</h3>
                    
                    <h4>Types of Firewalls:</h4>
                    
                    <div class="subsection">
                        <h5>1. Packet Filtering Firewalls</h5>
                        <ul>
                            <li>Examine individual packets based on header information</li>
                            <li>Filter based on source/destination IP, ports, and protocols</li>
                            <li>Simple but limited in capability</li>
                        </ul>
                    </div>
                    
                    <div class="subsection">
                        <h5>2. Stateful Inspection Firewalls</h5>
                        <ul>
                            <li>Track the state of network connections</li>
                            <li>Make decisions based on connection context</li>
                            <li>More secure than packet filtering</li>
                        </ul>
                    </div>
                    
                    <div class="subsection">
                        <h5>3. Application Layer Firewalls</h5>
                        <ul>
                            <li>Inspect application-specific data</li>
                            <li>Can filter based on application content</li>
                            <li>Provide deep packet inspection capabilities</li>
                        </ul>
                    </div>
                    
                    <h4>Firewall Rules and Policies:</h4>
                    <ul>
                        <li>Default deny policy</li>
                        <li>Principle of least privilege</li>
                        <li>Regular review and updates</li>
                        <li>Logging and monitoring</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Virtual Private Networks (VPNs)</h3>
                    
                    <h4>VPN Types:</h4>
                    
                    <div class="subsection">
                        <h5>1. Site-to-Site VPNs</h5>
                        <ul>
                            <li>Connect entire networks together</li>
                            <li>Used for branch office connectivity</li>
                            <li>Transparent to end users</li>
                        </ul>
                    </div>
                    
                    <div class="subsection">
                        <h5>2. Remote Access VPNs</h5>
                        <ul>
                            <li>Allow individual users to connect remotely</li>
                            <li>Common for telecommuting</li>
                            <li>Require client software</li>
                        </ul>
                    </div>
                    
                    <h4>VPN Protocols:</h4>
                    <ul>
                        <li>IPSec (Internet Protocol Security)</li>
                        <li>SSL/TLS (Secure Sockets Layer/Transport Layer Security)</li>
                        <li>PPTP (Point-to-Point Tunneling Protocol)</li>
                        <li>L2TP (Layer 2 Tunneling Protocol)</li>
                    </ul>
                    
                    <h4>VPN Benefits:</h4>
                    <ul>
                        <li>Secure remote access</li>
                        <li>Cost-effective WAN connectivity</li>
                        <li>Data encryption and authentication</li>
                        <li>Network traffic concealment</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Intrusion Detection Systems</h3>
                    
                    <h4>IDS Types:</h4>
                    
                    <div class="subsection">
                        <h5>1. Network-based IDS (NIDS)</h5>
                        <ul>
                            <li>Monitors network traffic in real-time</li>
                            <li>Placed at strategic network points</li>
                            <li>Can detect network-based attacks</li>
                        </ul>
                    </div>
                    
                    <div class="subsection">
                        <h5>2. Host-based IDS (HIDS)</h5>
                        <ul>
                            <li>Monitors individual host systems</li>
                            <li>Examines system logs and file integrity</li>
                            <li>Detects host-specific attacks</li>
                        </ul>
                    </div>
                    
                    <h4>Detection Methods:</h4>
                    <ul>
                        <li>Signature-based detection (known attack patterns)</li>
                        <li>Anomaly-based detection (deviation from normal behavior)</li>
                        <li>Hybrid approaches combining both methods</li>
                    </ul>
                    
                    <h4>IDS vs IPS:</h4>
                    <ul>
                        <li>IDS: Detection and alerting only</li>
                        <li>IPS: Detection and automatic response/blocking</li>
                        <li>IPS can actively prevent attacks</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Security Best Practices</h3>
                    
                    <h4>Network Segmentation:</h4>
                    <ul>
                        <li>Use VLANs to separate network traffic</li>
                        <li>Implement DMZ for public-facing services</li>
                        <li>Isolate critical systems</li>
                    </ul>
                    
                    <h4>Access Control:</h4>
                    <ul>
                        <li>Strong authentication mechanisms</li>
                        <li>Role-based access control (RBAC)</li>
                        <li>Regular access reviews</li>
                    </ul>
                    
                    <h4>Monitoring and Logging:</h4>
                    <ul>
                        <li>Continuous network monitoring</li>
                        <li>Centralized log management</li>
                        <li>Security incident response procedures</li>
                    </ul>
                    
                    <h4>Regular Updates:</h4>
                    <ul>
                        <li>Keep systems and software updated</li>
                        <li>Apply security patches promptly</li>
                        <li>Update security policies and procedures</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Summary</h3>
                    <p>Network security is a multi-layered approach that requires:</p>
                    <ul>
                        <li>Understanding of security principles (CIA triad)</li>
                        <li>Implementation of appropriate security technologies</li>
                        <li>Regular monitoring and maintenance</li>
                        <li>Continuous education and awareness</li>
                    </ul>
                    
                    <p>Key security technologies include:</p>
                    <ul>
                        <li>Firewalls for traffic filtering</li>
                        <li>VPNs for secure communications</li>
                        <li>IDS/IPS for threat detection and prevention</li>
                        <li>Access control systems for user management</li>
                    </ul>
                    
                    <p>Effective network security requires a combination of technology, policies, and procedures to protect against evolving threats.</p>
                </div>
                
                <div class="assessment-section">
                    <h3>📝 Comprehensive Security Assessment</h3>
                    <div class="mcq-container">
                        <div class="mcq-question">
                            <h4>Question 1: Which component of the CIA triad ensures data hasn't been tampered with?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q1" value="a"> A) Confidentiality</label>
                                <label><input type="radio" name="q1" value="b"> B) Integrity</label>
                                <label><input type="radio" name="q1" value="c"> C) Availability</label>
                                <label><input type="radio" name="q1" value="d"> D) Authentication</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: B) Integrity</strong>
                                <p>Explanation: Integrity ensures data accuracy and prevents unauthorized modification through digital signatures, hash functions, and checksums.</p>
                            </div>
                        </div>
                        
                        <div class="mcq-question">
                            <h4>Question 2: Which firewall type provides the most comprehensive security inspection?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q2" value="a"> A) Packet filtering firewall</label>
                                <label><input type="radio" name="q2" value="b"> B) Stateful inspection firewall</label>
                                <label><input type="radio" name="q2" value="c"> C) Application layer firewall</label>
                                <label><input type="radio" name="q2" value="d"> D) Circuit-level gateway</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: C) Application layer firewall</strong>
                                <p>Explanation: Application layer firewalls inspect data at all OSI layers including application data, providing deep packet inspection capabilities.</p>
                            </div>
                        </div>
                        
                        <div class="mcq-question">
                            <h4>Question 3: What is the main advantage of SSL VPN over IPSec VPN for remote access?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q3" value="a"> A) Better encryption algorithms</label>
                                <label><input type="radio" name="q3" value="b"> B) No client software installation required</label>
                                <label><input type="radio" name="q3" value="c"> C) Faster data transmission</label>
                                <label><input type="radio" name="q3" value="d"> D) Lower implementation cost</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: B) No client software installation required</strong>
                                <p>Explanation: SSL VPNs provide browser-based access without requiring dedicated client software installation on user devices.</p>
                            </div>
                        </div>
                        
                        <div class="mcq-question">
                            <h4>Question 4: Which detection method is most effective for identifying zero-day attacks?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q4" value="a"> A) Signature-based detection</label>
                                <label><input type="radio" name="q4" value="b"> B) Anomaly-based detection</label>
                                <label><input type="radio" name="q4" value="c"> C) Rule-based detection</label>
                                <label><input type="radio" name="q4" value="d"> D) Blacklist-based detection</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: B) Anomaly-based detection</strong>
                                <p>Explanation: Anomaly-based detection identifies threats by detecting deviations from established baseline behavior patterns, making it effective against unknown attacks.</p>
                            </div>
                        </div>
                        
                        <div class="mcq-question">
                            <h4>Question 5: What is the primary difference between IDS and IPS systems?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q5" value="a"> A) IDS operates faster than IPS</label>
                                <label><input type="radio" name="q5" value="b"> B) IPS can actively block attacks while IDS only detects</label>
                                <label><input type="radio" name="q5" value="c"> C) IDS works at network layer, IPS at application layer</label>
                                <label><input type="radio" name="q5" value="d"> D) IPS is less expensive than IDS</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: B) IPS can actively block attacks while IDS only detects</strong>
                                <p>Explanation: IPS (Intrusion Prevention System) actively blocks threats in real-time, while IDS (Intrusion Detection System) only detects and alerts about threats.</p>
                            </div>
                        </div>
                        
                        <div class="mcq-question">
                            <h4>Question 6: Which VPN protocol is considered deprecated due to security vulnerabilities?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q6" value="a"> A) IPSec</label>
                                <label><input type="radio" name="q6" value="b"> B) SSL/TLS</label>
                                <label><input type="radio" name="q6" value="c"> C) L2TP</label>
                                <label><input type="radio" name="q6" value="d"> D) PPTP</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: D) PPTP</strong>
                                <p>Explanation: PPTP (Point-to-Point Tunneling Protocol) has known cryptographic vulnerabilities and is considered deprecated for security applications.</p>
                            </div>
                        </div>
                    </div>
                    
                    <button class="show-answers-btn" onclick="toggleAnswers()">Show Answers</button>
                    
                    <script>
                    function toggleAnswers() {
                        const answers = document.querySelectorAll('.mcq-answer');
                        const button = document.querySelector('.show-answers-btn');
                        
                        answers.forEach(answer => {
                            if (answer.style.display === 'none') {
                                answer.style.display = 'block';
                                button.textContent = 'Hide Answers';
                            } else {
                                answer.style.display = 'none';
                                button.textContent = 'Show Answers';
                            }
                        });
                    }
                    </script>
                </div>
            </div>
            """
        },
        
        # Module 7: Advanced Routing Concepts
        "net2_7.1": {
            "title": "Advanced Routing Concepts",
            "description": "Advanced routing topics including route redistribution, policy routing, and complex network troubleshooting scenarios",
            "estimated_time": 120,
            "difficulty": "advanced",
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
        },

        # Additional Module 1 Lessons
        "net2_1.2": {
            "title": "Dynamic Routing Protocols",
            "description": "Fundamentals of dynamic routing protocols and their automatic network maintenance capabilities",
            "estimated_time": 75,
            "difficulty": "intermediate",
            "content": """
            <div class="lesson-content">
                <h2>Dynamic Routing Protocols</h2>
                
                <div class="lesson-description">
                    <p>This lesson covers the fundamentals of dynamic routing protocols and how they automatically 
                    maintain routing tables in network infrastructures.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Overview of Dynamic Routing</h3>
                    <p>Dynamic routing protocols enable routers to automatically exchange routing information 
                    and adapt to network changes without manual intervention.</p>
                    
                    <ul>
                        <li>Automatic route discovery and maintenance</li>
                        <li>Adaptation to network topology changes</li>
                        <li>Reduced administrative overhead</li>
                        <li>Scalability for large networks</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Types of Dynamic Routing Protocols</h3>
                    
                    <div class="protocol-types">
                        <h4>Distance Vector Protocols</h4>
                        <ul>
                            <li>RIP (Routing Information Protocol)</li>
                            <li>Share routing table with neighbors</li>
                            <li>Use hop count as metric</li>
                        </ul>
                        
                        <h4>Link State Protocols</h4>
                        <ul>
                            <li>OSPF (Open Shortest Path First)</li>
                            <li>Maintain complete network topology</li>
                            <li>Use cost-based metrics</li>
                        </ul>
                        
                        <h4>Hybrid Protocols</h4>
                        <ul>
                            <li>EIGRP (Enhanced Interior Gateway Routing Protocol)</li>
                            <li>Combine benefits of both distance vector and link state</li>
                            <li>Fast convergence and efficient updates</li>
                        </ul>
                    </div>
                </div>
            </div>
            """
        },

        "net2_1.3": {
            "title": "Static vs Dynamic Routing",
            "description": "Comprehensive comparison between static and dynamic routing approaches with implementation considerations",
            "estimated_time": 60,
            "difficulty": "intermediate",
            "content": """
            <div class="lesson-content">
                <h2>Static vs Dynamic Routing Comparison</h2>
                
                <div class="lesson-description">
                    <p>Understanding the differences between static and dynamic routing helps in choosing 
                    the appropriate routing strategy for different network scenarios.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Static Routing</h3>
                    
                    <div class="routing-comparison">
                        <h4>Advantages</h4>
                        <ul>
                            <li>No bandwidth overhead for routing updates</li>
                            <li>Complete control over routing paths</li>
                            <li>Predictable routing behavior</li>
                            <li>Enhanced security</li>
                        </ul>
                        
                        <h4>Disadvantages</h4>
                        <ul>
                            <li>Manual configuration required</li>
                            <li>No automatic adaptation to failures</li>
                            <li>Difficult to maintain in large networks</li>
                            <li>Scaling challenges</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Dynamic Routing</h3>
                    
                    <div class="routing-comparison">
                        <h4>Advantages</h4>
                        <ul>
                            <li>Automatic route discovery</li>
                            <li>Self-healing capabilities</li>
                            <li>Scalable for large networks</li>
                            <li>Reduced administrative overhead</li>
                        </ul>
                        
                        <h4>Disadvantages</h4>
                        <ul>
                            <li>Bandwidth overhead for updates</li>
                            <li>Potential security vulnerabilities</li>
                            <li>Complexity in troubleshooting</li>
                            <li>Convergence time delays</li>
                        </ul>
                    </div>
                </div>
            </div>
            """
        },

        "net2_1.4": {
            "title": "Load Balancing",
            "description": "Load balancing techniques, equal-cost and unequal-cost implementations for optimal network performance",
            "estimated_time": 45,
            "difficulty": "intermediate",
            "content": """
            <div class="lesson-content">
                <h2>Load Balancing in Routing</h2>
                
                <div class="lesson-description">
                    <p>Load balancing allows traffic to be distributed across multiple paths, 
                    improving network performance and providing redundancy.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Equal Cost Load Balancing</h3>
                    <ul>
                        <li>Traffic distributed across paths with equal metrics</li>
                        <li>Supported by all routing protocols</li>
                        <li>Round-robin or per-destination distribution</li>
                        <li>Automatic failover to remaining paths</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Unequal Cost Load Balancing</h3>
                    <ul>
                        <li>Traffic distributed proportionally based on path metrics</li>
                        <li>Primarily supported by EIGRP</li>
                        <li>Uses variance command for configuration</li>
                        <li>More efficient utilization of available bandwidth</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Configuration Examples</h3>
                    <div class="code-block">
                        <pre>
! Equal Cost Load Balancing (automatic)
router ospf 1
  maximum-paths 4

! Unequal Cost Load Balancing (EIGRP)
router eigrp 100
  variance 2
                        </pre>
                    </div>
                </div>
            </div>
            """
        },

        # Module 2: Network Security Lessons
        "net2_2.1": {
            "title": "Security Principles",
            "content": """
            <div class="lesson-content">
                <h2>Network Security Principles</h2>
                
                <div class="lesson-description">
                    <p>Understanding the fundamental principles of network security is essential 
                    for implementing effective security measures in modern networks.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>CIA Triad</h3>
                    
                    <div class="security-principles">
                        <div class="principle">
                            <h4>Confidentiality</h4>
                            <p>Ensuring that information is accessible only to authorized users</p>
                            <ul>
                                <li>Data encryption</li>
                                <li>Access controls</li>
                                <li>Authentication mechanisms</li>
                            </ul>
                        </div>
                        
                        <div class="principle">
                            <h4>Integrity</h4>
                            <p>Maintaining the accuracy and completeness of data</p>
                            <ul>
                                <li>Digital signatures</li>
                                <li>Hash functions</li>
                                <li>Message authentication codes</li>
                            </ul>
                        </div>
                        
                        <div class="principle">
                            <h4>Availability</h4>
                            <p>Ensuring that authorized users have access when needed</p>
                            <ul>
                                <li>Redundancy and failover</li>
                                <li>DDoS protection</li>
                                <li>Regular maintenance and updates</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            """
        },

        "net2_2.2": {
            "title": "Firewall Implementation",
            "content": """
            <div class="lesson-content">
                <h2>Firewall Implementation</h2>
                
                <div class="lesson-description">
                    <p>Firewalls are critical security devices that control traffic flow between networks 
                    based on predefined security rules.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Types of Firewalls</h3>
                    
                    <div class="firewall-types">
                        <h4>Packet Filtering Firewalls</h4>
                        <ul>
                            <li>Examine individual packets</li>
                            <li>Filter based on IP addresses and ports</li>
                            <li>Stateless operation</li>
                        </ul>
                        
                        <h4>Stateful Inspection Firewalls</h4>
                        <ul>
                            <li>Track connection states</li>
                            <li>More sophisticated filtering</li>
                            <li>Better security than packet filtering</li>
                        </ul>
                        
                        <h4>Application Layer Firewalls</h4>
                        <ul>
                            <li>Deep packet inspection</li>
                            <li>Application-aware filtering</li>
                            <li>Content filtering capabilities</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Firewall Rules and Policies</h3>
                    <ul>
                        <li>Default deny policy</li>
                        <li>Least privilege principle</li>
                        <li>Regular rule review and updates</li>
                        <li>Logging and monitoring</li>
                    </ul>
                </div>
            </div>
            """
        },

        "net2_2.3": {
            "title": "VPN Technologies",
            "content": """
            <div class="lesson-content">
                <h2>Virtual Private Network (VPN) Technologies</h2>
                
                <div class="lesson-description">
                    <p>VPNs provide secure connectivity over public networks by creating 
                    encrypted tunnels between endpoints.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>VPN Types</h3>
                    
                    <div class="vpn-types">
                        <h4>Site-to-Site VPN</h4>
                        <ul>
                            <li>Connects entire networks</li>
                            <li>Permanent connection</li>
                            <li>IPSec commonly used</li>
                        </ul>
                        
                        <h4>Remote Access VPN</h4>
                        <ul>
                            <li>Individual user connections</li>
                            <li>On-demand connectivity</li>
                            <li>SSL/TLS or IPSec protocols</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>VPN Protocols</h3>
                    <ul>
                        <li><strong>IPSec:</strong> Layer 3 VPN with strong encryption</li>
                        <li><strong>SSL/TLS:</strong> Application layer VPN</li>
                        <li><strong>PPTP:</strong> Legacy protocol (not recommended)</li>
                        <li><strong>L2TP:</strong> Often combined with IPSec</li>
                    </ul>
                </div>
            </div>
            """
        },

        "net2_2.4": {
            "title": "Intrusion Detection",
            "content": """
            <div class="lesson-content">
                <h2>Intrusion Detection Systems</h2>
                
                <div class="lesson-description">
                    <p>Intrusion Detection Systems (IDS) monitor network traffic and systems 
                    for malicious activities and security policy violations.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Types of IDS</h3>
                    
                    <div class="ids-types">
                        <h4>Network-based IDS (NIDS)</h4>
                        <ul>
                            <li>Monitors network traffic</li>
                            <li>Placed at strategic network points</li>
                            <li>Real-time traffic analysis</li>
                        </ul>
                        
                        <h4>Host-based IDS (HIDS)</h4>
                        <ul>
                            <li>Monitors individual systems</li>
                            <li>Examines system logs and files</li>
                            <li>Detects local attacks</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Detection Methods</h3>
                    <ul>
                        <li><strong>Signature-based:</strong> Known attack patterns</li>
                        <li><strong>Anomaly-based:</strong> Deviation from normal behavior</li>
                        <li><strong>Hybrid:</strong> Combination of both methods</li>
                    </ul>
                </div>
            </div>
            """
        },

        # Module 3: Wireless Networks Lessons
        "net2_3.2": {
            "title": "WLAN Configuration",
            "content": """
            <div class="lesson-content">
                <h2>Wireless LAN Configuration</h2>
                
                <div class="lesson-description">
                    <p>Proper WLAN configuration is essential for optimal performance, 
                    security, and user experience in wireless networks.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Basic WLAN Setup</h3>
                    <ul>
                        <li>SSID configuration and broadcasting</li>
                        <li>Channel selection and planning</li>
                        <li>Power settings optimization</li>
                        <li>Authentication and encryption setup</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Advanced Configuration</h3>
                    <div class="advanced-config">
                        <h4>QoS and Traffic Management</h4>
                        <ul>
                            <li>WMM (Wi-Fi Multimedia) configuration</li>
                            <li>Bandwidth allocation</li>
                            <li>Traffic prioritization</li>
                        </ul>
                        
                        <h4>Roaming and Mobility</h4>
                        <ul>
                            <li>Seamless handoff configuration</li>
                            <li>Load balancing between APs</li>
                            <li>Fast BSS transition setup</li>
                        </ul>
                    </div>
                </div>
            </div>
            """
        },

        "net2_3.3": {
            "title": "Wireless Security",
            "content": """
            <div class="lesson-content">
                <h2>Wireless Network Security</h2>
                
                <div class="lesson-description">
                    <p>Securing wireless networks requires understanding various security protocols 
                    and implementing appropriate measures to protect against wireless-specific threats.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Wireless Security Protocols</h3>
                    
                    <div class="security-protocols">
                        <h4>WEP (Deprecated)</h4>
                        <ul>
                            <li>64-bit and 128-bit encryption</li>
                            <li>Significant security vulnerabilities</li>
                            <li>Should not be used</li>
                        </ul>
                        
                        <h4>WPA/WPA2</h4>
                        <ul>
                            <li>TKIP and AES encryption</li>
                            <li>PSK and Enterprise modes</li>
                            <li>Improved security over WEP</li>
                        </ul>
                        
                        <h4>WPA3</h4>
                        <ul>
                            <li>Enhanced encryption (192-bit)</li>
                            <li>SAE (Simultaneous Authentication of Equals)</li>
                            <li>Protection against offline attacks</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Additional Security Measures</h3>
                    <ul>
                        <li>MAC address filtering</li>
                        <li>Access point isolation</li>
                        <li>Guest network segmentation</li>
                        <li>Regular security audits</li>
                    </ul>
                </div>
            </div>
            """
        },

        "net2_3.4": {
            "title": "Troubleshooting Wireless",
            "content": """
            <div class="lesson-content">
                <h2>Wireless Network Troubleshooting</h2>
                
                <div class="lesson-description">
                    <p>Effective wireless troubleshooting requires systematic approaches 
                    to identify and resolve connectivity and performance issues.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Common Wireless Issues</h3>
                    <ul>
                        <li>Poor signal strength and coverage</li>
                        <li>Interference from other devices</li>
                        <li>Authentication and association failures</li>
                        <li>Slow data transfer rates</li>
                        <li>Intermittent connectivity</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Troubleshooting Tools</h3>
                    <div class="troubleshooting-tools">
                        <h4>Hardware Tools</h4>
                        <ul>
                            <li>Wi-Fi analyzers</li>
                            <li>Spectrum analyzers</li>
                            <li>Signal strength meters</li>
                        </ul>
                        
                        <h4>Software Tools</h4>
                        <ul>
                            <li>Site survey software</li>
                            <li>Network monitoring tools</li>
                            <li>Packet capture utilities</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Systematic Troubleshooting Process</h3>
                    <ol>
                        <li>Verify physical layer connectivity</li>
                        <li>Check signal strength and coverage</li>
                        <li>Analyze interference sources</li>
                        <li>Verify configuration settings</li>
                        <li>Test with different devices</li>
                        <li>Review logs and monitoring data</li>
                    </ol>
                </div>
            </div>
            """
        },

        # Module 4: Network Management Lessons  
        "net2_4.2": {
            "title": "SNMP Protocol",
            "content": """
            <div class="lesson-content">
                <h2>Simple Network Management Protocol (SNMP)</h2>
                
                <div class="lesson-description">
                    <p>SNMP is a standard protocol for network management that enables 
                    monitoring and control of network devices.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>SNMP Components</h3>
                    
                    <div class="snmp-components">
                        <h4>SNMP Manager</h4>
                        <ul>
                            <li>Central management station</li>
                            <li>Collects and processes management data</li>
                            <li>Sends commands to agents</li>
                        </ul>
                        
                        <h4>SNMP Agent</h4>
                        <ul>
                            <li>Software running on managed devices</li>
                            <li>Responds to manager requests</li>
                            <li>Sends trap notifications</li>
                        </ul>
                        
                        <h4>Management Information Base (MIB)</h4>
                        <ul>
                            <li>Database of manageable objects</li>
                            <li>Hierarchical structure</li>
                            <li>Object Identifiers (OIDs)</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>SNMP Versions</h3>
                    <ul>
                        <li><strong>SNMPv1:</strong> Original version, limited security</li>
                        <li><strong>SNMPv2c:</strong> Improved performance, community-based</li>
                        <li><strong>SNMPv3:</strong> Enhanced security with authentication and encryption</li>
                    </ul>
                </div>
            </div>
            """
        },

        "net2_4.3": {
            "title": "Performance Analysis",
            "content": """
            <div class="lesson-content">
                <h2>Network Performance Analysis</h2>
                
                <div class="lesson-description">
                    <p>Performance analysis involves measuring, monitoring, and optimizing 
                    network performance to ensure efficient operation.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Key Performance Metrics</h3>
                    
                    <div class="performance-metrics">
                        <h4>Bandwidth and Throughput</h4>
                        <ul>
                            <li>Available vs. utilized bandwidth</li>
                            <li>Peak and average throughput</li>
                            <li>Bandwidth utilization trends</li>
                        </ul>
                        
                        <h4>Latency and Delay</h4>
                        <ul>
                            <li>Round-trip time (RTT)</li>
                            <li>Processing delays</li>
                            <li>Queuing delays</li>
                        </ul>
                        
                        <h4>Reliability Metrics</h4>
                        <ul>
                            <li>Packet loss rates</li>
                            <li>Error rates</li>
                            <li>Availability percentages</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Performance Monitoring Tools</h3>
                    <ul>
                        <li>Network analyzers and packet captures</li>
                        <li>Flow monitoring (NetFlow, sFlow)</li>
                        <li>SNMP-based monitoring systems</li>
                        <li>Application performance monitoring</li>
                    </ul>
                </div>
            </div>
            """
        },

        "net2_4.4": {
            "title": "Network Documentation",
            "content": """
            <div class="lesson-content">
                <h2>Network Documentation</h2>
                
                <div class="lesson-description">
                    <p>Comprehensive network documentation is essential for effective 
                    network management, troubleshooting, and planning.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Types of Network Documentation</h3>
                    
                    <div class="documentation-types">
                        <h4>Physical Documentation</h4>
                        <ul>
                            <li>Network topology diagrams</li>
                            <li>Rack and cable layout</li>
                            <li>Equipment inventory</li>
                        </ul>
                        
                        <h4>Logical Documentation</h4>
                        <ul>
                            <li>IP addressing schemes</li>
                            <li>VLAN configurations</li>
                            <li>Routing protocols and policies</li>
                        </ul>
                        
                        <h4>Procedural Documentation</h4>
                        <ul>
                            <li>Configuration procedures</li>
                            <li>Troubleshooting guides</li>
                            <li>Change management processes</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Documentation Best Practices</h3>
                    <ul>
                        <li>Keep documentation current and accurate</li>
                        <li>Use standardized formats and symbols</li>
                        <li>Version control and change tracking</li>
                        <li>Accessibility and organization</li>
                        <li>Regular reviews and updates</li>
                    </ul>
                </div>
            </div>
            """
        },

        # Module 5: Advanced Routing/OSPF Lessons
        "net2_5.2": {
            "title": "OSPF Configuration",
            "content": """
            <div class="lesson-content">
                <h2>OSPF Configuration</h2>
                
                <div class="lesson-description">
                    <p>Configuring OSPF requires understanding the protocol's hierarchical design 
                    and proper implementation of areas, networks, and authentication.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Basic OSPF Configuration</h3>
                    <div class="code-block">
                        <pre>
! Enable OSPF process
router ospf 1
  router-id 1.1.1.1
  
! Configure networks
  network 192.168.1.0 0.0.0.255 area 0
  network 10.0.0.0 0.255.255.255 area 1
  
! Set passive interfaces
  passive-interface GigabitEthernet0/1
                        </pre>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>OSPF Authentication</h3>
                    <div class="code-block">
                        <pre>
! Area authentication
area 0 authentication message-digest

! Interface authentication
interface GigabitEthernet0/0
  ip ospf message-digest-key 1 md5 MyPassword
                        </pre>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Verification Commands</h3>
                    <ul>
                        <li><code>show ip ospf neighbor</code></li>
                        <li><code>show ip ospf database</code></li>
                        <li><code>show ip route ospf</code></li>
                        <li><code>show ip ospf interface</code></li>
                    </ul>
                </div>
            </div>
            """
        },

        "net2_5.3": {
            "title": "Area Design",
            "content": """
            <div class="lesson-content">
                <h2>OSPF Area Design</h2>
                
                <div class="lesson-description">
                    <p>Proper OSPF area design is crucial for scalability, performance, 
                    and efficient routing in large networks.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>OSPF Area Types</h3>
                    
                    <div class="area-types">
                        <h4>Backbone Area (Area 0)</h4>
                        <ul>
                            <li>Central area for inter-area routing</li>
                            <li>All other areas must connect to backbone</li>
                            <li>Contains ABRs and ASBRs</li>
                        </ul>
                        
                        <h4>Standard Areas</h4>
                        <ul>
                            <li>Accept all LSA types</li>
                            <li>Full routing information</li>
                            <li>Most flexible configuration</li>
                        </ul>
                        
                        <h4>Stub Areas</h4>
                        <ul>
                            <li>No external LSAs (Type 5)</li>
                            <li>Reduced LSDB size</li>
                            <li>Default route injection</li>
                        </ul>
                        
                        <h4>NSSA (Not-So-Stubby Areas)</h4>
                        <ul>
                            <li>Allow limited external routes</li>
                            <li>Type 7 LSAs converted to Type 5</li>
                            <li>Useful for branch offices</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Design Guidelines</h3>
                    <ul>
                        <li>Limit area size (50 routers maximum recommended)</li>
                        <li>Minimize inter-area traffic</li>
                        <li>Use hierarchical addressing</li>
                        <li>Consider redundant ABR placement</li>
                    </ul>
                </div>
            </div>
            """
        },

        "net2_5.4": {
            "title": "OSPF Troubleshooting",
            "content": """
            <div class="lesson-content">
                <h2>OSPF Troubleshooting</h2>
                
                <div class="lesson-description">
                    <p>Effective OSPF troubleshooting requires understanding common issues 
                    and systematic approaches to problem resolution.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Common OSPF Issues</h3>
                    
                    <div class="ospf-issues">
                        <h4>Neighbor Adjacency Problems</h4>
                        <ul>
                            <li>Hello/Dead timer mismatches</li>
                            <li>Area ID misconfigurations</li>
                            <li>Authentication failures</li>
                            <li>Network type mismatches</li>
                        </ul>
                        
                        <h4>Routing Issues</h4>
                        <ul>
                            <li>Missing routes in routing table</li>
                            <li>Suboptimal path selection</li>
                            <li>Area partitioning</li>
                            <li>LSA filtering problems</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Troubleshooting Steps</h3>
                    <ol>
                        <li>Verify physical connectivity</li>
                        <li>Check OSPF neighbor relationships</li>
                        <li>Examine OSPF database consistency</li>
                        <li>Verify area configurations</li>
                        <li>Check authentication settings</li>
                        <li>Analyze LSA propagation</li>
                    </ol>
                </div>
                
                <div class="lesson-section">
                    <h3>Debug Commands</h3>
                    <ul>
                        <li><code>debug ip ospf hello</code></li>
                        <li><code>debug ip ospf adj</code></li>
                        <li><code>debug ip ospf lsa-generation</code></li>
                        <li><code>debug ip ospf spf</code></li>
                    </ul>
                </div>
            </div>
            """
        },

        # Module 7: Network Troubleshooting Lessons
        "net2_7.2": {
            "title": "Network Diagnostic Tools",
            "content": """
            <div class="lesson-content">
                <h2>Network Diagnostic Tools</h2>
                
                <div class="lesson-description">
                    <p>Various diagnostic tools are available to help identify and resolve 
                    network issues efficiently and effectively.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Command-Line Tools</h3>
                    
                    <div class="diagnostic-tools">
                        <h4>Connectivity Testing</h4>
                        <ul>
                            <li><strong>ping:</strong> ICMP echo requests for basic connectivity</li>
                            <li><strong>traceroute:</strong> Path discovery and latency measurement</li>
                            <li><strong>pathping:</strong> Combined ping and traceroute functionality</li>
                        </ul>
                        
                        <h4>DNS and Name Resolution</h4>
                        <ul>
                            <li><strong>nslookup:</strong> DNS query and troubleshooting</li>
                            <li><strong>dig:</strong> Advanced DNS lookup tool</li>
                            <li><strong>host:</strong> Simple DNS lookup utility</li>
                        </ul>
                        
                        <h4>Network Configuration</h4>
                        <ul>
                            <li><strong>ipconfig/ifconfig:</strong> Interface configuration</li>
                            <li><strong>netstat:</strong> Network connections and statistics</li>
                            <li><strong>arp:</strong> ARP table viewing and manipulation</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Advanced Diagnostic Tools</h3>
                    <ul>
                        <li>Wireshark for packet analysis</li>
                        <li>SNMP monitoring tools</li>
                        <li>Network scanners (Nmap)</li>
                        <li>Bandwidth testing tools (iperf)</li>
                        <li>Network mapping utilities</li>
                    </ul>
                </div>
            </div>
            """
        },

        "net2_7.3": {
            "title": "Common Network Issues",
            "content": """
            <div class="lesson-content">
                <h2>Common Network Issues</h2>
                
                <div class="lesson-description">
                    <p>Understanding common network problems and their symptoms helps 
                    in quick identification and resolution of issues.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Physical Layer Issues</h3>
                    
                    <div class="network-issues">
                        <h4>Cable Problems</h4>
                        <ul>
                            <li>Damaged or loose cables</li>
                            <li>Incorrect cable types</li>
                            <li>Excessive cable length</li>
                            <li>Poor cable management</li>
                        </ul>
                        
                        <h4>Hardware Failures</h4>
                        <ul>
                            <li>Failed network interfaces</li>
                            <li>Power supply issues</li>
                            <li>Overheating components</li>
                            <li>Port malfunctions</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Logical Layer Issues</h3>
                    
                    <div class="logical-issues">
                        <h4>Configuration Problems</h4>
                        <ul>
                            <li>IP address conflicts</li>
                            <li>Incorrect subnet masks</li>
                            <li>Wrong default gateway</li>
                            <li>DNS misconfiguration</li>
                        </ul>
                        
                        <h4>Protocol Issues</h4>
                        <ul>
                            <li>Routing loops</li>
                            <li>VLAN misconfigurations</li>
                            <li>Spanning tree problems</li>
                            <li>DHCP issues</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Performance Issues</h3>
                    <ul>
                        <li>Bandwidth saturation</li>
                        <li>High latency and jitter</li>
                        <li>Packet loss</li>
                        <li>Application-specific problems</li>
                        <li>Security-related slowdowns</li>
                    </ul>
                </div>
            </div>
            """
        },

        "net2_7.4": {
            "title": "Advanced Troubleshooting",
            "content": """
            <div class="lesson-content">
                <h2>Advanced Troubleshooting Techniques</h2>
                
                <div class="lesson-description">
                    <p>Advanced troubleshooting involves sophisticated techniques and tools 
                    for complex network problems that require in-depth analysis.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Packet Analysis</h3>
                    
                    <div class="packet-analysis">
                        <h4>Capture Strategies</h4>
                        <ul>
                            <li>Strategic placement of capture points</li>
                            <li>Filtering to reduce capture size</li>
                            <li>Time-based captures for intermittent issues</li>
                            <li>Multi-point simultaneous captures</li>
                        </ul>
                        
                        <h4>Analysis Techniques</h4>
                        <ul>
                            <li>Protocol layer analysis</li>
                            <li>Traffic flow tracking</li>
                            <li>Error pattern identification</li>
                            <li>Performance bottleneck detection</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Baseline Analysis</h3>
                    <ul>
                        <li>Establishing performance baselines</li>
                        <li>Trend analysis and monitoring</li>
                        <li>Anomaly detection</li>
                        <li>Capacity planning insights</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Root Cause Analysis</h3>
                    <ol>
                        <li>Symptom identification and documentation</li>
                        <li>Data collection and correlation</li>
                        <li>Hypothesis formation and testing</li>
                        <li>Solution implementation and verification</li>
                        <li>Documentation and lessons learned</li>
                    </ol>
                </div>
                
                <div class="lesson-section">
                    <h3>Advanced Tools and Techniques</h3>
                    <ul>
                        <li>Network simulators and emulators</li>
                        <li>Traffic generators and load testing</li>
                        <li>Automated monitoring and alerting</li>
                        <li>Machine learning for anomaly detection</li>
                        <li>Correlation analysis across multiple data sources</li>
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
