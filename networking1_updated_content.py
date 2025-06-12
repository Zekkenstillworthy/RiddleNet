"""
Networking 1 Course Content - COMPLETE RECREATION
Comprehensive structured content recreated from all modules
Date: June 11, 2025
Source: Modules 1-4.3 from Networking 1 folder
"""

def get_networking1_content():
    """
    Returns comprehensive content for Networking 1 course
    Organized by modules and lessons based on actual module files
    """
    return {
        # Module 1: Computer Network Fundamentals
        "1.1": {
            "title": "Introduction to Computer Networks",
            "source_file": "Module-1-ITEP-207-Networking-1.txt",
            "content": """
            <div class="lesson-content">
                <h2>Introduction to Computer Networks</h2>
                
                <div class="lesson-description">
                    <p>Computer Network tutorial provides basic and advanced concepts of Data Communication & Networks (DCN). 
                    A computer network is a set of devices connected through links. A node can be computer, printer, or any 
                    other device capable of sending or receiving the data. The links connecting the nodes are known as 
                    communication channels.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>What is a Computer Network?</h3>
                    <ul>
                        <li>Computer Network is a group of computers connected with each other through wires, optical fibres or optical links</li>
                        <li>Various devices can interact with each other through a network</li>
                        <li>The aim of the computer network is the sharing of resources among various devices</li>
                        <li>There are several types of networks that vary from simple to complex level</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Distributed Processing</h3>
                    <p>Computer Network uses distributed processing in which task is divided among several computers. 
                    Instead, a single computer handles an entire task, each separate computer handles a subset.</p>
                    
                    <div class="benefits-list">
                        <h4>Advantages of Distributed Processing:</h4>
                        <ul>
                            <li><strong>Security:</strong> It provides limited interaction that a user can have with the entire system</li>
                            <li><strong>Faster problem solving:</strong> Multiple computers can solve the problem faster than a single machine working alone</li>
                            <li><strong>Security through redundancy:</strong> Multiple computers running the same program at the same time can provide security through redundancy</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Major Components of Computer Network</h3>
                    
                    <div class="component-item">
                        <h4>NIC (Network Interface Card)</h4>
                        <p>NIC is a device that helps the computer to communicate with another device. Contains hardware addresses for system identification.</p>
                        <ul>
                            <li><strong>Wireless NIC:</strong> Uses antenna with radio wave technology</li>
                            <li><strong>Wired NIC:</strong> Uses cables to transfer data over the medium</li>
                        </ul>
                    </div>
                    
                    <div class="component-item">
                        <h4>Hub</h4>
                        <p>Central device that splits network connection into multiple devices. Distributes requests to all interconnected computers.</p>
                    </div>
                    
                    <div class="component-item">
                        <h4>Switch</h4>
                        <p>Better than Hub as it sends messages directly to specific devices instead of broadcasting to all.</p>
                    </div>
                    
                    <div class="component-item">
                        <h4>Router</h4>
                        <p>Connects LAN to internet and connects distinct networks together.</p>
                    </div>
                    
                    <div class="component-item">
                        <h4>Modem</h4>
                        <p>Connects computer to internet over telephone line. Stands for Modulator/Demodulator.</p>
                    </div>
                </div>
            </div>
            """
        },
        
        "1.2": {
            "title": "Network Architecture and Types",
            "source_file": "Module-1-ITEP-207-Networking-1.txt",
            "content": """
            <div class="lesson-content">
                <h2>Computer Network Architecture</h2>
                
                <div class="lesson-description">
                    <p>Computer Network Architecture is defined as the physical and logical design of the software, hardware, 
                    protocols, and media of the transmission of data.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Types of Network Architectures</h3>
                    
                    <div class="architecture-type">
                        <h4>Peer-To-Peer Network</h4>
                        <ul>
                            <li>All computers linked with equal privilege and responsibilities</li>
                            <li>Useful for small environments, usually up to 10 computers</li>
                            <li>No dedicated server</li>
                            <li>Less costly but security issues exist</li>
                        </ul>
                    </div>
                    
                    <div class="architecture-type">
                        <h4>Client/Server Network</h4>
                        <ul>
                            <li>End users (clients) access resources from central computer (server)</li>
                            <li>Server performs major operations like security and network management</li>
                            <li>Better security and performance</li>
                            <li>More expensive but scalable</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Network Types</h3>
                    
                    <div class="network-types">
                        <h4>LAN (Local Area Network)</h4>
                        <ul>
                            <li>Covers small geographical area like building or campus</li>
                            <li>High data transfer rates</li>
                            <li>Private ownership</li>
                            <li>Easy to maintain and install</li>
                        </ul>
                        
                        <h4>WAN (Wide Area Network)</h4>
                        <ul>
                            <li>Covers large geographical area across cities or countries</li>
                            <li>Uses public networks like telephone lines</li>
                            <li>Lower data transfer rates compared to LAN</li>
                            <li>Higher setup and maintenance costs</li>
                        </ul>
                        
                        <h4>MAN (Metropolitan Area Network)</h4>
                        <ul>
                            <li>Covers larger area than LAN but smaller than WAN</li>
                            <li>Typically covers a city or metropolitan area</li>
                            <li>Can be public or private</li>
                        </ul>
                    </div>
                </div>
            </div>
            """
        },
        
        "1.3": {
            "title": "OSI Model and Layered Architecture",
            "source_file": "Module-1-ITEP-207-Networking-1.txt",
            "content": """
            <div class="lesson-content">
                <h2>OSI Model</h2>
                
                <div class="lesson-description">
                    <p>OSI stands for Open System Interconnection. It is a reference model that describes how information 
                    from a software application in one computer moves through a physical medium to the software application 
                    in another computer.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Characteristics of OSI Model</h3>
                    <ul>
                        <li>OSI consists of seven layers, each performing particular network functions</li>
                        <li>Developed by ISO in 1984</li>
                        <li>Divides complex task into smaller, manageable tasks</li>
                        <li>Each layer is self-contained</li>
                        <li>Upper layers deal with application issues, lower layers with data transport</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>The Seven Layers of OSI Model</h3>
                    
                    <div class="osi-layer">
                        <h4>1. Physical Layer</h4>
                        <ul>
                            <li>Responsible for actual physical connection between devices</li>
                            <li>Transmits raw bit stream over physical medium</li>
                            <li>Defines electrical and physical specifications</li>
                            <li>Examples: cables, switches, hubs</li>
                        </ul>
                    </div>
                    
                    <div class="osi-layer">
                        <h4>2. Data Link Layer</h4>
                        <ul>
                            <li>Responsible for node-to-node delivery</li>
                            <li>Ensures error-free transfer of data frames</li>
                            <li>Handles error detection and correction</li>
                            <li>Examples: Ethernet, WiFi protocols</li>
                        </ul>
                    </div>
                    
                    <div class="osi-layer">
                        <h4>3. Network Layer</h4>
                        <ul>
                            <li>Responsible for delivery of packets between different networks</li>
                            <li>Handles routing and logical addressing</li>
                            <li>Determines best path for data transmission</li>
                            <li>Examples: IP, ICMP, ARP</li>
                        </ul>
                    </div>
                    
                    <div class="osi-layer">
                        <h4>4. Transport Layer</h4>
                        <ul>
                            <li>Ensures end-to-end delivery of complete message</li>
                            <li>Provides error recovery and flow control</li>
                            <li>Segments data and reassembles at destination</li>
                            <li>Examples: TCP, UDP</li>
                        </ul>
                    </div>
                    
                    <div class="osi-layer">
                        <h4>5. Session Layer</h4>
                        <ul>
                            <li>Establishes, manages, and terminates sessions</li>
                            <li>Provides authentication and authorization</li>
                            <li>Handles session checkpointing and recovery</li>
                        </ul>
                    </div>
                    
                    <div class="osi-layer">
                        <h4>6. Presentation Layer</h4>
                        <ul>
                            <li>Handles data encryption, compression, and translation</li>
                            <li>Ensures data is readable by receiving system</li>
                            <li>Manages syntax and semantics of information</li>
                        </ul>
                    </div>
                    
                    <div class="osi-layer">
                        <h4>7. Application Layer</h4>
                        <ul>
                            <li>Closest to end user</li>
                            <li>Provides network services to applications</li>
                            <li>Examples: HTTP, FTP, SMTP, DNS</li>
                        </ul>
                    </div>
                </div>
            </div>
            """
        },
        
        "1.4": {
            "title": "TCP/IP Model",
            "source_file": "Module-1-ITEP-207-Networking-1.txt",
            "content": """
            <div class="lesson-content">
                <h2>TCP/IP Model</h2>
                
                <div class="lesson-description">
                    <p>The TCP/IP model was developed prior to the OSI model. It consists of four layers that provide 
                    standards for internetworking and communication protocols.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>TCP/IP Model Layers</h3>
                    
                    <div class="tcpip-layer">
                        <h4>1. Network Access Layer</h4>
                        <ul>
                            <li>Combination of Physical and Data Link layers of OSI</li>
                            <li>Defines how data should be sent physically through network</li>
                            <li>Responsible for transmission between devices on same network</li>
                            <li>Protocols: Ethernet, Token Ring, FDDI</li>
                        </ul>
                    </div>
                    
                    <div class="tcpip-layer">
                        <h4>2. Internet Layer</h4>
                        <ul>
                            <li>Also known as Network layer</li>
                            <li>Sends packets from any network to destination</li>
                            <li>Handles logical addressing and routing</li>
                            <li>Main protocol: IP (Internet Protocol)</li>
                        </ul>
                    </div>
                    
                    <div class="tcpip-layer">
                        <h4>3. Transport Layer</h4>
                        <ul>
                            <li>Provides reliable delivery of data</li>
                            <li>Handles error detection and recovery</li>
                            <li>Two main protocols: TCP and UDP</li>
                        </ul>
                    </div>
                    
                    <div class="tcpip-layer">
                        <h4>4. Application Layer</h4>
                        <ul>
                            <li>Combines Session, Presentation, and Application layers of OSI</li>
                            <li>Provides network services to applications</li>
                            <li>Protocols: HTTP, FTP, SMTP, DNS, SNMP</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Key Application Layer Protocols</h3>
                    <ul>
                        <li><strong>HTTP:</strong> Hypertext Transfer Protocol for web browsing</li>
                        <li><strong>FTP:</strong> File Transfer Protocol for file sharing</li>
                        <li><strong>SMTP:</strong> Simple Mail Transfer Protocol for email</li>
                        <li><strong>DNS:</strong> Domain Name System for name resolution</li>
                        <li><strong>SNMP:</strong> Simple Network Management Protocol for network management</li>
                    </ul>
                </div>
            </div>
            """
        },
        
        "2.1": {
            "title": "Ethernet Technology",
            "source_file": "Module-2.1-ITEP-207-Networking-1.txt",
            "content": """
            <div class="lesson-content">
                <h2>Ethernet Technology</h2>
                
                <div class="lesson-description">
                    <p>Ethernet is the most widely used LAN technology and is defined under IEEE standards 802.3. 
                    The reason behind its wide usability is that Ethernet is easy to understand, implement, and maintain.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Ethernet Characteristics</h3>
                    <ul>
                        <li>Operates in Physical layer and Data link layer of OSI model</li>
                        <li>Uses bus topology generally</li>
                        <li>Protocol data unit is frame</li>
                        <li>Uses CSMA/CD for collision handling</li>
                        <li>Allows flexibility in topologies</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Advantages of Ethernet</h3>
                    <ul>
                        <li><strong>Simplicity:</strong> Easy to understand and implement</li>
                        <li><strong>Flexibility:</strong> Works with wide range of devices and operating systems</li>
                        <li><strong>Reliability:</strong> Uses error-correction techniques</li>
                        <li><strong>Cost-effectiveness:</strong> Widely available and easy to implement</li>
                        <li><strong>Interoperability:</strong> Allows devices from different manufacturers to communicate</li>
                        <li><strong>Security:</strong> Built-in encryption and authentication features</li>
                        <li><strong>Manageability:</strong> Various tools available for monitoring and control</li>
                        <li><strong>Compatibility:</strong> Compatible with wide range of networking technologies</li>
                        <li><strong>Scalability:</strong> Can accommodate addition of new devices and users</li>
                        <li><strong>Standardization:</strong> All Ethernet devices designed to work together</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Ethernet Standards</h3>
                    <div class="ethernet-standards">
                        <ul>
                            <li><strong>10BASE-T:</strong> 10 Mbps over twisted pair</li>
                            <li><strong>100BASE-TX:</strong> 100 Mbps Fast Ethernet</li>
                            <li><strong>1000BASE-T:</strong> 1 Gbps Gigabit Ethernet</li>
                            <li><strong>10GBASE-T:</strong> 10 Gbps over twisted pair</li>
                        </ul>
                    </div>
                </div>
            </div>
            """
        },
        
        "3.1": {
            "title": "Transport Layer and TCP/IP",
            "source_file": "Module-3-ITEP-207-Networking-1.txt",
            "content": """
            <div class="lesson-content">
                <h2>Transport Layer Protocols</h2>
                
                <div class="lesson-description">
                    <p>The Transport layer ensures that messages are transmitted in the order in which they are sent 
                    and there is no duplication of data. It provides end-to-end delivery of complete message.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Transmission Control Protocol (TCP)</h3>
                    <ul>
                        <li>Connection-oriented protocol</li>
                        <li>Provides reliable data delivery</li>
                        <li>Establishes and maintains connection between hosts</li>
                        <li>Uses acknowledgments to ensure data reception</li>
                        <li>Implements flow control and error recovery</li>
                    </ul>
                    
                    <div class="tcp-features">
                        <h4>Key Features of TCP</h4>
                        <ul>
                            <li><strong>Segment Numbering System:</strong> TCP assigns numbers to each segment for tracking</li>
                            <li><strong>Flow Control:</strong> Manages data transmission rate</li>
                            <li><strong>Error Control:</strong> Detects and recovers from errors</li>
                            <li><strong>Congestion Control:</strong> Prevents network congestion</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>User Datagram Protocol (UDP)</h3>
                    <ul>
                        <li>Connectionless protocol</li>
                        <li>Faster transmission than TCP</li>
                        <li>No guarantee of delivery</li>
                        <li>Used for time-sensitive applications</li>
                        <li>Lower overhead than TCP</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Network Layer Services</h3>
                    
                    <div class="network-services">
                        <h4>1. Packetizing</h4>
                        <p>Process of encapsulating data from upper layers into network layer packets at source 
                        and decapsulating at destination.</p>
                        
                        <h4>2. Routing</h4>
                        <p>Process of moving data from one device to another. Network layer specifies strategies 
                        to find the best route from source to destination.</p>
                        
                        <h4>3. Forwarding</h4>
                        <p>Action taken by router when packet arrives - router forwards packet to appropriate 
                        output interface toward destination.</p>
                    </div>
                </div>
            </div>
            """
        },
        
        "4.1": {
            "title": "Application Layer Protocols",
            "source_file": "Module-4-ITEP-207-Networking-1.txt",
            "content": """
            <div class="lesson-content">
                <h2>Application Layer Protocols</h2>
                
                <div class="lesson-description">
                    <p>The Application layer is the closest layer to the end user and provides network services 
                    to software applications. It enables users to access network resources and services.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Key Application Layer Functions</h3>
                    <ul>
                        <li><strong>Identifying communication partners:</strong> Determines availability of communication partners</li>
                        <li><strong>Determining resource availability:</strong> Checks if sufficient network resources are available</li>
                        <li><strong>Synchronizing communication:</strong> Manages cooperation between applications</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Major Application Protocols</h3>
                    
                    <div class="protocol-item">
                        <h4>Domain Name System (DNS)</h4>
                        <ul>
                            <li>Translates domain names to IP addresses</li>
                            <li>Hierarchical distributed database</li>
                            <li>Essential for internet functionality</li>
                            <li>Uses UDP port 53</li>
                        </ul>
                    </div>
                    
                    <div class="protocol-item">
                        <h4>File Transfer Protocol (FTP)</h4>
                        <ul>
                            <li>Used for transferring files between computers</li>
                            <li>Supports authentication</li>
                            <li>Uses TCP ports 20 and 21</li>
                            <li>Provides reliable file transfer</li>
                        </ul>
                    </div>
                    
                    <div class="protocol-item">
                        <h4>Telnet</h4>
                        <ul>
                            <li>Enables remote login to network devices</li>
                            <li>Text-based communication</li>
                            <li>Uses TCP port 23</li>
                            <li>Not secure (sends data in clear text)</li>
                        </ul>
                    </div>
                    
                    <div class="protocol-item">
                        <h4>Simple Mail Transfer Protocol (SMTP)</h4>
                        <ul>
                            <li>Used for sending email messages</li>
                            <li>Works with email clients and servers</li>
                            <li>Uses TCP port 25</li>
                            <li>Text-based protocol</li>
                        </ul>
                    </div>
                    
                    <div class="protocol-item">
                        <h4>Simple Network Management Protocol (SNMP)</h4>
                        <ul>
                            <li>Used for network management and monitoring</li>
                            <li>Collects information from network devices</li>
                            <li>Uses UDP ports 161 and 162</li>
                            <li>Essential for network administration</li>
                        </ul>
                    </div>
                    
                    <div class="protocol-item">
                        <h4>HyperText Transfer Protocol (HTTP)</h4>
                        <ul>
                            <li>Foundation of World Wide Web</li>
                            <li>Used for transferring web pages</li>
                            <li>Uses TCP port 80 (HTTP) and 443 (HTTPS)</li>
                            <li>Stateless protocol</li>
                        </ul>
                    </div>
                </div>
            </div>
            """
        },
        
        "4.2": {
            "title": "Advanced Networking Concepts",
            "source_file": "Module-4.2-ITEP-207-Networking-1.txt",
            "content": """
            <div class="lesson-content">
                <h2>Advanced Networking Concepts</h2>
                
                <div class="lesson-description">
                    <p>This module covers advanced networking topics including switching techniques, 
                    network protocols, and modern networking technologies.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Switching Techniques</h3>
                    
                    <div class="switching-types">
                        <h4>Circuit Switching</h4>
                        <ul>
                            <li>Dedicated communication path established</li>
                            <li>Resources reserved for entire communication</li>
                            <li>Used in traditional telephone networks</li>
                            <li>Guaranteed bandwidth but inefficient resource usage</li>
                        </ul>
                        
                        <h4>Packet Switching</h4>
                        <ul>
                            <li>Data broken into packets</li>
                            <li>Packets transmitted independently</li>
                            <li>More efficient resource utilization</li>
                            <li>Used in internet and modern networks</li>
                        </ul>
                        
                        <h4>Message Switching</h4>
                        <ul>
                            <li>Entire message sent as single unit</li>
                            <li>Store-and-forward mechanism</li>
                            <li>High storage requirements</li>
                            <li>Not suitable for real-time applications</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Network Performance and QoS</h3>
                    <ul>
                        <li><strong>Bandwidth:</strong> Maximum data transfer rate</li>
                        <li><strong>Latency:</strong> Time delay in communication</li>
                        <li><strong>Throughput:</strong> Actual data transfer rate achieved</li>
                        <li><strong>Quality of Service:</strong> Network performance optimization for specific traffic types</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Network Security Fundamentals</h3>
                    <ul>
                        <li><strong>Authentication:</strong> Verifying user identity</li>
                        <li><strong>Authorization:</strong> Controlling access to resources</li>
                        <li><strong>Encryption:</strong> Protecting data confidentiality</li>
                        <li><strong>Firewall:</strong> Network traffic filtering</li>
                        <li><strong>VPN:</strong> Secure remote connectivity</li>
                    </ul>
                </div>
            </div>
            """
        },
        
        "4.3": {
            "title": "Modern Networking Technologies",
            "source_file": "Module-4.3-ITEP-207-Networking-1.txt",
            "content": """
            <div class="lesson-content">
                <h2>Modern Networking Technologies</h2>
                
                <div class="lesson-description">
                    <p>This module explores advanced networking concepts including routing protocols, 
                    network design issues, and emerging technologies.</p>
                </div>
                
                <div class="lesson-section">
                    <h3>Routing Protocols Overview</h3>
                    
                    <div class="routing-protocols">
                        <h4>Types of Routing Protocols</h4>
                        <ul>
                            <li><strong>Static Routing:</strong> Manually configured routes</li>
                            <li><strong>Dynamic Routing:</strong> Automatically discovered routes</li>
                            <li><strong>Default Routing:</strong> Route of last resort</li>
                        </ul>
                        
                        <h4>Interior Gateway Protocols (IGP)</h4>
                        <ul>
                            <li><strong>RIP:</strong> Distance vector, hop count metric</li>
                            <li><strong>OSPF:</strong> Link state, cost metric</li>
                            <li><strong>EIGRP:</strong> Hybrid, composite metric</li>
                        </ul>
                        
                        <h4>Exterior Gateway Protocols (EGP)</h4>
                        <ul>
                            <li><strong>BGP:</strong> Path vector protocol for internet routing</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Network Design Issues</h3>
                    <ul>
                        <li><strong>Reliability:</strong> Network fault tolerance and redundancy</li>
                        <li><strong>Scalability:</strong> Ability to grow and adapt</li>
                        <li><strong>Security:</strong> Protection against threats</li>
                        <li><strong>Performance:</strong> Throughput and latency optimization</li>
                        <li><strong>Cost:</strong> Implementation and maintenance expenses</li>
                        <li><strong>Management:</strong> Network monitoring and control</li>
                    </ul>
                </div>
                
                <div class="lesson-section">
                    <h3>Emerging Technologies</h3>
                    
                    <div class="emerging-tech">
                        <h4>Software-Defined Networking (SDN)</h4>
                        <ul>
                            <li>Centralized network control</li>
                            <li>Programmable network infrastructure</li>
                            <li>Dynamic configuration capabilities</li>
                        </ul>
                        
                        <h4>Network Function Virtualization (NFV)</h4>
                        <ul>
                            <li>Virtualized network services</li>
                            <li>Reduced hardware dependency</li>
                            <li>Flexible service deployment</li>
                        </ul>
                        
                        <h4>Internet of Things (IoT)</h4>
                        <ul>
                            <li>Connected devices and sensors</li>
                            <li>Machine-to-machine communication</li>
                            <li>New networking challenges and opportunities</li>
                        </ul>
                        
                        <h4>5G and Beyond</h4>
                        <ul>
                            <li>Ultra-low latency communications</li>
                            <li>Massive IoT connectivity</li>
                            <li>Network slicing capabilities</li>
                        </ul>
                    </div>
                </div>
                
                <div class="lesson-section">
                    <h3>Router Types and Applications</h3>
                    
                    <div class="router-types">
                        <h4>Home Routers</h4>
                        <ul>
                            <li>Internet access for residential use</li>
                            <li>WiFi capabilities</li>
                            <li>Basic security features</li>
                        </ul>
                        
                        <h4>Enterprise Routers</h4>
                        <ul>
                            <li>High-performance routing</li>
                            <li>Advanced security features</li>
                            <li>Multiple interface types</li>
                        </ul>
                        
                        <h4>Service Provider Routers</h4>
                        <ul>
                            <li>Extremely high scalability</li>
                            <li>Carrier-grade reliability</li>
                            <li>Advanced traffic management</li>
                        </ul>
                        
                        <h4>Virtual Routers</h4>
                        <ul>
                            <li>Software-based routing</li>
                            <li>Virtualization technology</li>
                            <li>Cost-effective and flexible</li>
                        </ul>
                    </div>
                </div>
            </div>
            """
        }
    }

# Test the function
if __name__ == "__main__":
    content = get_networking1_content()
    print("Networking 1 Content Structure:")
    for key, lesson in content.items():
        print(f"- {key}: {lesson['title']}")
