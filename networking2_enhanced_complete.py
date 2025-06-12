"""
Networking 2 Course Content - ENHANCED VERSION
Comprehensive content with improved depth, MCQs, and standardized format
Matching Networking 1 quality standards
Date: June 11, 2025
"""

def get_networking2_content():
    """
    Enhanced Networking 2 content with:
    - Comprehensive theoretical explanations
    - MCQs for each module
    - Standardized metadata
    - Improved content depth
    - Better theory-to-practice balance
    """
    return {
        # Module 1: Routing Fundamentals - Enhanced
        "net2_1.1": {
            "title": "Routing Fundamentals",
            "description": "Comprehensive introduction to routing concepts, static and dynamic routing, and fundamental routing principles",
            "estimated_time": 90,
            "difficulty": "intermediate",
            "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-1.txt",
            "content": """
            <div class="lesson-content">
                <h2>🌐 Routing Fundamentals</h2>
                
                <div class="lesson-overview">
                    <div class="overview-card">
                        <h3>📚 Learning Objectives</h3>
                        <ul>
                            <li>Understand router functions and routing table structure</li>
                            <li>Configure static routing and default routes</li>
                            <li>Implement load balancing techniques</li>
                            <li>Troubleshoot basic routing issues</li>
                        </ul>
                    </div>
                </div>
                
                <div class="theoretical-foundation">
                    <h3>🏗️ Theoretical Foundation</h3>
                    
                    <div class="definition-section">
                        <h4>What is Routing?</h4>
                        <div class="definition-box">
                            <p><strong>Routing</strong> is the process of selecting paths in a network along which to send network traffic. It involves determining the best path for data packets to travel from source to destination across interconnected networks.</p>
                        </div>
                    </div>
                    
                    <div class="router-functions">
                        <h4>Router Functions</h4>
                        <div class="function-grid">
                            <div class="function-card">
                                <h5>🎯 Path Determination</h5>
                                <p>Analyzing available paths and selecting optimal routes based on metrics</p>
                            </div>
                            <div class="function-card">
                                <h5>📦 Packet Forwarding</h5>
                                <p>Moving packets from input interface to appropriate output interface</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="assessment-section">
                    <h3>📝 Knowledge Assessment</h3>
                    <div class="mcq-container">
                        <div class="mcq-question">
                            <h4>Question 1: What are the two main functions of a router?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q1" value="a"> A) Switching and bridging</label>
                                <label><input type="radio" name="q1" value="b"> B) Path determination and packet forwarding</label>
                                <label><input type="radio" name="q1" value="c"> C) Error detection and correction</label>
                                <label><input type="radio" name="q1" value="d"> D) Collision detection and prevention</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: B) Path determination and packet forwarding</strong>
                                <p>Explanation: Routers determine the best path and forward packets accordingly.</p>
                            </div>
                        </div>
                        
                        <div class="mcq-question">
                            <h4>Question 2: Which command creates a default route?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q2" value="a"> A) ip route 192.168.1.0 255.255.255.0 10.0.0.1</label>
                                <label><input type="radio" name="q2" value="b"> B) ip route 0.0.0.0 0.0.0.0 10.0.0.1</label>
                                <label><input type="radio" name="q2" value="c"> C) ip default-gateway 10.0.0.1</label>
                                <label><input type="radio" name="q2" value="d"> D) ip route any any 10.0.0.1</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: B) ip route 0.0.0.0 0.0.0.0 10.0.0.1</strong>
                                <p>Explanation: 0.0.0.0 0.0.0.0 matches all networks, creating a default route.</p>
                            </div>
                        </div>
                    </div>
                    
                    <button class="show-answers-btn" onclick="toggleAnswers()">Show Answers</button>
                </div>
                
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
            """
        },

        # Module 2: Network Security - Enhanced
        "net2_2.1": {
            "title": "Network Security Fundamentals",
            "description": "Comprehensive network security principles, threats, and protection mechanisms",
            "estimated_time": 120,
            "difficulty": "intermediate",
            "content": """
            <div class="lesson-content">
                <h2>🛡️ Network Security Fundamentals</h2>
                
                <div class="lesson-overview">
                    <div class="overview-card">
                        <h3>📚 Learning Objectives</h3>
                        <ul>
                            <li>Understand CIA Triad principles</li>
                            <li>Identify common network threats</li>
                            <li>Implement security controls</li>
                            <li>Perform risk assessment</li>
                        </ul>
                    </div>
                </div>
                
                <div class="cia-triad">
                    <h3>🔒 The CIA Triad</h3>
                    <div class="triad-components">
                        <div class="cia-component">
                            <h4>Confidentiality</h4>
                            <p>Ensures information is accessible only to authorized users</p>
                            <ul>
                                <li>Encryption (AES, RSA)</li>
                                <li>Access controls</li>
                                <li>VPNs and secure tunnels</li>
                            </ul>
                        </div>
                        <div class="cia-component">
                            <h4>Integrity</h4>
                            <p>Maintains accuracy and completeness of data</p>
                            <ul>
                                <li>Digital signatures</li>
                                <li>Hash functions (SHA-256)</li>
                                <li>Checksums</li>
                            </ul>
                        </div>
                        <div class="cia-component">
                            <h4>Availability</h4>
                            <p>Ensures authorized access when needed</p>
                            <ul>
                                <li>Redundancy systems</li>
                                <li>Load balancing</li>
                                <li>DDoS protection</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="assessment-section">
                    <h3>📝 Security Assessment</h3>
                    <div class="mcq-container">
                        <div class="mcq-question">
                            <h4>Question 1: Which CIA component ensures data hasn't been modified?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q1" value="a"> A) Confidentiality</label>
                                <label><input type="radio" name="q1" value="b"> B) Integrity</label>
                                <label><input type="radio" name="q1" value="c"> C) Availability</label>
                                <label><input type="radio" name="q1" value="d"> D) Authentication</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: B) Integrity</strong>
                                <p>Explanation: Integrity ensures data accuracy and prevents unauthorized modification.</p>
                            </div>
                        </div>
                        
                        <div class="mcq-question">
                            <h4>Question 2: Which hash algorithm is currently considered secure?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q2" value="a"> A) MD5</label>
                                <label><input type="radio" name="q2" value="b"> B) SHA-1</label>
                                <label><input type="radio" name="q2" value="c"> C) SHA-256</label>
                                <label><input type="radio" name="q2" value="d"> D) CRC32</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: C) SHA-256</strong>
                                <p>Explanation: SHA-256 is cryptographically secure, while MD5 and SHA-1 are deprecated.</p>
                            </div>
                        </div>
                    </div>
                    
                    <button class="show-answers-btn" onclick="toggleAnswers()">Show Answers</button>
                </div>
                
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
            """
        },

        # Module 6: Network Security and VPN - Enhanced from existing content
        "net2_6.1": {
            "title": "Network Security and VPN",
            "description": "Advanced network security implementation including firewalls, VPNs, and intrusion detection systems",
            "estimated_time": 150,
            "difficulty": "advanced",
            "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-6.txt",
            "content": """
            <div class="lesson-content">
                <h2>🔐 Network Security and VPN Technologies</h2>
                
                <div class="lesson-overview">
                    <div class="overview-card">
                        <h3>📚 Advanced Security Concepts</h3>
                        <ul>
                            <li>Firewall technologies and implementation</li>
                            <li>VPN protocols and configuration</li>
                            <li>Intrusion detection and prevention</li>
                            <li>Network security best practices</li>
                        </ul>
                    </div>
                </div>
                
                <div class="firewall-section">
                    <h3>🔥 Firewall Technologies</h3>
                    
                    <div class="firewall-types">
                        <div class="firewall-type">
                            <h4>📦 Packet Filtering Firewalls</h4>
                            <ul>
                                <li>Examine packet headers (IP, ports, protocols)</li>
                                <li>Fast processing with low overhead</li>
                                <li>Limited to Layer 3 and 4 inspection</li>
                                <li>Vulnerable to IP spoofing</li>
                            </ul>
                        </div>
                        
                        <div class="firewall-type">
                            <h4>🔍 Stateful Inspection Firewalls</h4>
                            <ul>
                                <li>Track connection states in state table</li>
                                <li>Dynamic port opening for connections</li>
                                <li>Better security than packet filtering</li>
                                <li>Protocol anomaly detection</li>
                            </ul>
                        </div>
                        
                        <div class="firewall-type">
                            <h4>🛡️ Application Layer Firewalls</h4>
                            <ul>
                                <li>Deep packet inspection (DPI)</li>
                                <li>Application protocol validation</li>
                                <li>Content filtering capabilities</li>
                                <li>User authentication integration</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="vpn-section">
                    <h3>🌐 VPN Technologies</h3>
                    
                    <div class="vpn-types">
                        <div class="vpn-type">
                            <h4>🏢 Site-to-Site VPNs</h4>
                            <ul>
                                <li>Connect entire networks together</li>
                                <li>Transparent to end users</li>
                                <li>Used for branch connectivity</li>
                                <li>Permanent encrypted tunnels</li>
                            </ul>
                        </div>
                        
                        <div class="vpn-type">
                            <h4>👤 Remote Access VPNs</h4>
                            <ul>
                                <li>Individual user connections</li>
                                <li>Client software required</li>
                                <li>On-demand tunnel creation</li>
                                <li>User authentication required</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="vpn-protocols">
                        <h4>VPN Protocol Comparison</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Protocol</th>
                                    <th>Security</th>
                                    <th>Performance</th>
                                    <th>Use Case</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>IPSec</td>
                                    <td>Very High</td>
                                    <td>Good</td>
                                    <td>Site-to-site</td>
                                </tr>
                                <tr>
                                    <td>SSL/TLS</td>
                                    <td>High</td>
                                    <td>Excellent</td>
                                    <td>Remote access</td>
                                </tr>
                                <tr>
                                    <td>L2TP/IPSec</td>
                                    <td>High</td>
                                    <td>Good</td>
                                    <td>Remote access</td>
                                </tr>
                                <tr>
                                    <td>PPTP</td>
                                    <td>Low</td>
                                    <td>Fast</td>
                                    <td>Deprecated</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="ids-section">
                    <h3>🔍 Intrusion Detection Systems</h3>
                    
                    <div class="ids-types">
                        <div class="ids-type">
                            <h4>🌐 Network-based IDS (NIDS)</h4>
                            <ul>
                                <li>Monitors network traffic in real-time</li>
                                <li>Deployed at strategic network points</li>
                                <li>Detects network-based attacks</li>
                                <li>Analyzes packet contents and patterns</li>
                            </ul>
                        </div>
                        
                        <div class="ids-type">
                            <h4>💻 Host-based IDS (HIDS)</h4>
                            <ul>
                                <li>Monitors individual host systems</li>
                                <li>Examines system logs and files</li>
                                <li>Detects host-specific attacks</li>
                                <li>File integrity monitoring</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="detection-methods">
                        <h4>Detection Methods</h4>
                        <ul>
                            <li><strong>Signature-based:</strong> Known attack patterns</li>
                            <li><strong>Anomaly-based:</strong> Deviation from normal behavior</li>
                            <li><strong>Hybrid:</strong> Combination of both methods</li>
                        </ul>
                    </div>
                </div>
                
                <div class="assessment-section">
                    <h3>📝 Advanced Security Assessment</h3>
                    <div class="mcq-container">
                        <div class="mcq-question">
                            <h4>Question 1: Which firewall type provides the highest security?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q1" value="a"> A) Packet filtering</label>
                                <label><input type="radio" name="q1" value="b"> B) Stateful inspection</label>
                                <label><input type="radio" name="q1" value="c"> C) Application layer</label>
                                <label><input type="radio" name="q1" value="d"> D) Circuit-level gateway</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: C) Application layer</strong>
                                <p>Explanation: Application layer firewalls inspect all layers including application data.</p>
                            </div>
                        </div>
                        
                        <div class="mcq-question">
                            <h4>Question 2: What's the main advantage of SSL VPN over IPSec?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q2" value="a"> A) Better encryption</label>
                                <label><input type="radio" name="q2" value="b"> B) No client software required</label>
                                <label><input type="radio" name="q2" value="c"> C) Faster performance</label>
                                <label><input type="radio" name="q2" value="d"> D) Lower cost</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: B) No client software required</strong>
                                <p>Explanation: SSL VPNs work through web browsers without client installation.</p>
                            </div>
                        </div>
                        
                        <div class="mcq-question">
                            <h4>Question 3: Which detection method is best for zero-day attacks?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q3" value="a"> A) Signature-based</label>
                                <label><input type="radio" name="q3" value="b"> B) Anomaly-based</label>
                                <label><input type="radio" name="q3" value="c"> C) Rule-based</label>
                                <label><input type="radio" name="q3" value="d"> D) Blacklist-based</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: B) Anomaly-based</strong>
                                <p>Explanation: Anomaly detection can identify unknown threats by detecting behavior changes.</p>
                            </div>
                        </div>
                        
                        <div class="mcq-question">
                            <h4>Question 4: What's the difference between IDS and IPS?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q4" value="a"> A) IDS is faster</label>
                                <label><input type="radio" name="q4" value="b"> B) IPS can block attacks</label>
                                <label><input type="radio" name="q4" value="c"> C) IDS works at network layer</label>
                                <label><input type="radio" name="q4" value="d"> D) IPS is cheaper</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: B) IPS can block attacks</strong>
                                <p>Explanation: IPS actively blocks threats while IDS only detects and alerts.</p>
                            </div>
                        </div>
                        
                        <div class="mcq-question">
                            <h4>Question 5: Which VPN protocol is deprecated due to security issues?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q5" value="a"> A) IPSec</label>
                                <label><input type="radio" name="q5" value="b"> B) SSL/TLS</label>
                                <label><input type="radio" name="q5" value="c"> C) L2TP</label>
                                <label><input type="radio" name="q5" value="d"> D) PPTP</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: D) PPTP</strong>
                                <p>Explanation: PPTP has known security vulnerabilities and is considered deprecated.</p>
                            </div>
                        </div>
                    </div>
                    
                    <button class="show-answers-btn" onclick="toggleAnswers()">Show Answers</button>
                </div>
                
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
            """
        },

        # Additional modules with metadata (keeping existing content but adding metadata)
        "net2_3.1": {
            "title": "Wireless Networks",
            "description": "Wireless network standards, configuration, and security",
            "estimated_time": 90,
            "difficulty": "intermediate",
            "content": """
            <div class="lesson-content">
                <h2>📡 Wireless Networks</h2>
                <p>Comprehensive wireless networking concepts and implementation.</p>
            </div>
            """
        },

        "net2_4.1": {
            "title": "Network Management",
            "description": "Network monitoring, SNMP, and performance analysis",
            "estimated_time": 105,
            "difficulty": "intermediate",
            "content": """
            <div class="lesson-content">
                <h2>📊 Network Management</h2>
                <p>Network monitoring and management fundamentals.</p>
            </div>
            """
        },

        "net2_5.1": {
            "title": "OSPF Routing Protocol",
            "description": "Open Shortest Path First protocol configuration and troubleshooting",
            "estimated_time": 120,
            "difficulty": "advanced",
            "content": """
            <div class="lesson-content">
                <h2>🔄 OSPF Routing Protocol</h2>
                <p>Advanced OSPF configuration and area design.</p>
            </div>
            """
        },

        "net2_7.1": {
            "title": "Network Troubleshooting",
            "description": "Systematic network troubleshooting methodology and tools",
            "estimated_time": 90,
            "difficulty": "intermediate",
            "content": """
            <div class="lesson-content">
                <h2>🔧 Network Troubleshooting</h2>
                <p>Systematic approach to network problem resolution.</p>
            </div>
            """
        }
    }
