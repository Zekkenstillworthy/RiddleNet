"""
Module content loader for RiddleNet learning platform.
Loads extracted content from .docx files.
"""

from extracted_module_content import MODULE_CONTENT

def get_module_lesson_content():
    """
    Returns lesson content extracted from .docx module files.
    Falls back to basic content for missing lessons.
    """
    # Start with extracted content
    lesson_content = {}
    
    # Add extracted module content
    for lesson_id, content in MODULE_CONTENT.items():
        lesson_content[lesson_id] = {
            "title": content["title"],
            "content": content["content"]
        }
    
    # Add fallback content for missing lessons to maintain compatibility
    fallback_lessons = {
        "1.2": {
            "title": "Computer Network Architecture",
            "content": """
                <div class="lesson-content">
                    <h2>Computer Network Architecture</h2>
                    
                    <div class="lesson-section">
                        <h3>Network Architecture Models</h3>
                        <p>Network architecture refers to the design of the network, including both physical and logical layout. 
                        It specifies the network's organization, its components, and their configuration.</p>
                        
                        <div class="info-box">
                            <h4>Key Concept</h4>
                            <p>The OSI (Open Systems Interconnection) and TCP/IP models provide frameworks for understanding how networks function at different layers.</p>
                        </div>
                    </div>
                    
                    <div class="lesson-section">
                        <h3>The OSI Model</h3>
                        <p>The OSI Model divides network communication into 7 layers:</p>
                        <div class="osi-model">
                            <div class="osi-layer">
                                <div class="layer-number">7</div>
                                <div class="layer-name">Application</div>
                                <div class="layer-desc">End-user services, file transfers, email</div>
                            </div>
                            <div class="osi-layer">
                                <div class="layer-number">6</div>
                                <div class="layer-name">Presentation</div>
                                <div class="layer-desc">Data translation, encryption, compression</div>
                            </div>
                            <div class="osi-layer">
                                <div class="layer-number">5</div>
                                <div class="layer-name">Session</div>
                                <div class="layer-desc">Connection management between applications</div>
                            </div>
                            <div class="osi-layer">
                                <div class="layer-number">4</div>
                                <div class="layer-name">Transport</div>
                                <div class="layer-desc">End-to-end connections, reliability, flow control</div>
                            </div>
                            <div class="osi-layer">
                                <div class="layer-number">3</div>
                                <div class="layer-name">Network</div>
                                <div class="layer-desc">Addressing, routing, packet forwarding</div>
                            </div>
                            <div class="osi-layer">
                                <div class="layer-number">2</div>
                                <div class="layer-name">Data Link</div>
                                <div class="layer-desc">Physical addressing, error detection</div>
                            </div>
                            <div class="osi-layer">
                                <div class="layer-number">1</div>
                                <div class="layer-name">Physical</div>
                                <div class="layer-desc">Physical connections, bit transmission</div>
                            </div>
                        </div>
                    </div>
                </div>
            """
        },
        "1.3": {
            "title": "Network Components",
            "content": """
                <div class="lesson-content">
                    <h2>Network Components</h2>
                    
                    <div class="lesson-section">
                        <h3>Essential Networking Devices</h3>
                        <p>Computer networks rely on various hardware components to establish connections and facilitate communication between devices.</p>
                        
                        <div class="network-components">
                            <div class="component">
                                <img src="/static/img/router.png" alt="Router">
                                <h4>Router</h4>
                                <p>Connects different networks and directs data packets between them using routing tables. Operates at the Network Layer (Layer 3).</p>
                            </div>
                            
                            <div class="component">
                                <img src="/static/img/switch.png" alt="Switch">
                                <h4>Switch</h4>
                                <p>Connects devices within a network and forwards data packets based on MAC addresses. Operates at the Data Link Layer (Layer 2).</p>
                            </div>
                        </div>
                    </div>
                </div>
            """
        },
        "1.4": {
            "title": "Computer Network Types",
            "content": """
                <div class="lesson-content">
                    <h2>Computer Network Types</h2>
                    
                    <div class="lesson-section">
                        <h3>Networks Based on Scale</h3>
                        <p>Networks can be classified based on their geographical coverage area:</p>
                        
                        <div class="network-types">
                            <div class="network-type">
                                <div class="type-icon">
                                    <i class="fas fa-home"></i>
                                </div>
                                <h4>PAN (Personal Area Network)</h4>
                                <p>The smallest network type, covering a range of a few meters.</p>
                                <ul>
                                    <li>Range: 1-10 meters</li>
                                    <li>Technologies: Bluetooth, NFC, Infrared</li>
                                    <li>Use cases: Connecting personal devices like smartphones to headphones, smartwatches</li>
                                </ul>
                            </div>
                            
                            <div class="network-type">
                                <div class="type-icon">
                                    <i class="fas fa-building"></i>
                                </div>
                                <h4>LAN (Local Area Network)</h4>
                                <p>Networks limited to a small geographical area like a home, office, or building.</p>
                                <ul>
                                    <li>Range: Up to a few kilometers</li>
                                    <li>Technologies: Ethernet, Wi-Fi</li>
                                    <li>Use cases: Home networks, office networks, school networks</li>
                                    <li>Characteristics: High data transfer rates, limited geographical area</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            """
        },
        "2.3": {
            "title": "Ethernet and Switching",
            "content": """
                <div class="lesson-content">
                    <h2>Ethernet and Switching</h2>
                    
                    <div class="lesson-section">
                        <h3>Ethernet Technology</h3>
                        <p>Ethernet is the most widely used Local Area Network (LAN) technology. It defines the physical and data link layer specifications for wired network connections.</p>
                        
                        <div class="info-box">
                            <h4>Key Concept</h4>
                            <p>Ethernet uses CSMA/CD (Carrier Sense Multiple Access with Collision Detection) for media access control in shared environments.</p>
                        </div>
                    </div>
                    
                    <div class="lesson-section">
                        <h3>Network Switching</h3>
                        <p>Network switches operate at the Data Link Layer (Layer 2) and use MAC addresses to forward frames between network segments.</p>
                    </div>
                </div>
            """
        },
        "2.4": {
            "title": "Advanced Data Link Protocols",
            "content": """
                <div class="lesson-content">
                    <h2>Advanced Data Link Protocols</h2>
                    
                    <div class="lesson-section">
                        <h3>Frame Relay</h3>
                        <p>Frame Relay is a packet-switching telecommunications service designed for cost-efficient data transmission for intermittent traffic.</p>
                    </div>
                    
                    <div class="lesson-section">
                        <h3>PPP (Point-to-Point Protocol)</h3>
                        <p>PPP provides a standard method for transporting multi-protocol datagrams over point-to-point links.</p>
                    </div>
                </div>
            """
        },
        "3.2": {
            "title": "IP Addressing and Subnetting",
            "content": """
                <div class="lesson-content">
                    <h2>IP Addressing and Subnetting</h2>
                    
                    <div class="lesson-section">
                        <h3>IPv4 Addressing</h3>
                        <p>IPv4 addresses are 32-bit identifiers used to uniquely identify devices on a network. They are typically written in dotted decimal notation.</p>
                        
                        <div class="info-box">
                            <h4>Address Classes</h4>
                            <ul>
                                <li>Class A: 1.0.0.0 to 126.255.255.255</li>
                                <li>Class B: 128.0.0.0 to 191.255.255.255</li>
                                <li>Class C: 192.0.0.0 to 223.255.255.255</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="lesson-section">
                        <h3>Subnetting</h3>
                        <p>Subnetting allows you to divide a network into smaller, more manageable subnetworks (subnets).</p>
                    </div>
                </div>
            """
        },
        "3.3": {
            "title": "Routing Protocols",
            "content": """
                <div class="lesson-content">
                    <h2>Routing Protocols</h2>
                    
                    <div class="lesson-section">
                        <h3>Static vs Dynamic Routing</h3>
                        <p>Routing protocols determine the best path for data packets to travel from source to destination across networks.</p>
                        
                        <div class="info-box">
                            <h4>Types of Routing Protocols</h4>
                            <ul>
                                <li><strong>Distance Vector:</strong> RIP, EIGRP</li>
                                <li><strong>Link State:</strong> OSPF, IS-IS</li>
                                <li><strong>Path Vector:</strong> BGP</li>
                            </ul>
                        </div>
                    </div>
                </div>
            """
        },
        "3.4": {
            "title": "Network Layer Security",
            "content": """
                <div class="lesson-content">
                    <h2>Network Layer Security</h2>
                    
                    <div class="lesson-section">
                        <h3>IPSec Protocol</h3>
                        <p>Internet Protocol Security (IPSec) is a suite of protocols for securing Internet Protocol (IP) communications by authenticating and encrypting each IP packet.</p>
                    </div>
                    
                    <div class="lesson-section">
                        <h3>VPN Technologies</h3>
                        <p>Virtual Private Networks (VPNs) create secure connections over public networks using tunneling protocols.</p>
                    </div>
                </div>
            """
        },
        "4.1": {
            "title": "Application Layer Overview",
            "content": """
                <div class="lesson-content">
                    <h2>Application Layer Overview</h2>
                    
                    <div class="lesson-section">
                        <h3>Application Layer Services</h3>
                        <p>The Application Layer (Layer 7) provides network services directly to end-users and applications. It serves as the interface between the network and the application software.</p>
                        
                        <div class="info-box">
                            <h4>Common Application Layer Protocols</h4>
                            <ul>
                                <li><strong>HTTP/HTTPS:</strong> Web browsing</li>
                                <li><strong>FTP:</strong> File transfer</li>
                                <li><strong>SMTP:</strong> Email sending</li>
                                <li><strong>POP3/IMAP:</strong> Email retrieval</li>
                                <li><strong>DNS:</strong> Domain name resolution</li>
                                <li><strong>DHCP:</strong> Dynamic IP assignment</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="lesson-section">
                        <h3>Client-Server Architecture</h3>
                        <p>Most application layer protocols follow a client-server model where clients request services and servers provide responses.</p>
                    </div>
                </div>
            """
        }
    }
    
    # Add fallback lessons for any missing content
    for lesson_id, content in fallback_lessons.items():
        if lesson_id not in lesson_content:
            lesson_content[lesson_id] = content
    
    return lesson_content

def get_available_lesson_ids():
    """Return a list of all available lesson IDs."""
    content = get_module_lesson_content()
    return sorted(content.keys())
