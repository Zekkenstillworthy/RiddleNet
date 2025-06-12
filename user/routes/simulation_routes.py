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

# Additional networking simulations can be added here
# For example, for Networking 2 module:

@simulation_bp.route('/networking2-simulations')
@login_required
def networking2_simulations():
    """Main Networking 2 simulations hub (placeholder)"""
    # This can be implemented when Networking 2 simulations are created
    return render_template('user/networking2_simulations.html')