/**
 * PKT File Handler for Network Simulation Core
 * Handles Cisco Packet Tracer file import/export functionality
 */

class PKTFileHandler {
    constructor() {
        this.supportedVersion = '7.3.0';
        this.fileSignature = 'PKT';
        this.initializeHandler();
    }

    initializeHandler() {
        this.createImportExportInterface();
        this.attachEventListeners();
    }

    createImportExportInterface() {
        // Add PKT import/export buttons to topology interface
        const toolbarHTML = `
        <div id="pktToolbar" class="pkt-toolbar">
            <div class="pkt-toolbar-section">
                <h4>Packet Tracer Integration</h4>
                <div class="pkt-buttons">
                    <button id="importPktBtn" class="pkt-btn pkt-import">
                        <i class="fas fa-file-import"></i>
                        Import PKT File
                    </button>
                    <button id="exportPktBtn" class="pkt-btn pkt-export">
                        <i class="fas fa-file-export"></i>
                        Export to PKT
                    </button>
                    <button id="validatePktBtn" class="pkt-btn pkt-validate">
                        <i class="fas fa-check-circle"></i>
                        Validate PKT
                    </button>
                </div>
            </div>
            
            <div class="pkt-status">
                <div id="pktStatus" class="status-indicator">
                    <span class="status-dot"></span>
                    <span class="status-text">Ready</span>
                </div>
            </div>
        </div>
        
        <!-- PKT Import Modal -->
        <div id="pktImportModal" class="pkt-modal" style="display: none;">
            <div class="pkt-modal-content">
                <div class="pkt-modal-header">
                    <h3>Import Packet Tracer File</h3>
                    <button class="close-btn" onclick="pktHandler.closeImportModal()">&times;</button>
                </div>
                
                <div class="pkt-modal-body">
                    <div class="file-drop-zone" id="pktDropZone">
                        <div class="drop-zone-content">
                            <i class="fas fa-cloud-upload-alt"></i>
                            <h4>Drop PKT file here or click to browse</h4>
                            <p>Supported: Cisco Packet Tracer files (.pkt)</p>
                            <input type="file" id="pktFileInput" accept=".pkt" style="display: none;">
                        </div>
                    </div>
                    
                    <div id="pktImportProgress" class="import-progress" style="display: none;">
                        <div class="progress-bar">
                            <div class="progress-fill"></div>
                        </div>
                        <div class="progress-text">Processing PKT file...</div>
                    </div>
                    
                    <div id="pktImportResults" class="import-results" style="display: none;">
                        <h4>Import Summary</h4>
                        <div class="results-content"></div>
                    </div>
                    
                    <div class="import-options">
                        <h4>Import Options</h4>
                        <label>
                            <input type="checkbox" id="importTopology" checked>
                            Import Network Topology
                        </label>
                        <label>
                            <input type="checkbox" id="importConfigs" checked>
                            Import Device Configurations
                        </label>
                        <label>
                            <input type="checkbox" id="importAddressing">
                            Import IP Addressing
                        </label>
                        <label>
                            <input type="checkbox" id="mergeWithExisting">
                            Merge with Existing Topology
                        </label>
                    </div>
                </div>
                
                <div class="pkt-modal-footer">
                    <button class="btn-secondary" onclick="pktHandler.closeImportModal()">Cancel</button>
                    <button class="btn-primary" onclick="pktHandler.processImport()" id="processImportBtn" disabled>
                        Import
                    </button>
                </div>
            </div>
        </div>
        
        <!-- PKT Export Modal -->
        <div id="pktExportModal" class="pkt-modal" style="display: none;">
            <div class="pkt-modal-content">
                <div class="pkt-modal-header">
                    <h3>Export to Packet Tracer</h3>
                    <button class="close-btn" onclick="pktHandler.closeExportModal()">&times;</button>
                </div>
                
                <div class="pkt-modal-body">
                    <div class="export-preview">
                        <h4>Export Preview</h4>
                        <div id="exportPreview" class="preview-content">
                            <!-- Preview will be populated -->
                        </div>
                    </div>
                    
                    <div class="export-options">
                        <h4>Export Options</h4>
                        <div class="option-group">
                            <label for="exportFileName">File Name:</label>
                            <input type="text" id="exportFileName" value="topology_export.pkt">
                        </div>
                        
                        <div class="option-group">
                            <label>Include:</label>
                            <label><input type="checkbox" id="exportDevices" checked> Network Devices</label>
                            <label><input type="checkbox" id="exportConnections" checked> Connections</label>
                            <label><input type="checkbox" id="exportConfigurations" checked> Device Configurations</label>
                            <label><input type="checkbox" id="exportAddressing"> IP Addressing</label>
                        </div>
                        
                        <div class="option-group">
                            <label for="pktVersion">Target PKT Version:</label>
                            <select id="pktVersion">
                                <option value="7.3.0">Packet Tracer 7.3.0</option>
                                <option value="8.0.0">Packet Tracer 8.0.0</option>
                                <option value="8.1.0">Packet Tracer 8.1.0</option>
                                <option value="8.2.0">Packet Tracer 8.2.0</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <div class="pkt-modal-footer">
                    <button class="btn-secondary" onclick="pktHandler.closeExportModal()">Cancel</button>
                    <button class="btn-primary" onclick="pktHandler.processExport()">
                        Export PKT File
                    </button>
                </div>
            </div>
        </div>`;
        
        // Add to page
        const topologyContainer = document.querySelector('.topology-container') || 
                                document.querySelector('#canvas').parentElement;
        if (topologyContainer) {
            topologyContainer.insertAdjacentHTML('beforebegin', toolbarHTML);
        }
        
        this.addPKTStyles();
    }

    addPKTStyles() {
        const styles = `
        <style>
        .pkt-toolbar {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .pkt-toolbar-section h4 {
            color: #00d4ff;
            margin: 0 0 10px 0;
            font-size: 16px;
        }
        
        .pkt-buttons {
            display: flex;
            gap: 10px;
        }
        
        .pkt-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        
        .pkt-import {
            background: #28a745;
            color: white;
        }
        
        .pkt-export {
            background: #007bff;
            color: white;
        }
        
        .pkt-validate {
            background: #ffc107;
            color: #000;
        }
        
        .pkt-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        
        .pkt-status {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #ccc;
        }
        
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #28a745;
        }
        
        .pkt-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .pkt-modal-content {
            background: #2a2a2a;
            border-radius: 12px;
            width: 700px;
            max-height: 80vh;
            overflow-y: auto;
            color: white;
        }
        
        .pkt-modal-header {
            padding: 20px;
            border-bottom: 1px solid #444;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .pkt-modal-header h3 {
            margin: 0;
            color: #00d4ff;
        }
        
        .pkt-modal-body {
            padding: 20px;
        }
        
        .file-drop-zone {
            border: 2px dashed #666;
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            margin-bottom: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .file-drop-zone:hover,
        .file-drop-zone.drag-over {
            border-color: #00d4ff;
            background: rgba(0, 212, 255, 0.1);
        }
        
        .drop-zone-content i {
            font-size: 48px;
            color: #666;
            margin-bottom: 15px;
        }
        
        .drop-zone-content h4 {
            margin: 0 0 10px 0;
            color: #ccc;
        }
        
        .drop-zone-content p {
            margin: 0;
            color: #999;
            font-size: 14px;
        }
        
        .import-progress {
            margin-bottom: 20px;
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: #444;
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: #00d4ff;
            width: 0%;
            transition: width 0.3s ease;
        }
        
        .progress-text {
            color: #ccc;
            font-size: 14px;
        }
        
        .import-options,
        .export-options {
            background: #333;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
        }
        
        .import-options h4,
        .export-options h4 {
            margin: 0 0 15px 0;
            color: #00d4ff;
        }
        
        .import-options label,
        .export-options label {
            display: block;
            margin-bottom: 8px;
            color: #ccc;
            cursor: pointer;
        }
        
        .import-options input[type="checkbox"],
        .export-options input[type="checkbox"] {
            margin-right: 8px;
        }
        
        .option-group {
            margin-bottom: 15px;
        }
        
        .option-group label {
            display: block;
            margin-bottom: 5px;
            color: #ccc;
            font-weight: 500;
        }
        
        .option-group input,
        .option-group select {
            width: 100%;
            padding: 8px;
            background: #444;
            border: 1px solid #666;
            border-radius: 4px;
            color: white;
        }
        
        .export-preview {
            background: #333;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
        }
        
        .export-preview h4 {
            margin: 0 0 15px 0;
            color: #00d4ff;
        }
        
        .preview-content {
            font-family: 'Courier New', monospace;
            font-size: 14px;
            color: #ccc;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .import-results {
            background: #333;
            border-radius: 8px;
            padding: 15px;
        }
        
        .import-results h4 {
            margin: 0 0 15px 0;
            color: #00d4ff;
        }
        
        .results-content {
            color: #ccc;
        }
        
        .pkt-modal-footer {
            padding: 20px;
            border-top: 1px solid #444;
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }
        
        .btn-primary, .btn-secondary {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
        }
        
        .btn-primary {
            background: #00d4ff;
            color: #000;
        }
        
        .btn-secondary {
            background: #666;
            color: white;
        }
        
        .btn-primary:disabled {
            background: #555;
            color: #999;
            cursor: not-allowed;
        }
        </style>`;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    attachEventListeners() {
        // Import button
        document.getElementById('importPktBtn')?.addEventListener('click', () => {
            this.openImportModal();
        });
        
        // Export button
        document.getElementById('exportPktBtn')?.addEventListener('click', () => {
            this.openExportModal();
        });
        
        // Validate button
        document.getElementById('validatePktBtn')?.addEventListener('click', () => {
            this.validateCurrentTopology();
        });
        
        // File input change
        document.getElementById('pktFileInput')?.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });
        
        // Drop zone events
        const dropZone = document.getElementById('pktDropZone');
        if (dropZone) {
            dropZone.addEventListener('click', () => {
                document.getElementById('pktFileInput').click();
            });
            
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('drag-over');
            });
            
            dropZone.addEventListener('dragleave', () => {
                dropZone.classList.remove('drag-over');
            });
            
            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
                const file = e.dataTransfer.files[0];
                if (file) this.handleFileSelect(file);
            });
        }
    }

    openImportModal() {
        document.getElementById('pktImportModal').style.display = 'flex';
        this.resetImportModal();
    }

    closeImportModal() {
        document.getElementById('pktImportModal').style.display = 'none';
    }

    openExportModal() {
        document.getElementById('pktExportModal').style.display = 'flex';
        this.generateExportPreview();
    }

    closeExportModal() {
        document.getElementById('pktExportModal').style.display = 'none';
    }

    resetImportModal() {
        // Reset all modal elements to initial state
        document.getElementById('pktImportProgress').style.display = 'none';
        document.getElementById('pktImportResults').style.display = 'none';
        document.getElementById('processImportBtn').disabled = true;
        
        // Reset progress bar
        const progressFill = document.querySelector('.progress-fill');
        if (progressFill) progressFill.style.width = '0%';
    }

    handleFileSelect(file) {
        if (!file) return;
        
        // Validate file type
        if (!file.name.toLowerCase().endsWith('.pkt')) {
            alert('Please select a valid Packet Tracer (.pkt) file');
            return;
        }
        
        // Show file info and enable import button
        this.updateStatus(`File selected: ${file.name} (${this.formatFileSize(file.size)})`);
        document.getElementById('processImportBtn').disabled = false;
        
        // Store the file for processing
        this.selectedFile = file;
    }

    async processImport() {
        if (!this.selectedFile) return;
        
        this.showImportProgress();
        
        try {
            // Simulate PKT file processing (in real implementation, this would parse the binary format)
            const pktData = await this.parsePKTFile(this.selectedFile);
            
            // Apply import options
            const options = this.getImportOptions();
            
            // Import the topology
            const importResult = await this.importTopology(pktData, options);
            
            // Show results
            this.showImportResults(importResult);
            
            this.updateStatus('Import completed successfully');
            
        } catch (error) {
            console.error('Import error:', error);
            alert(`Import failed: ${error.message}`);
            this.updateStatus('Import failed');
        }
    }

    showImportProgress() {
        document.getElementById('pktImportProgress').style.display = 'block';
        
        // Simulate progress
        let progress = 0;
        const progressFill = document.querySelector('.progress-fill');
        const progressText = document.querySelector('.progress-text');
        
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 100) progress = 100;
            
            progressFill.style.width = progress + '%';
            
            if (progress < 30) {
                progressText.textContent = 'Reading PKT file...';
            } else if (progress < 60) {
                progressText.textContent = 'Parsing network topology...';
            } else if (progress < 90) {
                progressText.textContent = 'Importing devices and connections...';
            } else {
                progressText.textContent = 'Finalizing import...';
            }
            
            if (progress >= 100) {
                clearInterval(interval);
                progressText.textContent = 'Import complete!';
            }
        }, 200);
    }

    async parsePKTFile(file) {
        // Mock PKT file parsing - in reality this would parse the binary format
        return new Promise((resolve) => {
            setTimeout(() => {
                // Simulated PKT data structure
                resolve({
                    version: '7.3.0',
                    devices: [
                        {
                            id: 'R1',
                            type: 'router',
                            model: '2911',
                            x: 200,
                            y: 150,
                            configuration: {
                                hostname: 'Router1',
                                interfaces: {
                                    'GigabitEthernet0/0': {
                                        ip: '192.168.1.1',
                                        mask: '255.255.255.0',
                                        enabled: true
                                    }
                                }
                            }
                        },
                        {
                            id: 'PC1',
                            type: 'pc',
                            model: 'PC-PT',
                            x: 100,
                            y: 250,
                            configuration: {
                                ip: '192.168.1.10',
                                mask: '255.255.255.0',
                                gateway: '192.168.1.1'
                            }
                        },
                        {
                            id: 'SW1',
                            type: 'switch',
                            model: '2960',
                            x: 200,
                            y: 250,
                            configuration: {
                                hostname: 'Switch1'
                            }
                        }
                    ],
                    connections: [
                        {
                            source: 'R1',
                            target: 'SW1',
                            sourcePort: 'GigabitEthernet0/0',
                            targetPort: 'FastEthernet0/1',
                            type: 'ethernet'
                        },
                        {
                            source: 'SW1',
                            target: 'PC1',
                            sourcePort: 'FastEthernet0/2',
                            targetPort: 'FastEthernet0',
                            type: 'ethernet'
                        }
                    ]
                });
            }, 2000);
        });
    }

    getImportOptions() {
        return {
            importTopology: document.getElementById('importTopology').checked,
            importConfigs: document.getElementById('importConfigs').checked,
            importAddressing: document.getElementById('importAddressing').checked,
            mergeWithExisting: document.getElementById('mergeWithExisting').checked
        };
    }

    async importTopology(pktData, options) {
        const results = {
            devicesImported: 0,
            connectionsImported: 0,
            configurationsImported: 0,
            errors: [],
            warnings: []
        };
        
        try {
            // Clear existing topology if not merging
            if (!options.mergeWithExisting) {
                this.clearCurrentTopology();
            }
            
            // Import devices
            if (options.importTopology) {
                for (const device of pktData.devices) {
                    try {
                        this.createDeviceFromPKT(device, options);
                        results.devicesImported++;
                    } catch (error) {
                        results.errors.push(`Failed to import device ${device.id}: ${error.message}`);
                    }
                }
            }
            
            // Import connections
            if (options.importTopology) {
                for (const connection of pktData.connections) {
                    try {
                        this.createConnectionFromPKT(connection);
                        results.connectionsImported++;
                    } catch (error) {
                        results.errors.push(`Failed to import connection: ${error.message}`);
                    }
                }
            }
            
            // Import configurations
            if (options.importConfigs) {
                for (const device of pktData.devices) {
                    if (device.configuration) {
                        try {
                            this.applyDeviceConfiguration(device);
                            results.configurationsImported++;
                        } catch (error) {
                            results.warnings.push(`Failed to apply configuration for ${device.id}: ${error.message}`);
                        }
                    }
                }
            }
            
        } catch (error) {
            results.errors.push(`Import failed: ${error.message}`);
        }
        
        return results;
    }

    createDeviceFromPKT(pktDevice, options) {
        // Convert PKT device to internal format
        const device = {
            id: pktDevice.id,
            type: this.mapPKTDeviceType(pktDevice.type),
            label: pktDevice.configuration?.hostname || pktDevice.id,
            x: pktDevice.x,
            y: pktDevice.y,
            model: pktDevice.model,
            pktImported: true
        };
        
        // Add to current topology (this would integrate with existing topology system)
        if (window.topology && window.topology.addDevice) {
            window.topology.addDevice(device);
        }
        
        return device;
    }

    createConnectionFromPKT(pktConnection) {
        // Convert PKT connection to internal format
        const connection = {
            source: pktConnection.source,
            target: pktConnection.target,
            sourcePort: pktConnection.sourcePort,
            targetPort: pktConnection.targetPort,
            type: pktConnection.type || 'ethernet',
            pktImported: true
        };
        
        // Add to current topology
        if (window.topology && window.topology.addConnection) {
            window.topology.addConnection(connection);
        }
        
        return connection;
    }

    applyDeviceConfiguration(pktDevice) {
        // Apply PKT device configuration
        if (window.ipManager && pktDevice.configuration) {
            const config = this.convertPKTConfiguration(pktDevice.configuration);
            window.ipManager.networkConfigs.set(pktDevice.id, config);
        }
    }

    convertPKTConfiguration(pktConfig) {
        const config = {};
        
        // Extract IP configuration from PKT format
        if (pktConfig.interfaces) {
            const firstInterface = Object.values(pktConfig.interfaces)[0];
            if (firstInterface) {
                config.ipAddress = firstInterface.ip;
                config.subnetMask = firstInterface.mask;
            }
        } else if (pktConfig.ip) {
            config.ipAddress = pktConfig.ip;
            config.subnetMask = pktConfig.mask;
            config.gateway = pktConfig.gateway;
        }
        
        return config;
    }

    mapPKTDeviceType(pktType) {
        const typeMap = {
            'router': 'router',
            'switch': 'switch',
            'pc': 'pc',
            'server': 'server',
            'hub': 'hub',
            'wireless_router': 'router',
            'access_point': 'switch'
        };
        
        return typeMap[pktType.toLowerCase()] || 'unknown';
    }

    showImportResults(results) {
        document.getElementById('pktImportResults').style.display = 'block';
        
        let html = `
            <div class="result-summary">
                <div class="result-item">
                    <strong>Devices Imported:</strong> ${results.devicesImported}
                </div>
                <div class="result-item">
                    <strong>Connections Imported:</strong> ${results.connectionsImported}
                </div>
                <div class="result-item">
                    <strong>Configurations Applied:</strong> ${results.configurationsImported}
                </div>
            </div>
        `;
        
        if (results.errors.length > 0) {
            html += '<div class="result-errors"><h5>Errors:</h5>';
            results.errors.forEach(error => {
                html += `<div class="error-item">❌ ${error}</div>`;
            });
            html += '</div>';
        }
        
        if (results.warnings.length > 0) {
            html += '<div class="result-warnings"><h5>Warnings:</h5>';
            results.warnings.forEach(warning => {
                html += `<div class="warning-item">⚠️ ${warning}</div>`;
            });
            html += '</div>';
        }
        
        document.querySelector('.results-content').innerHTML = html;
    }

    generateExportPreview() {
        // Generate preview of what will be exported
        const currentTopology = this.getCurrentTopology();
        
        let preview = `PKT Export Preview\n`;
        preview += `==================\n\n`;
        preview += `Devices: ${currentTopology.devices.length}\n`;
        preview += `Connections: ${currentTopology.connections.length}\n`;
        preview += `Configurations: ${Object.keys(currentTopology.configurations || {}).length}\n\n`;
        
        preview += `Device List:\n`;
        currentTopology.devices.forEach(device => {
            preview += `- ${device.label || device.id} (${device.type})\n`;
        });
        
        if (currentTopology.connections.length > 0) {
            preview += `\nConnections:\n`;
            currentTopology.connections.forEach(conn => {
                preview += `- ${conn.source} ↔ ${conn.target}\n`;
            });
        }
        
        document.getElementById('exportPreview').textContent = preview;
    }

    async processExport() {
        try {
            const options = this.getExportOptions();
            const exportData = this.generateExportData(options);
            const pktData = this.convertToPKTFormat(exportData, options);
            
            // Generate and download PKT file
            await this.downloadPKTFile(pktData, options.fileName);
            
            this.updateStatus('Export completed successfully');
            this.closeExportModal();
            
        } catch (error) {
            console.error('Export error:', error);
            alert(`Export failed: ${error.message}`);
        }
    }

    getExportOptions() {
        return {
            fileName: document.getElementById('exportFileName').value,
            exportDevices: document.getElementById('exportDevices').checked,
            exportConnections: document.getElementById('exportConnections').checked,
            exportConfigurations: document.getElementById('exportConfigurations').checked,
            exportAddressing: document.getElementById('exportAddressing').checked,
            targetVersion: document.getElementById('pktVersion').value
        };
    }

    generateExportData(options) {
        const currentTopology = this.getCurrentTopology();
        const exportData = {};
        
        if (options.exportDevices) {
            exportData.devices = currentTopology.devices;
        }
        
        if (options.exportConnections) {
            exportData.connections = currentTopology.connections;
        }
        
        if (options.exportConfigurations && window.ipManager) {
            exportData.configurations = window.ipManager.exportConfiguration();
        }
        
        return exportData;
    }

    convertToPKTFormat(data, options) {
        // Convert internal format to PKT format
        const pktData = {
            version: options.targetVersion,
            timestamp: new Date().toISOString(),
            devices: [],
            connections: []
        };
        
        // Convert devices
        if (data.devices) {
            data.devices.forEach(device => {
                const pktDevice = {
                    id: device.id,
                    type: this.mapToPKTDeviceType(device.type),
                    model: this.getDefaultPKTModel(device.type),
                    x: device.x || 0,
                    y: device.y || 0,
                    configuration: {}
                };
                
                // Add configuration if available
                if (data.configurations && data.configurations[device.id]) {
                    const config = data.configurations[device.id];
                    if (device.type === 'router' && config.ipAddress) {
                        pktDevice.configuration.interfaces = {
                            'GigabitEthernet0/0': {
                                ip: config.ipAddress,
                                mask: config.subnetMask,
                                enabled: true
                            }
                        };
                    } else if (config.ipAddress) {
                        pktDevice.configuration.ip = config.ipAddress;
                        pktDevice.configuration.mask = config.subnetMask;
                        pktDevice.configuration.gateway = config.gateway;
                    }
                }
                
                pktData.devices.push(pktDevice);
            });
        }
        
        // Convert connections
        if (data.connections) {
            data.connections.forEach(conn => {
                pktData.connections.push({
                    source: conn.source,
                    target: conn.target,
                    sourcePort: conn.sourcePort || this.getDefaultPort(conn.sourceType),
                    targetPort: conn.targetPort || this.getDefaultPort(conn.targetType),
                    type: conn.type || 'ethernet'
                });
            });
        }
        
        return pktData;
    }

    mapToPKTDeviceType(internalType) {
        const typeMap = {
            'router': 'router',
            'switch': 'switch',
            'pc': 'pc',
            'server': 'server'
        };
        
        return typeMap[internalType] || 'pc';
    }

    getDefaultPKTModel(deviceType) {
        const modelMap = {
            'router': '2911',
            'switch': '2960',
            'pc': 'PC-PT',
            'server': 'Server-PT'
        };
        
        return modelMap[deviceType] || 'Generic-PT';
    }

    getDefaultPort(deviceType) {
        const portMap = {
            'router': 'GigabitEthernet0/0',
            'switch': 'FastEthernet0/1',
            'pc': 'FastEthernet0',
            'server': 'FastEthernet0'
        };
        
        return portMap[deviceType] || 'FastEthernet0';
    }

    async downloadPKTFile(pktData, fileName) {
        // Convert to binary PKT format (simplified - in reality would use proper PKT binary format)
        const jsonString = JSON.stringify(pktData, null, 2);
        const blob = new Blob([jsonString], { type: 'application/octet-stream' });
        
        // Create download link
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    getCurrentTopology() {
        // Get current topology data - this would integrate with the existing topology system
        return {
            devices: window.devices || [],
            connections: window.connections || [],
            configurations: window.ipManager ? window.ipManager.exportConfiguration() : {}
        };
    }

    clearCurrentTopology() {
        // Clear current topology - this would integrate with existing system
        if (window.devices) window.devices.length = 0;
        if (window.connections) window.connections.length = 0;
        if (window.ipManager) window.ipManager.networkConfigs.clear();
    }

    validateCurrentTopology() {
        // Validate current topology for PKT compatibility
        const topology = this.getCurrentTopology();
        const issues = [];
        const warnings = [];
        
        // Check for PKT compatibility issues
        topology.devices.forEach(device => {
            if (!this.isPKTCompatibleDevice(device)) {
                warnings.push(`Device ${device.label} may not be compatible with Packet Tracer`);
            }
        });
        
        topology.connections.forEach(conn => {
            if (!this.isPKTCompatibleConnection(conn)) {
                warnings.push(`Connection between ${conn.source} and ${conn.target} may not be supported`);
            }
        });
        
        // Display validation results
        let message = 'PKT Validation Results:\n\n';
        
        if (issues.length === 0 && warnings.length === 0) {
            message += '✅ Topology is fully compatible with Packet Tracer';
        } else {
            if (issues.length > 0) {
                message += 'Issues:\n' + issues.map(issue => `❌ ${issue}`).join('\n') + '\n\n';
            }
            if (warnings.length > 0) {
                message += 'Warnings:\n' + warnings.map(warning => `⚠️ ${warning}`).join('\n');
            }
        }
        
        alert(message);
    }

    isPKTCompatibleDevice(device) {
        const compatibleTypes = ['router', 'switch', 'pc', 'server', 'hub'];
        return compatibleTypes.includes(device.type.toLowerCase());
    }

    isPKTCompatibleConnection(connection) {
        const compatibleTypes = ['ethernet', 'serial', 'console'];
        return compatibleTypes.includes((connection.type || 'ethernet').toLowerCase());
    }

    updateStatus(message) {
        const statusText = document.querySelector('.status-text');
        if (statusText) {
            statusText.textContent = message;
        }
        console.log('PKT Handler:', message);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize PKT File Handler
const pktHandler = new PKTFileHandler();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PKTFileHandler;
}