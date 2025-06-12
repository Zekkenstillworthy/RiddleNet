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
        # Module 1: Routing Fundamentals
        "net2_1.1": {
            "title": "Routing Fundamentals",
            "description": "Comprehensive introduction to routing concepts, static and dynamic routing, and fundamental routing principles",
            "estimated_time": 90,
            "difficulty": "intermediate",
            "source_file": "ISLES-LSPU-Sample-Module-in-Networking-2-Module-1.txt",
            "content": """
            <div class="lesson-content">
                <h2>Routing Fundamentals</h2>
                
                <div class="lesson-overview">
                    <div class="overview-card">
                        <h3>📚 What You'll Learn</h3>
                        <ul>
                            <li>Understanding router functions and operations</li>
                            <li>Routing table structure and maintenance</li>
                            <li>Static vs. dynamic routing concepts</li>
                            <li>Load balancing implementation</li>
                            <li>Default route configuration</li>
                        </ul>
                    </div>
                </div>
                
                <div class="learning-outcomes">
                    <h3>🎯 Learning Outcomes</h3>
                    <div class="outcomes-grid">
                        <div class="outcome-item">
                            <h4>Technical Skills</h4>
                            <ul>
                                <li>Define routing and its importance</li>
                                <li>Configure static routing</li>
                                <li>Implement load balancing</li>
                                <li>Identify default routes</li>
                            </ul>
                        </div>
                        <div class="outcome-item">
                            <h4>Practical Applications</h4>
                            <ul>
                                <li>Corporate network routing implementation</li>
                                <li>Network troubleshooting techniques</li>
                                <li>Performance optimization strategies</li>
                                <li>Routing protocol selection</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="theoretical-foundation">
                    <h3>🏗️ Theoretical Foundation</h3>
                    
                    <div class="theory-section">
                        <h4>What is Routing?</h4>
                        <div class="definition-box">
                            <p><strong>Routing</strong> is the process of selecting paths in a network along which to send network traffic. 
                            It involves determining the best path for data packets to travel from source to destination across 
                            interconnected networks.</p>
                        </div>
                        
                        <div class="key-concepts">
                            <h5>Core Routing Concepts:</h5>
                            <ul>
                                <li><strong>Router:</strong> A network device that forwards data packets between computer networks</li>
                                <li><strong>Routing Table:</strong> A data table stored in a router that lists routes to network destinations</li>
                                <li><strong>Metric:</strong> A value used to determine the best path to a destination</li>
                                <li><strong>Next Hop:</strong> The next router in the path to the destination</li>
                                <li><strong>Administrative Distance:</strong> A rating of trustworthiness for routing information</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="theory-section">
                        <h4>Router Functions</h4>
                        <div class="function-grid">
                            <div class="function-card">
                                <h5>🎯 Path Determination</h5>
                                <p>Routers analyze available paths to destinations and select the optimal route based on 
                                routing metrics such as hop count, bandwidth, delay, and cost.</p>
                            </div>
                            <div class="function-card">
                                <h5>📦 Packet Forwarding</h5>
                                <p>Once the best path is determined, routers forward packets from the source interface 
                                to the appropriate destination interface.</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="theory-section">
                        <h4>Routing Table Components</h4>
                        <div class="table-structure">
                            <div class="table-component">
                                <h5>Destination Network</h5>
                                <p>The network address that can be reached</p>
                            </div>
                            <div class="table-component">
                                <h5>Subnet Mask</h5>
                                <p>Defines the network and host portions of the address</p>
                            </div>
                            <div class="table-component">
                                <h5>Next Hop/Gateway</h5>
                                <p>The IP address of the next router in the path</p>
                            </div>
                            <div class="table-component">
                                <h5>Interface</h5>
                                <p>The local interface used to reach the destination</p>
                            </div>
                            <div class="table-component">
                                <h5>Metric</h5>
                                <p>The cost associated with the route</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="practical-implementation">
                    <h3>⚙️ Practical Implementation</h3>
                    
                    <div class="implementation-section">
                        <h4>Static Routing Configuration</h4>
                        <div class="config-example">
                            <div class="config-header">
                                <h5>Basic Static Route Command</h5>
                            </div>
                            <div class="config-code">
                                <pre><code>ip route [destination_network] [subnet_mask] [next_hop_ip]

Example:
Router(config)# ip route 192.168.2.0 255.255.255.0 10.0.0.2
</code></pre>
                            </div>
                            <div class="config-explanation">
                                <p>This command creates a static route to network 192.168.2.0/24 via next hop 10.0.0.2</p>
                            </div>
                        </div>
                        
                        <div class="config-example">
                            <div class="config-header">
                                <h5>Default Route Configuration</h5>
                            </div>
                            <div class="config-code">
                                <pre><code>ip route 0.0.0.0 0.0.0.0 [next_hop_ip]

Example:
Router(config)# ip route 0.0.0.0 0.0.0.0 203.0.113.1
</code></pre>
                            </div>
                            <div class="config-explanation">
                                <p>Default route (gateway of last resort) for destinations not in routing table</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="implementation-section">
                        <h4>Load Balancing</h4>
                        <div class="load-balancing-info">
                            <h5>Equal Cost Load Balancing</h5>
                            <p>When multiple paths to a destination have the same metric, traffic is distributed across all paths:</p>
                            <ul>
                                <li>Automatic load distribution</li>
                                <li>Improved network utilization</li>
                                <li>Redundancy and fault tolerance</li>
                                <li>Better performance under high traffic</li>
                            </ul>
                            
                            <div class="config-code">
                                <pre><code>Router(config)# ip route 192.168.1.0 255.255.255.0 10.0.0.1
Router(config)# ip route 192.168.1.0 255.255.255.0 10.0.0.2
</code></pre>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="verification-commands">
                    <h3>🔍 Verification Commands</h3>
                    <div class="command-list">
                        <div class="command-item">
                            <h5>show ip route</h5>
                            <p>Displays the complete routing table with all routes</p>
                        </div>
                        <div class="command-item">
                            <h5>show ip route static</h5>
                            <p>Shows only static routes in the routing table</p>
                        </div>
                        <div class="command-item">
                            <h5>show running-config | include route</h5>
                            <p>Displays configured static routes in the configuration</p>
                        </div>
                    </div>
                </div>
                
                <div class="assessment-section">
                    <h3>📝 Knowledge Check</h3>
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
                                <p>Explanation: Routers have two primary functions - determining the best path to destinations and forwarding packets along those paths.</p>
                            </div>
                        </div>
                        
                        <div class="mcq-question">
                            <h4>Question 2: What does the command "ip route 0.0.0.0 0.0.0.0 192.168.1.1" configure?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q2" value="a"> A) A static route to a specific network</label>
                                <label><input type="radio" name="q2" value="b"> B) A default route (gateway of last resort)</label>
                                <label><input type="radio" name="q2" value="c"> C) A host route</label>
                                <label><input type="radio" name="q2" value="d"> D) A loopback route</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: B) A default route (gateway of last resort)</strong>
                                <p>Explanation: The 0.0.0.0 0.0.0.0 destination matches all networks, making it a default route.</p>
                            </div>
                        </div>
                        
                        <div class="mcq-question">
                            <h4>Question 3: Which factor is NOT typically used as a routing metric?</h4>
                            <div class="mcq-options">
                                <label><input type="radio" name="q3" value="a"> A) Bandwidth</label>
                                <label><input type="radio" name="q3" value="b"> B) Delay</label>
                                <label><input type="radio" name="q3" value="c"> C) MAC address</label>
                                <label><input type="radio" name="q3" value="d"> D) Hop count</label>
                            </div>
                            <div class="mcq-answer" style="display:none;">
                                <strong>Answer: C) MAC address</strong>
                                <p>Explanation: MAC addresses are Layer 2 identifiers and are not used as routing metrics. Routing operates at Layer 3.</p>
                            </div>
                        </div>
                    </div>
                    
                    <button class="show-answers-btn" onclick="toggleAnswers()">Show Answers</button>
                </div>
                
                <div class="practical-exercises">
                    <h3>🔧 Hands-on Exercises</h3>
                    <div class="exercise-list">
                        <div class="exercise-item">
                            <h4>Exercise 1: Basic Static Routing</h4>
                            <p>Configure static routes between three networks: 192.168.1.0/24, 192.168.2.0/24, and 192.168.3.0/24</p>
                            <div class="exercise-steps">
                                <ol>
                                    <li>Set up the network topology</li>
                                    <li>Configure IP addresses on interfaces</li>
                                    <li>Add static routes for inter-network communication</li>
                                    <li>Test connectivity using ping</li>
                                    <li>Verify routes using show commands</li>
                                </ol>
                            </div>
                        </div>
                        
                        <div class="exercise-item">
                            <h4>Exercise 2: Load Balancing Implementation</h4>
                            <p>Configure equal-cost load balancing with redundant paths</p>
                            <div class="exercise-steps">
                                <ol>
                                    <li>Create redundant paths between networks</li>
                                    <li>Configure multiple static routes with equal metrics</li>
                                    <li>Test load distribution</li>
                                    <li>Simulate link failure and observe failover</li>
                                </ol>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="industry-relevance">
                    <h3>🏢 Industry Applications</h3>
                    <div class="application-grid">
                        <div class="application-card">
                            <h4>Enterprise Networks</h4>
                            <p>Large corporations use complex routing to connect multiple sites, data centers, and cloud services efficiently.</p>
                        </div>
                        <div class="application-card">
                            <h4>Service Providers</h4>
                            <p>ISPs use advanced routing protocols to manage traffic across vast networks and provide reliable internet services.</p>
                        </div>
                        <div class="application-card">
                            <h4>Data Centers</h4>
                            <p>Modern data centers implement sophisticated routing for load balancing, redundancy, and optimal resource utilization.</p>
                        </div>
                        <div class="application-card">
                            <h4>Cloud Computing</h4>
                            <p>Cloud providers use dynamic routing to automatically adapt to changing network conditions and optimize performance.</p>
                        </div>
                    </div>
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

        "net2_1.2": {
            "title": "Dynamic Routing Protocols",
            "description": "Understanding dynamic routing protocols, their operation, and comparison with static routing",
            "estimated_time": 75,
            "difficulty": "intermediate",
            "content": """
            <div class="lesson-content">
                <h2>Dynamic Routing Protocols</h2>
                
                <div class="lesson-overview">
                    <div class="overview-card">
                        <h3>📚 What You'll Learn</h3>
                        <ul>
                            <li>Dynamic vs. static routing comparison</li>
                            <li>Types of routing protocols and their characteristics</li>
                            <li>Routing metrics and administrative distance</li>
                            <li>Protocol convergence and loop prevention</li>
                        </ul>
                    </div>
                </div>
                
                <div class="theoretical-foundation">
                    <h3>🏗️ Dynamic Routing Fundamentals</h3>
                    
                    <div class="comparison-section">
                        <h4>Static vs. Dynamic Routing</h4>
                        <div class="comparison-table">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Aspect</th>
                                        <th>Static Routing</th>
                                        <th>Dynamic Routing</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Configuration</td>
                                        <td>Manual configuration required</td>
                                        <td>Automatic route learning</td>
                                    </tr>
                                    <tr>
                                        <td>Adaptability</td>
                                        <td>No automatic adaptation</td>
                                        <td>Adapts to network changes</td>
                                    </tr>
                                    <tr>
                                        <td>CPU Usage</td>
                                        <td>Low CPU overhead</td>
                                        <td>Higher CPU overhead</td>
   