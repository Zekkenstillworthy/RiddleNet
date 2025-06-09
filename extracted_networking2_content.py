# Extracted Networking 2 module content from .docx files
# Generated automatically by extract_networking2_modules.py

NETWORKING2_MODULE_CONTENT = {
    "1.1": {
        "title": "Advanced Network Protocols",
        "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-1.docx",
        "content": """
                <div class="lesson-content">
                    <h2>Advanced Network Protocols</h2>
                    
                    <div class="lesson-section">
                        <p>LSPU Self-Paced Learning Module (SLM)</p>
<p>Learning Outcomes</p>
<p>Student Learning Strategies</p>
<p>Performance Tasks</p>
<p>Understanding Directed Assess</p>
<p>Learning Resources</p>
<p>Course | ITEP 309 Networking 2</p>
<p>Sem/AY | First Semester/2020-2021</p>
<p>Module No. | 1</p>
<p>Lesson Title | Routing Fundamentals</p>
<p>Week Duration | 1</p>
<p>Date | Oct 5 to 9, 2020</p>
<p>Description of the Lesson | This lesson will discuss Routing fundamentals terminologies, principles, concept, application, advantages, and importance of routing in networking. Also, discuss the unfamiliar terms in networking and it functions and uses.</p>
<p>Intended Learning Outcomes | Students should be able to meet the following intended learning outcomes:</p>
<p>To define what is routing</p>
<p>To understand the importance of implementing routing on a corporate network</p>
<p>Demonstrate simple Static routing</p>
<p>To identify default routes</p>
<p>To understand the importance of Load Balancing</p>
<p>Targets/ Objectives | At the end of the lesson, students should be able to:</p>
<p>Explain what is what is routing</p>
<p>Understand the importance of implementing routing on a corporate network</p>
<p>Configure simple static routing</p>
<p>Identify default routes</p>
<p>Understand the importance of Load Balancing</p>
<p>Online Activities (Synchronous/</p>
<p>Asynchronous) | Lecture presentation uploaded in Google Classroom</p>
<p>Students will be instructed to download lecture presentations with narrations / pre-recorded lecture presentation uploaded in Google Classroom.</p>
<p>For further instructions, refer to your Google Classroom and see the schedule of activities for this module.</p>
<h4>Learning Guide Questions:</h4>
<p>What is Routing?</p>
<p>Why it is important to implement routing on a corporate network?</p>
<p>How to configure simple static routing?</p>
<p>How identify default routes?</p>
<p>Importance of Load Balancing in Networking?</p>
<p>Note: The insight that you will post on online discussion forum using Learning Management System (LMS) will receive additional scores in class participation.</p>
<p>Offline Activities</p>
<p>(e-Learning/Self-Paced) | Lecture Guide</p>
<p>Routing Fundamentals</p>
<p>Router Functions</p>
<p>A router has two main functions:</p>
<p>Determining the best path to available networks</p>
<p>Forwarding traffic to those networks</p>
<p>The Routing Table</p>
<p>The best available path or paths to a destination network are listed in a router’s routing table and will be used for forwarding traffic</p>
<p>A routing table consists of directly connected networks and routes configured statically by the administrator or dynamically learned through a routing protocol.</p>
<p>Connected and Local Routes</p>
<p>The administrator configures IP addresses on the router’s interfaces</p>
<p>CLI Command (Local Routes)</p>
<p>show ip route</p>
<p>From IOS 15, local routes will also be added to the routing table</p>
<p>Local routes always have a /32 mask and show the IP address configured on the interface</p>
<p>Static Routes</p>
<p>If a router receives traffic for a network which it is not directly attached to, it needs to know how to get there in order to forward the traffic</p>
<p>An administrator can manually add a static route to the destination, or the router can learn it via a routing protocol</p>
<p>Example Infrastructure</p>
<p>Static Routes</p>
<p>Routes on router 1</p>
<p>Summary Routes</p>
<p>For static routing, summary routes lessen administrative overhead and memory usage on the routers</p>
<h4>Routes on R1:</h4>
<p>Summary Routes</p>
<p>Summarization doesn’t have to be on classful boundaries</p>
<p>To summarize the range 10.1.0.0 to 10.1.3.0:</p>
<p>Longest Prefix Match</p>
<p>When there are overlapping routes, the longest prefix will be selected</p>
<p>Load Balancing</p>
<p>When multiple equal length routes are added for the same destination, the router will add them all to the routing table and load balance between them</p>
<p>Default Route (Gateway of Last Resort)</p>
<p>Laboratory Topology</p>
<p>Engaging Activities</p>
<p>What is your understanding about Routing?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>Why it is very important to configure and implement routing on a large-scale or corporate network?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>How do you define load balancing?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>How do you identify default route?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>What is the primary role of a load balancer in a network?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>Performance Task 2</p>
<p>Direction: list down terminologies in networking infrastructure and its uses in your own idea or explanation.</p>
<p>https://www.flackbox.com/cisco-ccna-lab-options</p>
<p>https://www.flackbox.com/#elementor-action%3Aaction%3Dpopup%3Aopen%26settings%3DeyJpZCI6IjEwMzk4IiwidG9nZ2xlIjpmYWxzZX0%3D</p>
<p>https://www.udemy.com/course/networkplus/</p>
                    </div>
                    
                    <div class="info-box">
                        <h4>Key Concept</h4>
                        <p>This content covers advanced networking concepts. Practice exercises and interactive simulations are available in the lab sections.</p>
                    </div>
                </div>
            """
    },
    "2.1": {
        "title": "Network Security Fundamentals",
        "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-2.docx",
        "content": """
                <div class="lesson-content">
                    <h2>Network Security Fundamentals</h2>
                    
                    <div class="lesson-section">
                        <p>LSPU Self-Paced Learning Module (SLM)</p>
<p>Learning Outcomes</p>
<p>Student Learning Strategies</p>
<p>Performance Tasks</p>
<p>Understanding Directed Assess</p>
<p>Learning Resources</p>
<p>Course | ITEP 309 Networking 2</p>
<p>Sem/AY | First Semester/2020-2021</p>
<p>Module No. | 2</p>
<p>Lesson Title | Routing Fundamentals</p>
<p>Week Duration | 2-3</p>
<p>Date | Oct 12 to 23, 2020</p>
<p>Description of the Lesson | This lesson will discuss Dynamic Routing Protocol terminologies, principles, concept, application, advantages, and importance of routing in networking. Also, discuss the unfamiliar terms in networking and it functions and uses.</p>
<p>Intended Learning Outcomes | Students should be able to meet the following intended learning outcomes:</p>
<p>To understand the difference between dynamic and static routing</p>
<p>To identify different types of Routing protocols</p>
<p>To understand routing protocol metrics</p>
<p>To understand the networks administrative distance</p>
<p>To identify loopback interfaces</p>
<p>To demonstrate adjacencies and passive interfaces</p>
<p>Targets/ Objectives | At the end of the lesson, students should be able to:</p>
<p>Explain the difference between dynamic and static routing</p>
<p>Explain different types of Routing protocols</p>
<p>Identify routing protocol metrics</p>
<p>Identify networks administrative distance</p>
<p>Determine loopback interfaces</p>
<p>Explain adjacencies and passive interfaces</p>
<p>Online Activities (Synchronous/</p>
<p>Asynchronous) | Lecture presentation uploaded in Google Classroom</p>
<p>Students will be instructed to download lecture presentations with narrations / pre-recorded lecture presentation uploaded in Google Classroom.</p>
<p>For further instructions, refer to your Google Classroom and see the schedule of activities for this module.</p>
<h4>Learning Guide Questions:</h4>
<p>What is Dynamic Routing?</p>
<p>What is Static Routing?</p>
<p>What are the different routing protocols?</p>
<p>How do you explain routing protocol metrics?</p>
<p>How to determine network administrative distance?</p>
<p>What is Loopback Interfaces?</p>
<p>How to you explain adjacencies and passive interfaces</p>
<p>Note: The insight that you will post on online discussion forum using Learning Management System (LMS) will receive additional scores in class participation.</p>
<p>Offline Activities</p>
<p>(e-Learning/Self-Paced) | Lecture Guide</p>
<p>Dynamic Routing Protocols</p>
<p>When a routing protocol is used, routers automatically advertise their best paths to known networks to each other.</p>
<p>Routers use this information to determine their own best path to the known destinations.</p>
<p>When the state of the network changes, such as a link going down or a new subnet being added, the routers update each other.</p>
<p>Routers will automatically calculate a new best path and update the routing table if the network changes.</p>
<p>Summary Routes</p>
<p>Summary routes lead to less memory usage in routers as their routing tables contain less routes</p>
<p>They also lead to less CPU usage as changes in the network only affect other routers in the same area</p>
<p>For example, if the link on R1 to the 10.0.1.1/24 network goes down, R2 will lose its route there and try to compute a new path</p>
<p>R3 will not be affected as its summary route to 10.0.0.0/16 is unchanged</p>
<p>Dynamic Routing Protocols vs Static Routes</p>
<p>Routing protocols are more scalable than administrator defined static routes.</p>
<p>Using purely static routes is only feasible in very small environments.</p>
<p>Dynamic Routing Protocol Advantages</p>
<p>The routers automatically advertise available subnets to each other without the administrator having to manually enter every route on every router.</p>
<p>If a subnet is added or removed the routers will automatically discover that and update their routing tables.</p>
<p>If the best path to a subnet goes down routers automatically discover that and will calculate a new best path if one is available.</p>
<p>Dynamic Routing Protocols vs Static Routes</p>
<p>Using a combination of a dynamic routing protocol and static routes is very common in real world environments.</p>
<p>In this case the routing protocol will be used to carry the bulk of the network information.</p>
<p>Static routes can also be used on an as needed basis. For example for backup purposes or for a static route to the Internet (which will typically be injected into the dynamic routing protocol and advertised to the rest of the routers.)</p>
<p>Laboratory Infrastructure</p>
<p>Routing Protocol Types</p>
<p>Routing protocols can be split into two main types:</p>
<p>Interior gateway protocols (IGPs)</p>
<p>Exterior gateway protocols (EGPs)</p>
<p>Interior gateway protocols are used for routing within an organization</p>
<p>Exterior gateway protocols are used for routing between organizations over the Internet</p>
<p>The only EGP in use today is BGP (Border Gateway Protocol)</p>
<p>Interior Gateway Protocols</p>
<p>Interior gateway protocols can be split into two main types:</p>
<p>Distance Vector routing protocols</p>
<p>Link State routing protocols</p>
<p>Distance Vector Routing Protocols</p>
<p>In Distance Vector protocols, each router sends its directly connected neighbors a list of all its known networks along with its own distance to each of those networks</p>
<p>Distance vector routing protocols do not advertise the entire network topology</p>
<p>A router only knows its directly connected neighbors and the lists of networks those neighbors have advertised. It doesn’t have detailed topology information beyond its directly connected neighbors</p>
<p>Distance Vector routing protocols are often called ‘Routing by rumor’</p>
<p>Link State Routing Protocols</p>
<p>In Link State routing protocols, each router describes itself and its interfaces to its directly connected neighbors</p>
<p>This information is passed unchanged from one router to another</p>
<p>Every router learns the full picture of the network including every router, its interfaces and what they connect to</p>
<p>RIP: Routing Information Protocol</p>
<p>EIGRP: Enhanced Interior Gateway Routing Protocol</p>
<p>OSPF: Open Shortest Path First</p>
<p>IS-IS: Intermediate System – Intermediate System</p>
<p>BGP: Border Gateway Protocol</p>
<p>Interior Gateway Protocols</p>
<p>All of the IGPs do the same job, which is to advertise routes within an organization and determine the best path or paths</p>
<p>An organization will typically pick one of the IGPs</p>
<p>If an organization has multiple IGPs in effect (for example because of a merger), information can be redistributed between them. This should generally be avoided if possible</p>
<p>Engaging Activities</p>
<p>What are your understanding about Static and Dynamic Routing?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>What is the most common type of routing protocol?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>How do you define administrative distance?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>How do you identify default route?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>How do you define loopback interfaces?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>Performance Task 2</p>
<p>Direction: list down terminologies in todays lesson that you find difficult to understand.</p>
<p>https://www.flackbox.com/cisco-ccna-lab-options</p>
<p>https://www.flackbox.com/#elementor-action%3Aaction%3Dpopup%3Aopen%26settings%3DeyJpZCI6IjEwMzk4IiwidG9nZ2xlIjpmYWxzZX0%3D</p>
<p>https://www.udemy.com/course/networkplus/</p>
                    </div>
                    
                    <div class="info-box">
                        <h4>Key Concept</h4>
                        <p>This content covers advanced networking concepts. Practice exercises and interactive simulations are available in the lab sections.</p>
                    </div>
                </div>
            """
    },
    "3.1": {
        "title": "Wireless Networks and Technologies",
        "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-3.docx",
        "content": """
                <div class="lesson-content">
                    <h2>Wireless Networks and Technologies</h2>
                    
                    <div class="lesson-section">
                        <p>LSPU Self-Paced Learning Module (SLM)</p>
<p>Learning Outcomes</p>
<p>Student Learning Strategies</p>
<p>Performance Tasks</p>
<p>Understanding Directed Assess</p>
<p>Learning Resources</p>
<p>Course | ITEP 309 Networking 2</p>
<p>Sem/AY | First Semester/2020-2021</p>
<p>Module No. | 3</p>
<p>Lesson Title | Routing Information Protocol</p>
<p>Week Duration | 4-5</p>
<p>Date | Oct 26 to November 06, 2020</p>
<p>Description of the Lesson | This lesson will discuss on Routing Information Protocol that focuses on tracing network hops in tracing where the network traffic proceeds from source to its destination.</p>
<p>Intended Learning Outcomes | Students should be able to meet the following intended learning outcomes:</p>
<p>Learn and understand the routing information protocol</p>
<p>To demonstrate the configuration of routing information protocol</p>
<p>To identify the usage and importance of routing information protocol on a corporate network</p>
<p>To simulate different scenarios in implementing routing information protocol</p>
<p>Targets/ Objectives | At the end of the lesson, students should be able to:</p>
<p>Explain the routing information protocol</p>
<p>Explain the configuration of routing information protocol</p>
<p>Understand the usage and importance of routing information protocol on a corporate network</p>
<p>To understand the simulation of different scenarios in implementing routing information protocol</p>
<p>Online Activities (Synchronous/</p>
<p>Asynchronous) | Lecture presentation uploaded in Google Classroom</p>
<p>Students will be instructed to download lecture presentations with narrations / pre-recorded lecture presentation uploaded in Google Classroom.</p>
<p>For further instructions, refer to your Google Classroom and see the schedule of activities for this module.</p>
<h4>Learning Guide Questions:</h4>
<p>What is Routing Information Protocol?</p>
<p>What is Network Self-Discovery?</p>
<p>What is the commands used in tracing the hops of a specific network traffic?</p>
<p>Note: The insight that you will post on online discussion forum using Learning Management System (LMS) will receive additional scores in class participation.</p>
<p>Offline Activities</p>
<p>(e-Learning/Self-Paced) | Lecture Guide</p>
<p>Routing Information Protocol (RIP)</p>
<p>▪ Interior Gateway Protocol</p>
<p>▪ Distance-vector protocol using hop count</p>
<p>▪ Maximum hops of 15, 16 is infinite</p>
<p>▪ Oldest dynamic routing protocol, provides updates every 30 seconds</p>
<p>▪ Easy to configure and runs over UDP</p>
<p>RIP Characteristics</p>
<p>The Routing Information Protocol (RIP) is a Distance Vector routing protocol</p>
<p>It uses hop count as its metric</p>
<p>The maximum hop count is 15</p>
<p>It will perform Equal Cost Multi Path, for up to 4 paths by default</p>
<p>RIPv2 vs RIPv1</p>
<p>RIPv1 is a legacy protocol which is not typically used anymore (although it is still supported on Cisco routers)</p>
<p>RIPv1 does not send subnet mask information with routing updates so Variable</p>
<p>Length Subnet Masking (VLSM) is not supported. RIPv2 does support VLSM</p>
<p>RIPv1 updates are sent every 30 seconds as broadcast traffic</p>
<p>RIPv2 uses multicast address 224.0.0.9 RIPv2 supports authentication, RIPv1 does not</p>
<p>RIPng</p>
<p>RIPng (RIP next generation) supports IPv6 networks</p>
<p>RIPv2 Configuration</p>
<p>The ‘network’ command should reference a classful network. No subnet mask is specified.</p>
<p>Auto-Summary</p>
<p>RIP will automatically summarise routes to the classful boundary by default</p>
<p>For example, 192.168.10.1/30 will be advertised as 192.168.10.0/24</p>
<li>172.16.10.1/30 will be advertised as 172.16.0.0/16</li>
<p>This is almost never desirable</p>
<p>Manual Summarization</p>
<p>Manual summarisation gives you control of exactly how you summarise</p>
<p>The individual summarised routes are not advertised - only their summary route</p>
<p>RIPv2 Verification – show ip protocols</p>
<p>RIPv2 Verification – show run | section rip</p>
<p>RIPv2 Verification – show ip route</p>
<p>RIPv2 Verification – show ip rip database</p>
<p>Passive Interfaces</p>
<p>Passive interfaces work differently in RIP than other routing protocols</p>
<p>With other routing protocols, a passive interface will not send out or listen for routing updates</p>
<p>The network configured on the interface will be advertised to other peer routers running the routing protocol</p>
<p>In RIP, a passive interface does not send out updates but it does listen to incoming updates from other RIP speaking neighbors</p>
<p>The router can receive updates on the passive interface and use them in the routing table.</p>
<p>Default Route Injection</p>
<p>Default Route Injection Verification</p>
<p>RIP Default Timers</p>
<p>Update: The router sends updates every 30 seconds.</p>
<p>Invalid: After no updates for 180 seconds the route becomes invalid.</p>
<p>Hold Down: The hold down timer is used to stabilize the network, it starts when the invalid timer completes. When a route enters hold down, it can't be installed even if there is a new route with a better metric. 180 seconds by default.</p>
<p>Flush: 240 seconds from the last update the route is flushed.</p>
<p>The timers can be changed to achieve faster convergence times</p>
<p>Be careful with this as it can introduce instability if the timers are set too low</p>
<p>All routers in the network should have the same timer settings</p>
<p>The update timer must be lower than the other timers.</p>
<p>Sample Laboratory Infrastructure</p>
<p>Engaging Activities</p>
<p>How do you define Routing Information Protocol?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>How do you explain network hops?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>How do you check for directly connected interfaces?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>How do you trigger the Routing Information Protocol auto summary?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>How do you check how many hops it will take for the source to reach the destination?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>Performance Task 2</p>
<p>Direction: Provide a one-liner explanation for the terminologies listed below.</p>
<p>https://www.flackbox.com/cisco-ccna-lab-options</p>
<p>https://www.flackbox.com/#elementor-action%3Aaction%3Dpopup%3Aopen%26settings%3DeyJpZCI6IjEwMzk4IiwidG9nZ2xlIjpmYWxzZX0%3D</p>
<p>https://www.udemy.com/course/networkplus/</p>
                    </div>
                    
                    <div class="info-box">
                        <h4>Key Concept</h4>
                        <p>This content covers advanced networking concepts. Practice exercises and interactive simulations are available in the lab sections.</p>
                    </div>
                </div>
            """
    },
    "4.1": {
        "title": "Network Management and Monitoring",
        "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-4.docx",
        "content": """
                <div class="lesson-content">
                    <h2>Network Management and Monitoring</h2>
                    
                    <div class="lesson-section">
                        <p>LSPU Self-Paced Learning Module (SLM)</p>
<p>Learning Outcomes</p>
<p>Student Learning Strategies</p>
<p>Performance Tasks</p>
<p>Understanding Directed Assess</p>
<p>Learning Resources</p>
<p>Course | ITEP 309 Networking 2</p>
<p>Sem/AY | First Semester/2020-2021</p>
<p>Module No. | 4</p>
<p>Lesson Title | EIGRP</p>
<p>Week Duration | 6-7</p>
<p>Date | November 09-20, 2020</p>
<p>Description of the Lesson | This lesson will discuss on EIGRP (Enhanced Interior Gateway Routing Protocol) an Advanced Distance Vector routing protocol with multiple scenarios, applicable in the real world network solution.</p>
<p>Intended Learning Outcomes | Students should be able to meet the following intended learning outcomes:</p>
<p>Learn and understand the Enhanced Interior Gateway Routing Protocol</p>
<p>To demonstrate the configuration of Enhanced Interior Gateway Routing Protocol</p>
<p>To identify the usage and importance of Enhanced Interior Gateway Routing Protocol on a corporate network</p>
<p>To simulate different scenarios in implementing Enhanced Interior Gateway Routing Protocol</p>
<p>Targets/ Objectives | At the end of the lesson, students should be able to:</p>
<p>Explain what is the difference between EIGRP and RIP</p>
<p>Explain how EIGRP supports large networks</p>
<p>Elaborate the feature EIGRP has as it covers fast convergence time</p>
<p>Explain how messages are being sent in a multicast manner</p>
<p>Online Activities (Synchronous/</p>
<p>Asynchronous) | Lecture presentation uploaded in Google Classroom</p>
<p>Students will be instructed to download lecture presentations with narrations / pre-recorded lecture presentation uploaded in Google Classroom.</p>
<p>For further instructions, refer to your Google Classroom and see the schedule of activities for this module.</p>
<h4>Learning Guide Questions:</h4>
<p>What is Enhanced Interior Gateway Routing Protocol?</p>
<p>What is Fast Convergence time?</p>
<p>How network traffic travels on multicast?</p>
<p>Note: The insight that you will post on online discussion forum using Learning Management System (LMS) will receive additional scores in class participation.</p>
<p>Offline Activities</p>
<p>(e-Learning/Self-Paced) | Lecture Guide</p>
<p>EIGRP (Enhanced Interior Gateway Routing Protocol) is an</p>
<p>Advanced Distance Vector routing protocol</p>
<p>It supports large networks</p>
<p>It has very fast convergence time</p>
<p>It supports bounded updates where network topology change</p>
<p>updates are only sent to routers affected by the change</p>
<p>Messages are sent using multicast</p>
<p>EIGRP will automatically perform equal cost load balancing on</p>
<p>up to 4 paths by default</p>
<p>This can be increased up to 16 paths</p>
<p>EIGRP can also be configured to perform unequal cost load</p>
<p>balancing</p>
<p>EIGRP Configuration – AS number</p>
<p>‘100’ in this example is the Autonomous System (AS), meaning an independent administrative domain. EIGRP routers need to have the same Autonomous System number to peer with each other.</p>
<p>EIGRP Configuration – network</p>
<p>The network command uses a wildcard mask which is the inverse of a</p>
<p>subnet mask.</p>
<p>Subtract each octet in the subnet mask from 255 to calculate the</p>
<p>wildcard mask</p>
<p>A subnet mask of 255.255.0.0 equals a wildcard mask of 0.0.255.255</p>
<p>A subnet mask of 255.255.255.252 equals a wildcard mask of 0.0.0.3</p>
<p>If you do not enter a wildcard mask, the command defaults to</p>
<p>using the classful boundary</p>
<li>0.255.255.255 for a Class A address</li>
<li>0.0.255.255 for a Class B address</li>
<li>0.0.0.255 for a Class C address</li>
<h4>The network command means:</h4>
<p>Look for interfaces with an IP address which falls within this</p>
<p>range.</p>
<p>Enable EIGRP on those interfaces – send out and listen for</p>
<p>EIGRP hello messages, and peer with adjacent EIGRP routers.</p>
<p>Advertise the network and mask which is configured on</p>
<p>those interfaces.</p>
<p>A default Class A wildcard of 0.255.255.255 will be used</p>
<p>All interfaces fall within this range in our example</p>
<p>EIGRP will be enabled on all interfaces and the router will peer with</p>
<p>adjacent EIGRP routers</p>
<h4>Networks advertised:</h4>
<li>10.1.0.0/24</li>
<li>10.0.1.0/24</li>
<li>10.0.2.0/24</li>
<li>10.0.0.0/8 is NOT advertised</li>
<p>Interface FE1/0 and FE2/0 fall within this range, FE0/0 does not</p>
<p>EIGRP will be enabled on FE1/0 and FE2/0 and the router will peer with</p>
<p>adjacent EIGRP routers</p>
<h4>Networks advertised:</h4>
<li>10.0.1.0/24</li>
<li>10.0.2.0/24</li>
<li>10.1.0.0/24 is NOT advertised</li>
<li>10.0.0.0/16 is NOT advertised</li>
<h4>Two different configurations, same result:</h4>
<p>EIGRP Router ID</p>
<p>EIGRP routers identify themselves using an EIGRP Router ID which is in</p>
<p>the form of an IP address.</p>
<p>This will default to being the highest IP address of any loopback</p>
<p>interfaces configured on the router, or the highest other IP address if a</p>
<p>loopback does not exist.</p>
<p>Loopback interfaces never go down so the Router ID will not change.</p>
<p>You can also manually specify the Router ID.</p>
<p>Best practice is to use a Loopback or manually set the Router ID.</p>
<p>EIGRP Router ID – Loopback</p>
<p>If a loopback or higher IP address is configured after EIGRP has been set up, the Router ID will change on EIGRP process restart.</p>
<p>EIGRP Configuration – Auto-Summary</p>
<p>EIGRP can automatically summarise routes to the classful boundary</p>
<p>For example, 192.168.10.1/30 can be advertised as 192.168.10.0/24</p>
<p>This is almost never desirable</p>
<p>Auto-summary is disabled by default (it was enabled in some old IOS</p>
<p>versions)</p>
<p>No need to run this command:</p>
<p>Manual Summarization</p>
<p>The individual summarised routes are not advertised - only their summary route</p>
<p>Passive Interface Configuration</p>
<p>EIGRP Metric Calculation</p>
<p>As EIGRP is a Distance Vector routing protocol, it will receive</p>
<p>routes from its neighbours with their metric to the destination networks</p>
<p>It will then add its metric to reach the neighbour to get the</p>
<p>total metric to the destination network</p>
<p>If multiple routes are available, the route (or equal cost</p>
<p>routes) with the best metric will make it into the routing table</p>
<p>Reported Distance (aka Advertised Distance)</p>
<p>Reported Distance (aka Advertised Distance)</p>
<p>Feasible Distance</p>
<p>Reported Distance (aka Advertised Distance)</p>
<p>Successors and Feasible Successors</p>
<p>EIGRP’s best (lowest metric) path to a destination is known as the Successor</p>
<p>route</p>
<p>When a successor route goes down, the router will query EIGRP peers in an</p>
<p>attempt to find a different route to that destination.</p>
<p>Queries take time and use resources, so it is preferable to avoid them.</p>
<p>EIGRP routers can do this by storing backup routes, known as Feasible</p>
<p>Successors, when certain requirements are met.</p>
<p>If a feasible successor is available when a successor route goes down, the</p>
<p>router will immediately fail over to it with no need to send a query.</p>
<p>A route qualifies as a Feasible Successor if its Reported Distance is</p>
<p>lower than the Feasible Distance of the current Successor Route.</p>
<p>In our example, R2 sees that the path via R3 to 10.0.1.0/24 has a</p>
<p>Reported Distance of 200.</p>
<p>This is lower than the Feasible Distance of the Successor Route via R1</p>
<p>(250), so it qualifies as a Feasible Successor.</p>
<p>EIGRP Metric Calculation</p>
<p>As EIGRP is a Distance Vector routing protocol, it will receive</p>
<p>routes from its neighbours with their metric to the</p>
<p>destination networks</p>
<p>It will then add its metric to reach the neighbour to get the</p>
<p>total metric to the destination network</p>
<p>If multiple routes are available, the route (or equal cost</p>
<p>routes) with the best metric will make it into the routing table</p>
<p>EIGRP can consider various link characteristics to calculate its metric: Bandwidth, Delay, Reliability and Load</p>
<p>EIGRP Metric Calculation</p>
<p>EIGRP Metric = 256*((K1*Bandwidth) + (K2*Bandwidth)/(256-</p>
<p>Load) + K3*Delay)*(K5/(Reliability + K4)))</p>
<p>By default, the values of K1 and K3 are set to 1, and K2, K4</p>
<p>and K5 are set to 0</p>
<p>The formula can be shortened to 256*(bandwidth + delay)</p>
<p>Engaging Activities</p>
<p>How do you define Enhanced Interior Gateway Routing Protocol?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>How do you explain fast convergence time?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>How do you check for messages being sent using multicast?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>How load balancing works on EIGRP?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>What is the purpose of a number in EIGRP command?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>Performance Task 2</p>
<p>Direction: Provide a one-liner explanation for the terminologies listed below.</p>
<p>https://www.flackbox.com/cisco-ccna-lab-options</p>
<p>https://www.flackbox.com/#elementor-action%3Aaction%3Dpopup%3Aopen%26settings%3DeyJpZCI6IjEwMzk4IiwidG9nZ2xlIjpmYWxzZX0%3D</p>
<p>https://www.udemy.com/course/networkplus/</p>
                    </div>
                    
                    <div class="info-box">
                        <h4>Key Concept</h4>
                        <p>This content covers advanced networking concepts. Practice exercises and interactive simulations are available in the lab sections.</p>
                    </div>
                </div>
            """
    },
    "5.1": {
        "title": "Advanced Routing and Switching",
        "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-5.docx",
        "content": """
                <div class="lesson-content">
                    <h2>Advanced Routing and Switching</h2>
                    
                    <div class="lesson-section">
                        <p>LSPU Self-Paced Learning Module (SLM)</p>
<p>Learning Outcomes</p>
<p>Student Learning Strategies</p>
<p>Performance Tasks</p>
<p>Understanding Directed Assess</p>
<p>Learning Resources</p>
<p>Course | ITEP 309 Networking 2</p>
<p>Sem/AY | First Semester/2020-2021</p>
<p>Module No. | 4</p>
<p>Lesson Title | OSPF</p>
<p>Week Duration | 8-9</p>
<p>Date | November 23 – December 04, 2020</p>
<p>Description of the Lesson | This lesson will discuss on OSPF (Open Shortest Path First) focusing on how routing can be fully utilized using one of the most used protocols on a wide-scale of network topologies.</p>
<p>Intended Learning Outcomes | Students should be able to meet the following intended learning outcomes:</p>
<p>Understand the fundamental usage of OSPF</p>
<p>Elaborate how OSPF should be implemented on top of the other protocols</p>
<p>Targets/ Objectives | At the end of the lesson, students should be able to:</p>
<p>Learn and understand the open shortest path first</p>
<p>To demonstrate the configuration of open shortest path first</p>
<p>To identify the usage and importance of open shortest path first on a corporate network</p>
<p>To simulate different scenarios in implementing open shortest path first</p>
<p>Online Activities (Synchronous/</p>
<p>Asynchronous) | Lecture presentation uploaded in Google Classroom</p>
<p>Students will be instructed to download lecture presentations with narrations / pre-recorded lecture presentation uploaded in Google Classroom.</p>
<p>For further instructions, refer to your Google Classroom and see the schedule of activities for this module.</p>
<h4>Learning Guide Questions:</h4>
<p>What is Open Shortest Path First?</p>
<p>What is Dijskstra’s algorithm>?</p>
<p>Is OSPF one of the open standard protocol?</p>
<p>Note: The insight that you will post on online discussion forum using Learning Management System (LMS) will receive additional scores in class participation.</p>
<p>Offline Activities</p>
<p>(e-Learning/Self-Paced) | Lecture Guide</p>
<p>OSPF is a Link State routing protocol</p>
<p>It supports large networks</p>
<p>It has very fast convergence time</p>
<p>Messages are sent using multicast</p>
<p>OSPF is an open standard protocol</p>
<p>It uses Dijkstra’s Shortest Path First algorithm to determine the best path</p>
<p>to learned networks</p>
<p>OSPF vs EIGRP vs RIP</p>
<p>RIP has scalability limitations so it is not typically used in production networks</p>
<p>It is suitable for small networks or lab/test environments</p>
<p>The choice for most companies for their IGP comes down to EIGRP or OSPF</p>
<p>OSPF is the most commonly used</p>
<p>It supports large networks and has always been an open standard.</p>
<p>It is supported on all vendors equipment EIGRP can be simpler to implement and troubleshoot It was historically a Cisco proprietary protocol</p>
<p>It is now an open standard but there is still limited support on other vendor’s equipment</p>
<p>Link State Routing Protocols</p>
<p>In Link State routing protocols, each router describes itself and its interfaces to its directly connected neighbours</p>
<p>This information is passed unchanged from one router to another</p>
<p>Every router learns the full picture of the network including every router, its interfaces and what they connect to</p>
<p>OSPF routers use LSA Link State Advertisements to pass on routing updates</p>
<p>OSPF Operations</p>
<li>1. Discover neighbours</li>
<li>2. Form adjacencies</li>
<li>3. Flood Link State Database (LSDB)</li>
<li>4. Compute Shortest Path</li>
<li>5. Install best routes in routing table</li>
<li>6. Respond to network changes</li>
<p>OSPF Packet Types</p>
<p>Hello: A router will send out and listen for Hello packets when OSPF is enabled on an interface, and form adjacencies with other OSPF routers on the link</p>
<p>DBD DataBase Description: Adjacent routers will tell each other the networks they know about with the DBD packet</p>
<p>LSR Link State Request: If a router is missing information about any of the networks in the received DBD, it will send the neighbour an LSR</p>
<p>LSA Link State Advertisement: A routing update</p>
<p>LSU Link State Update: Contains a list of LSA’s which should be updated, used during flooding</p>
<p>LSAck: Receiving routers acknowledge LSAs</p>
<p>OSPF Configuration – Process ID</p>
<p>Different interfaces on a router can run in different instances of OSPF.</p>
<p>Different instances have different Link State Databases</p>
<p>Only one instance is typically configured on OSPF routers – multiple Process IDs are very rarely used</p>
<p>The Process ID is locally significant. It does not have to match on the neighbour router to form an adjacency</p>
<p>In the example below, R2 will form adjacencies with both R1 and R3 (even though the Router ID does not match on both sides)</p>
<p>R1 and R3 will not learn each others routes because they are in different Process IDs on R2</p>
<p>This is a normal configuration. All routers will learn all routes</p>
<p>OSPF Configuration – network</p>
<p>The network command uses a wildcard mask which is the inverse of a subnet mask.</p>
<p>Subtract each octet in the subnet mask from 255 to calculate the wildcard mask</p>
<p>A subnet mask of 255.255.0.0 equals a wildcard mask of 0.0.255.255</p>
<p>A subnet mask of 255.255.255.252 equals a wildcard mask of 0.0.0.3</p>
<p>The command does not default to using the classful boundary</p>
<p>You must enter a wildcard mask</p>
<h4>The network command means:</h4>
<p>Look for interfaces with an IP address which falls within this range.</p>
<p>Enable OSPF on those interfaces – send out and listen for OSPF hello messages, and peer with adjacent OSPF routers.</p>
<p>Advertise the network and mask which is configured on those interfaces.</p>
<p>OSPF Configuration Example – network</p>
<p>Interface FE1/0 and FE2/0 fall within this range, FE0/0 does not</p>
<p>OSPF will be enabled on FE1/0 and FE2/0 and the router will peer with adjacent OSPF routers</p>
<p>Networks advertised: 10.0.1.0/24 10.0.2.0/24 10.1.0.0/24 is NOT advertised 10.0.0.0/16 is NOT advertised</p>
<p>OSPF Verification – show run | section ospf</p>
<p>OSPF Verification – show ip ospf interface brief</p>
<p>OSPF Operations</p>
<li>1. Discover neighbours</li>
<li>2. Form adjacencies</li>
<li>3. Flood Link State Database (LSDB)</li>
<li>4. Compute Shortest Path</li>
<li>5. Install best routes in routing table</li>
<li>6. Respond to network changes</li>
<p>OSPF Verification -show ip ospf neighbor</p>
<p>OSPF Verification -show ip ospf database</p>
<p>OSPF Verification -show ip route</p>
<p>Engaging Activities</p>
<p>How do you define Open Shortest Path First?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>Why OSPF is suitable for small network lab/test environments?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>Which among the following protocols are most commonly used (RIP, EIGRP and OSPF) and why ?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>How do you explain link state routing protocol?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>What Flood Link State Database can provide for its operation?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>Performance Task 2</p>
<p>Direction: Provide a one-liner explanation for the terminologies listed below.</p>
<p>https://www.flackbox.com/cisco-ccna-lab-options</p>
<p>https://www.flackbox.com/#elementor-action%3Aaction%3Dpopup%3Aopen%26settings%3DeyJpZCI6IjEwMzk4IiwidG9nZ2xlIjpmYWxzZX0%3D</p>
<p>https://www.udemy.com/course/networkplus/</p>
                    </div>
                    
                    <div class="info-box">
                        <h4>Key Concept</h4>
                        <p>This content covers advanced networking concepts. Practice exercises and interactive simulations are available in the lab sections.</p>
                    </div>
                </div>
            """
    },
    "7.1": {
        "title": "Network Troubleshooting and Optimization",
        "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-7.docx",
        "content": """
                <div class="lesson-content">
                    <h2>Network Troubleshooting and Optimization</h2>
                    
                    <div class="lesson-section">
                        <p>LSPU Self-Paced Learning Module (SLM)</p>
<p>Learning Outcomes</p>
<p>Student Learning Strategies</p>
<p>Performance Tasks</p>
<p>Understanding Directed Assess</p>
<p>Learning Resources</p>
<p>Course | ITEP 309 Networking 2</p>
<p>Sem/AY | First Semester/2020-2021</p>
<p>Module No. | 7</p>
<p>Lesson Title | VLAN Trunking Protocol</p>
<p>Week Duration | 12-13</p>
<p>Date | December 21 – December 31, 2020</p>
<p>Description of the Lesson | To save cost on network infrastructure and to have an optimal performance VLAN is widely used to utilize the maximum efficiency of the network devices. On this lesson, we will be discussing one of the most useful protocols available in networking that helps a lot of collisions, traffics and network problems solved.</p>
<p>Intended Learning Outcomes | Students should be able to meet the following intended learning outcomes:</p>
<p>Learn VLAN as one of the most useful protocol in networking</p>
<p>Understand how it works and how it can provide a solution on complex network infrastructures</p>
<p>Understand how to configure and how it can be implemented</p>
<p>Targets/ Objectives | At the end of the lesson, students should be able to:</p>
<p>Learn VLAN as one of the most useful protocol in networking</p>
<p>Understand how it works and how it can provide a solution on complex network infrastructures</p>
<p>Understand how to configure and how it can be implemented</p>
<p>Online Activities (Synchronous/</p>
<p>Asynchronous) | Lecture presentation uploaded in Google Classroom</p>
<p>Students will be instructed to download lecture presentations with narrations / pre-recorded lecture presentation uploaded in Google Classroom.</p>
<p>For further instructions, refer to your Google Classroom and see the schedule of activities for this module.</p>
<h4>Learning Guide Questions:</h4>
<p>How to configure VLAN?</p>
<p>What are the problems that can be solved with this protocol?</p>
<p>Why VLAN is essential in managing a wide scale network infrastructure?</p>
<p>Note: The insight that you will post on online discussion forum using Learning Management System (LMS) will receive additional scores in class participation.</p>
<p>Offline Activities</p>
<p>(e-Learning/Self-Paced) | Lecture Guide</p>
<p>Explain the Role of VLANs in a Converged Network</p>
<p>Describe the different types VLANs</p>
<p>Describe the VLAN port membership modes</p>
<p>Describe how to manage broadcast domains with VLANs</p>
<p>Explain the role of a trunk when using multiple VLANs in a converged network</p>
<p>Describe how a trunk works</p>
<p>Describe the switch port trunking modes</p>
<p>Describe the steps to configure trunks and VLANs</p>
<p>Configure VLANs on the Switches in a Converged Network Topology</p>
<p>Describe the Cisco IOS commands used to create a VLAN on a Cisco Catalyst switch</p>
<p>Describe the Cisco IOS commands used to manage VLANs on a Cisco Catalyst switch</p>
<p>Describe the Cisco IOS commands used to create a trunk on a Cisco Catalyst switch</p>
<p>Describe the common problems with VLANs and trunks</p>
<p>Troubleshoot Common Software or Hardware Misconfigurations Associated with VLANs</p>
<p>Describe the common problems with VLANs and trunks</p>
<p>Describe how to use the troubleshooting procedure to fix a common problem with VLAN configurations</p>
<p>Summary</p>
<p>VLANS Allows an administrator to logically group devices that act as their own network Are used to segment broadcast domains Some benefits of VLANs include Cost reduction, security, higher performance, better management</p>
<p>Types of Traffic on a VLAN include Data, Voice Network protocol and Network management Communication between different VLANs requires the use of Routers</p>
<p>Trunks A common conduit used by multiple VLANS for intra-VLAN communication</p>
<p>EEE 802.1Q The standard trunking protocol Uses frame tagging to identify the VLAN to which a frame belongs Does not tag native VLAN traffic</p>
<p>Engaging Activities</p>
<p>How do you describe VLAN in terms of its usability?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>Is it a great idea to use VLAN on a single network with only 5 computers? Why?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>Suppose you are managing 50 computers for 10 departments, how are you going to utilize VLAN for the entire network?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>As VLAN is commonly used to create a separate virtual network on a physical infrastructure, how are you going to implement this on a multi-layered network platform?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>If a company requested a vlan configuration for their office, how are you going to address their request once the network devices and peripherals has been provided to you?</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>__________________________________________________________________________________</p>
<p>Performance Task 2</p>
<p>Direction: Provide a one-liner explanation for the terminologies listed below.</p>
<p>https://www.flackbox.com/cisco-ccna-lab-options</p>
<p>https://www.flackbox.com/#elementor-action%3Aaction%3Dpopup%3Aopen%26settings%3DeyJpZCI6IjEwMzk4IiwidG9nZ2xlIjpmYWxzZX0%3D</p>
<p>https://www.udemy.com/course/networkplus/</p>
                    </div>
                    
                    <div class="info-box">
                        <h4>Key Concept</h4>
                        <p>This content covers advanced networking concepts. Practice exercises and interactive simulations are available in the lab sections.</p>
                    </div>
                </div>
            """
    },
}
