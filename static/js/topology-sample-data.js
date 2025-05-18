// Sample topology data for when the API is not working
const sampleTopologies = [
    {
        id: 1,
        title: "Point-to-Point Network",
        description: "A point-to-point network topology consists of a direct connection between two devices.",
        topology_type: "point-to-point",
        difficulty: "easy",
        base_score: 100,
        time_bonus: 20,
        perfect_match_bonus: 10,
        is_active: true,
        initial_config: {
            devices: [],
            connections: []
        },
        expected_config: {
            devices: [
                {id: "pc1", type: "pc", name: "PC-1", x: 0.3, y: 0.5},
                {id: "pc2", type: "pc", name: "PC-2", x: 0.7, y: 0.5}
            ],
            connections: [
                {source: "pc1", target: "pc2"}
            ]
        },
        scoring_metrics: {
            time_efficiency: 10,
            config_process: 25,
            design_layout: 20,
            completeness: 20,
            correctness: 25
        }
    },
    {
        id: 2,
        title: "Star Network",
        description: "A star network topology consists of one central device that's connected to multiple peripheral devices.",
        topology_type: "star",
        difficulty: "medium",
        base_score: 150,
        time_bonus: 30,
        perfect_match_bonus: 15,
        is_active: true,
        initial_config: {
            devices: [
                {id: "sw1", type: "switch", name: "Core Switch", x: 0.5, y: 0.3}
            ],
            connections: []
        },
        expected_config: {
            devices: [
                {id: "sw1", type: "switch", name: "Core Switch", x: 0.5, y: 0.3},
                {id: "pc1", type: "pc", name: "PC-1", x: 0.3, y: 0.6},
                {id: "pc2", type: "pc", name: "PC-2", x: 0.5, y: 0.6},
                {id: "pc3", type: "pc", name: "PC-3", x: 0.7, y: 0.6}
            ],
            connections: [
                {source: "sw1", target: "pc1"},
                {source: "sw1", target: "pc2"},
                {source: "sw1", target: "pc3"}
            ]
        },
        scoring_metrics: {
            time_efficiency: 15,
            config_process: 20,
            design_layout: 25,
            completeness: 20,
            correctness: 20
        }
    },
    {
        id: 3,
        title: "Mesh Network",
        description: "A mesh network topology consists of devices that are all connected to each other, creating multiple paths for data.",
        topology_type: "mesh",
        difficulty: "hard",
        base_score: 200,
        time_bonus: 40,
        perfect_match_bonus: 20,
        is_active: true,
        initial_config: {
            devices: [],
            connections: []
        },
        expected_config: {
            devices: [
                {id: "r1", type: "router", name: "Router 1", x: 0.3, y: 0.3},
                {id: "r2", type: "router", name: "Router 2", x: 0.7, y: 0.3},
                {id: "r3", type: "router", name: "Router 3", x: 0.3, y: 0.7},
                {id: "r4", type: "router", name: "Router 4", x: 0.7, y: 0.7}
            ],
            connections: [
                {source: "r1", target: "r2"},
                {source: "r1", target: "r3"},
                {source: "r1", target: "r4"},
                {source: "r2", target: "r3"},
                {source: "r2", target: "r4"},
                {source: "r3", target: "r4"}
            ]
        },
        scoring_metrics: {
            time_efficiency: 20,
            config_process: 20,
            design_layout: 20,
            completeness: 20,
            correctness: 20
        }
    },
    {
        id: 4,
        title: "Bus Network",
        description: "A bus network topology consists of a central cable to which all nodes connect.",
        topology_type: "bus",
        difficulty: "easy",
        base_score: 100,
        time_bonus: 20,
        perfect_match_bonus: 10,
        is_active: true,
        initial_config: {
            devices: [
                {id: "bus", type: "bus", name: "Main Bus", x: 0.5, y: 0.4}
            ],
            connections: []
        },
        expected_config: {
            devices: [
                {id: "bus", type: "bus", name: "Main Bus", x: 0.5, y: 0.4},
                {id: "pc1", type: "pc", name: "PC-1", x: 0.2, y: 0.6},
                {id: "pc2", type: "pc", name: "PC-2", x: 0.4, y: 0.6},
                {id: "pc3", type: "pc", name: "PC-3", x: 0.6, y: 0.6},
                {id: "pc4", type: "pc", name: "PC-4", x: 0.8, y: 0.6}
            ],
            connections: [
                {source: "bus", target: "pc1"},
                {source: "bus", target: "pc2"},
                {source: "bus", target: "pc3"},
                {source: "bus", target: "pc4"}
            ]
        }
    },
    {
        id: 5,
        title: "Ring Network",
        description: "A ring network topology consists of devices connected in a circular fashion.",
        topology_type: "ring",
        difficulty: "medium",
        base_score: 150,
        time_bonus: 30,
        perfect_match_bonus: 15,
        is_active: true,
        initial_config: {
            devices: [],
            connections: []
        },
        expected_config: {
            devices: [
                {id: "sw1", type: "switch", name: "Switch 1", x: 0.3, y: 0.3},
                {id: "sw2", type: "switch", name: "Switch 2", x: 0.7, y: 0.3},
                {id: "sw3", type: "switch", name: "Switch 3", x: 0.7, y: 0.7},
                {id: "sw4", type: "switch", name: "Switch 4", x: 0.3, y: 0.7}
            ],
            connections: [
                {source: "sw1", target: "sw2"},
                {source: "sw2", target: "sw3"},
                {source: "sw3", target: "sw4"},
                {source: "sw4", target: "sw1"}
            ]
        }
    },
    {
        id: 6,
        title: "Tree Network",
        description: "A tree network topology consists of a root node connected to child nodes in a hierarchical structure.",
        topology_type: "tree",
        difficulty: "medium",
        base_score: 150,
        time_bonus: 30,
        perfect_match_bonus: 15,
        is_active: true,
        initial_config: {
            devices: [
                {id: "r1", type: "router", name: "Root Router", x: 0.5, y: 0.2}
            ],
            connections: []
        },
        expected_config: {
            devices: [
                {id: "r1", type: "router", name: "Root Router", x: 0.5, y: 0.2},
                {id: "sw1", type: "switch", name: "Switch 1", x: 0.3, y: 0.4},
                {id: "sw2", type: "switch", name: "Switch 2", x: 0.7, y: 0.4},
                {id: "pc1", type: "pc", name: "PC-1", x: 0.2, y: 0.6},
                {id: "pc2", type: "pc", name: "PC-2", x: 0.4, y: 0.6},
                {id: "pc3", type: "pc", name: "PC-3", x: 0.6, y: 0.6},
                {id: "pc4", type: "pc", name: "PC-4", x: 0.8, y: 0.6}
            ],
            connections: [
                {source: "r1", target: "sw1"},
                {source: "r1", target: "sw2"},
                {source: "sw1", target: "pc1"},
                {source: "sw1", target: "pc2"},
                {source: "sw2", target: "pc3"},
                {source: "sw2", target: "pc4"}
            ]
        },
        scoring_metrics: {
            time_efficiency: 20,
            config_process: 15,
            design_layout: 30,
            completeness: 15,
            correctness: 20
        }
    },
    {
        id: 7,
        title: "Hybrid Network",
        description: "A hybrid network topology combines two or more different network topologies.",
        topology_type: "hybrid",
        difficulty: "hard",
        base_score: 250,
        time_bonus: 50,
        perfect_match_bonus: 25,
        is_active: true,
        initial_config: {
            devices: [],
            connections: []
        },
        expected_config: {
            devices: [
                {id: "r1", type: "router", name: "Core Router", x: 0.5, y: 0.2},
                {id: "sw1", type: "switch", name: "Switch 1", x: 0.3, y: 0.4},
                {id: "sw2", type: "switch", name: "Switch 2", x: 0.7, y: 0.4},
                {id: "pc1", type: "pc", name: "PC-1", x: 0.2, y: 0.6},
                {id: "pc2", type: "pc", name: "PC-2", x: 0.4, y: 0.6},
                {id: "pc3", type: "pc", name: "PC-3", x: 0.6, y: 0.6},
                {id: "pc4", type: "pc", name: "PC-4", x: 0.8, y: 0.6},
                {id: "sv1", type: "server", name: "Server", x: 0.5, y: 0.4}
            ],
            connections: [
                {source: "r1", target: "sw1"},
                {source: "r1", target: "sw2"},
                {source: "r1", target: "sv1"},
                {source: "sw1", target: "pc1"},
                {source: "sw1", target: "pc2"},
                {source: "sw2", target: "pc3"},
                {source: "sw2", target: "pc4"},
                {source: "sw1", target: "sw2"}
            ]
        },
        scoring_metrics: {
            time_efficiency: 10,
            config_process: 20,
            design_layout: 25,
            completeness: 20,
            correctness: 25
        }
    }
];

// Sample troubleshooting data
const sampleTroubleshooting = [
    {
        id: 1,
        title: "Network Connectivity Issue",
        description: "A company's workstations cannot connect to the internet. Diagnose and fix the issue.",
        difficulty: "medium",
        scenario: "Users in the marketing department report that they cannot access any websites or external resources. Other departments are working normally. The network administrator has checked that the router and firewall are operational.",
        solution: "The issue is with the DHCP server for the marketing VLAN. It's not assigning proper default gateway addresses. Reconfigure the DHCP scope to provide the correct default gateway (192.168.10.1) for the marketing department's VLAN.",
        hints: [
            "Check if the workstations have valid IP addresses",
            "Verify the default gateway configuration",
            "Look at the DHCP server settings for the marketing VLAN"
        ],
        is_active: true,
        created_at: "2023-04-15T14:30:00",
        updated_at: "2023-04-15T14:30:00"
    },
    {
        id: 2,
        title: "Server Authentication Problem",
        description: "Users are unable to authenticate to the company's internal server. Find and fix the authentication issue.",
        difficulty: "hard",
        scenario: "The company's internal authentication server is rejecting connections from legitimate users. The system was working yesterday, and no configuration changes have been reported. Users receive 'Authentication failed' errors when trying to log in to company resources.",
        solution: "The issue is with the expired SSL certificate on the authentication server. Renew the SSL certificate and restart the authentication service to restore proper functionality.",
        hints: [
            "Check the authentication server's logs",
            "Verify the server's certificate status",
            "Look for any recent changes in the authentication service"
        ],
        is_active: true,
        created_at: "2023-05-20T09:15:00",
        updated_at: "2023-05-20T09:15:00"
    },
    {
        id: 3,
        title: "DNS Resolution Failure",
        description: "Workstations cannot resolve domain names but can access IP addresses directly. Fix the DNS configuration issue.",
        difficulty: "easy",
        scenario: "Users report they cannot access websites by name, but they can ping IP addresses like 8.8.8.8 successfully. The issue started after a power outage earlier this morning.",
        solution: "The DNS server addresses were cleared from the network configuration during the power outage. Add the primary DNS server (192.168.1.10) and secondary DNS server (192.168.1.11) to the DHCP server configuration.",
        hints: [
            "Check if users can ping IP addresses",
            "Verify the DNS settings on client workstations",
            "Review the DHCP server configuration"
        ],
        is_active: true,
        created_at: "2023-06-05T10:45:00",
        updated_at: "2023-06-05T10:45:00"
    }
];
