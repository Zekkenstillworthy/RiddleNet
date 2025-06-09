"""
Module content loader for RiddleNet Networking 2 learning platform.
Loads extracted content from networking 2 .docx files.
"""

from extracted_networking2_content import NETWORKING2_MODULE_CONTENT

def get_networking2_lesson_content():
    """
    Returns lesson content extracted from networking 2 .docx module files.
    Falls back to basic content for missing lessons.
    """
    # Start with extracted content
    lesson_content = {}
    
    # Add extracted module content
    for lesson_id, content in NETWORKING2_MODULE_CONTENT.items():
        lesson_content[lesson_id] = {
            "title": content["title"],
            "content": content["content"]
        }
    
    # Add fallback content for missing lessons to maintain compatibility
    fallback_lessons = {
        "1.2": {
            "title": "Advanced Routing Concepts",
            "content": """
                <div class="lesson-content">
                    <h2>Advanced Routing Concepts</h2>
                    
                    <div class="lesson-section">
                        <h3>Dynamic Routing Protocols</h3>
                        <p>Dynamic routing protocols automatically update routing tables and adapt to network changes.</p>
                        
                        <div class="info-box">
                            <h4>Key Concept</h4>
                            <p>Dynamic routing protocols like OSPF, EIGRP, and BGP provide automated route discovery and maintenance.</p>
                        </div>
                    </div>
                    
                    <div class="lesson-section">
                        <h3>Routing Protocol Types</h3>
                        <p>Routing protocols are classified into different categories:</p>
                        <div class="routing-types">
                            <div class="routing-type">
                                <div class="type-number">1</div>
                                <div class="type-name">Distance Vector</div>
                                <div class="type-desc">RIP, EIGRP - Exchange routing tables with neighbors</div>
                            </div>
                            <div class="routing-type">
                                <div class="type-number">2</div>
                                <div class="type-name">Link State</div>
                                <div class="type-desc">OSPF, IS-IS - Build complete network topology map</div>
                            </div>
                            <div class="routing-type">
                                <div class="type-number">3</div>
                                <div class="type-name">Path Vector</div>
                                <div class="type-desc">BGP - Maintains path information to prevent loops</div>
                            </div>
                        </div>
                    </div>
                </div>
            """
        },
        "2.2": {
            "title": "Network Security Implementation",
            "content": """
                <div class="lesson-content">
                    <h2>Network Security Implementation</h2>
                    
                    <div class="lesson-section">
                        <h3>Security Policies and Procedures</h3>
                        <p>Implementing comprehensive network security requires well-defined policies and procedures.</p>
                        
                        <div class="security-components">
                            <div class="component">
                                <h4>Firewalls</h4>
                                <p>Control network traffic based on predetermined security rules</p>
                            </div>
                            <div class="component">
                                <h4>VPNs</h4>
                                <p>Secure remote access and site-to-site connections</p>
                            </div>
                            <div class="component">
                                <h4>IDS/IPS</h4>
                                <p>Intrusion detection and prevention systems</p>
                            </div>
                        </div>
                    </div>
                </div>
            """
        }
    }
    
    # Add fallback lessons for missing content
    for lesson_id, lesson_data in fallback_lessons.items():
        if lesson_id not in lesson_content:
            lesson_content[lesson_id] = lesson_data
    
    return lesson_content

def get_networking2_module_structure():
    """
    Returns the module structure for networking 2
    """
    return {
        "1": {
            "title": "Advanced Routing",
            "lessons": ["1.1", "1.2", "1.3", "1.4"]
        },
        "2": {
            "title": "Network Security",
            "lessons": ["2.1", "2.2", "2.3", "2.4"]
        },
        "3": {
            "title": "Network Management",
            "lessons": ["3.1", "3.2", "3.3", "3.4"]
        },
        "4": {
            "title": "Advanced Topics",
            "lessons": ["4.1", "4.2", "4.3", "4.4"]
        },
        "5": {
            "title": "Network Design",
            "lessons": ["5.1", "5.2", "5.3", "5.4"]
        },
        "7": {
            "title": "Network Troubleshooting",
            "lessons": ["7.1", "7.2", "7.3", "7.4"]
        }
    }
