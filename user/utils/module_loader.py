"""
Module content loader for the RiddleNet learning platform.
This module loads extracted content from .docx files and provides it 
in the format expected by the learning platform.
"""

from extracted_module_content import MODULE_CONTENT

def get_module_content():
    """
    Get all extracted module content from .docx files.
    Returns a dictionary with lesson IDs as keys and lesson data as values.
    """
    return MODULE_CONTENT

def enhance_content_with_interactivity(content, lesson_id):
    """
    Enhance extracted content with interactive elements like quizzes and activities.
    This can be expanded to add more interactive features in the future.
    """
    # Add a basic quiz section for certain lessons
    quiz_content = ""
    
    if lesson_id == "1.1":
        quiz_content = '''
            <div class="quiz-section">
                <h3>Quick Check</h3>
                <div class="quiz-question">
                    <p>What is the primary purpose of computer networks?</p>
                    <div class="quiz-options">
                        <div class="quiz-option" data-correct="false">
                            <input type="radio" name="q1" id="q1a">
                            <label for="q1a">Running software applications</label>
                        </div>
                        <div class="quiz-option" data-correct="true">
                            <input type="radio" name="q1" id="q1b">
                            <label for="q1b">Sharing resources and enabling communication</label>
                        </div>
                        <div class="quiz-option" data-correct="false">
                            <input type="radio" name="q1" id="q1c">
                            <label for="q1c">Storing data locally</label>
                        </div>
                        <div class="quiz-option" data-correct="false">
                            <input type="radio" name="q1" id="q1d">
                            <label for="q1d">Processing graphics</label>
                        </div>
                    </div>
                    <div class="quiz-feedback"></div>
                </div>
            </div>
        '''
    elif lesson_id == "2.1":
        quiz_content = '''
            <div class="quiz-section">
                <h3>Quick Check</h3>
                <div class="quiz-question">
                    <p>Which OSI layer does the Data Link Layer correspond to?</p>
                    <div class="quiz-options">
                        <div class="quiz-option" data-correct="false">
                            <input type="radio" name="q1" id="q1a">
                            <label for="q1a">Layer 1</label>
                        </div>
                        <div class="quiz-option" data-correct="true">
                            <input type="radio" name="q1" id="q1b">
                            <label for="q1b">Layer 2</label>
                        </div>
                        <div class="quiz-option" data-correct="false">
                            <input type="radio" name="q1" id="q1c">
                            <label for="q1c">Layer 3</label>
                        </div>
                        <div class="quiz-option" data-correct="false">
                            <input type="radio" name="q1" id="q1d">
                            <label for="q1d">Layer 4</label>
                        </div>
                    </div>
                    <div class="quiz-feedback"></div>
                </div>
            </div>
        '''
    
    # Insert quiz content before the closing </div> of lesson-content
    if quiz_content and content:
        # Find the last </div> and insert quiz before it
        content = content.rstrip()
        if content.endswith('</div>'):
            content = content[:-6] + quiz_content + '\n                </div>'
        else:
            content += quiz_content
    
    return content

def get_enhanced_lesson_content():
    """
    Get module content enhanced with interactive elements.
    Returns content in the same format as the original hardcoded lessons.
    """
    enhanced_content = {}
    
    for lesson_id, lesson_data in MODULE_CONTENT.items():
        enhanced_lesson_content = enhance_content_with_interactivity(
            lesson_data["content"], 
            lesson_id
        )
        
        enhanced_content[lesson_id] = {
            "title": lesson_data["title"],
            "content": enhanced_lesson_content
        }
    
    return enhanced_content

# Fallback content for lessons not yet extracted from documents
FALLBACK_CONTENT = {
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
                            <h4>LAN (Local Area Network)</h4>
                            <p>Networks limited to a small geographical area like a home, office, or building.</p>
                        </div>
                    </div>
                </div>
            </div>
        """
    }
}

def get_all_lesson_content():
    """
    Get all lesson content, combining extracted content with fallback content.
    """
    all_content = {}
    
    # Add extracted content
    all_content.update(get_enhanced_lesson_content())
    
    # Add fallback content for missing lessons
    all_content.update(FALLBACK_CONTENT)
    
    return all_content
