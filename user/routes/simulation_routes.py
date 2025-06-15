from flask import Blueprint, render_template
from flask_login import login_required

# Create simulation routes blueprint
simulation_bp = Blueprint('simulation', __name__)

@simulation_bp.route('/networking1-simulations')
@login_required
def networking1_simulations():
    """Main Networking 1 simulations hub"""
    return render_template('user/networking1_simulations.html')

@simulation_bp.route('/networking1-components-simulation')
@login_required
def networking1_components_simulation():
    """Network Components Builder Simulation"""
    return render_template('user/networking1-components-simulation.html')

@simulation_bp.route('/networking1-osi-simulation')
@login_required
def networking1_osi_simulation():
    """OSI Model Interactive Simulation"""
    return render_template('user/networking1-osi-simulation.html')

@simulation_bp.route('/networking1-tcpip-simulation')
@login_required
def networking1_tcpip_simulation():
    """TCP/IP Protocol Stack Simulation"""
    return render_template('user/networking1-tcpip-simulation.html')

@simulation_bp.route('/networking1-ethernet-simulation')
@login_required
def networking1_ethernet_simulation():
    """Ethernet Technology Simulation"""
    return render_template('user/networking1-ethernet-simulation.html')

@simulation_bp.route('/networking1-application-simulation')
@login_required
def networking1_application_simulation():
    """Application Layer Protocols Simulation"""
    return render_template('user/networking1-application-simulation.html')

@simulation_bp.route('/networking1-datalink-simulation')
@login_required
def networking1_datalink_simulation():
    """Data Link Layer Flow Control Simulation"""
    return render_template('user/networking1-datalink-simulation.html')

# Networking 2 Simulations Hub and Individual Modules

@simulation_bp.route('/networking2-simulations')
@login_required
def networking2_simulations():
    """Main Networking 2 simulations hub"""
    return render_template('user/networking2_simulations.html')

# Core Module Simulations

@simulation_bp.route('/networking2-routing-fundamentals-simulation')
@login_required
def networking2_routing_fundamentals_simulation():
    """Module 1: Routing Fundamentals Simulation"""
    return render_template('user/networking2-routing-fundamentals-simulation.html')

@simulation_bp.route('/networking2-dynamic-routing-simulation')
@login_required
def networking2_dynamic_routing_simulation():
    """Module 2: Dynamic Routing Protocols Simulation"""
    return render_template('user/networking2-dynamic-routing-simulation.html')

@simulation_bp.route('/networking2-rip-simulation')
@login_required
def networking2_rip_simulation():
    """Module 3: Routing Information Protocol (RIP) Simulation"""
    return render_template('user/networking2-rip-simulation.html')

@simulation_bp.route('/networking2-eigrp-simulation')
@login_required
def networking2_eigrp_simulation():
    """Module 4: Enhanced Interior Gateway Routing Protocol (EIGRP) Simulation"""
    return render_template('user/networking2-eigrp-simulation.html')

@simulation_bp.route('/networking2-ospf-simulation')
@login_required
def networking2_ospf_simulation():
    """Module 5: Open Shortest Path First (OSPF) Simulation"""
    return render_template('user/networking2-ospf-simulation.html')

@simulation_bp.route('/networking2-security-simulation')
@login_required
def networking2_security_simulation():
    """Module 6: Network Security and VPN Simulation"""
    return render_template('user/networking2-security-simulation.html')

@simulation_bp.route('/networking2-vlan-simulation')
@login_required
def networking2_vlan_simulation():
    """Module 7: VLAN Trunking Protocol Simulation"""
    return render_template('user/networking2-vlan-simulation.html')

# Additional Specialized Simulations

@simulation_bp.route('/networking2-routing-simulation')
@login_required
def networking2_routing_simulation():
    """Advanced Routing Simulation"""
    return render_template('user/networking2-routing-simulation.html')

@simulation_bp.route('/networking2-wireless-simulation')
@login_required
def networking2_wireless_simulation():
    """Wireless Networks Simulation"""
    return render_template('user/networking2-wireless-simulation.html')

@simulation_bp.route('/networking2-management-simulation')
@login_required
def networking2_management_simulation():
    """Network Management Simulation"""
    return render_template('user/networking2-management-simulation.html')

@simulation_bp.route('/networking2-vpn-simulation')
@login_required
def networking2_vpn_simulation():
    """VPN Technologies Simulation"""
    return render_template('user/networking2-vpn-simulation.html')

@simulation_bp.route('/networking2-troubleshooting-simulation')
@login_required
def networking2_troubleshooting_simulation():
    """Network Troubleshooting Simulation"""
    return render_template('user/networking2-troubleshooting-simulation.html')