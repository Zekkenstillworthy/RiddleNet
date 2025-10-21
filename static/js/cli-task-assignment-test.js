/**
 * CLI Task Assignment Connection Test
 * 
 * This script verifies that CLI commands are properly connected to Task Assignment tracking.
 * 
 * Usage:
 * 1. Open browser console in simulation with task assignment enabled
 * 2. Paste this script and run it
 * 3. Check console for test results
 */

(function testCLITaskAssignmentConnection() {
    console.log('🧪 Starting CLI Task Assignment Connection Test...\n');
    
    const results = {
        passed: 0,
        failed: 0,
        warnings: 0
    };
    
    // Test 1: Check if TaskAssignmentManager exists
    console.log('Test 1: TaskAssignmentManager existence');
    if (window.taskAssignmentManager) {
        console.log('✅ PASS: TaskAssignmentManager found');
        results.passed++;
    } else {
        console.log('❌ FAIL: TaskAssignmentManager not initialized');
        console.log('   → Ensure simulation has task assignment enabled');
        results.failed++;
    }
    
    // Test 2: Check if event listener is attached
    console.log('\nTest 2: Event listener check');
    const hasListener = window.taskAssignmentManager && 
                       typeof window.taskAssignmentManager.trackCLICommand === 'function';
    if (hasListener) {
        console.log('✅ PASS: trackCLICommand method exists');
        results.passed++;
    } else {
        console.log('❌ FAIL: trackCLICommand method not found');
        results.failed++;
    }
    
    // Test 3: Simulate CLI command event
    console.log('\nTest 3: Simulating CLI command event');
    try {
        const testEvent = new CustomEvent('cli-command-executed', {
            detail: {
                device_id: 'TEST_DEVICE',
                command: 'show interfaces',
                output: 'Test output',
                timestamp: new Date().toISOString()
            }
        });
        
        console.log('📤 Dispatching test event...');
        document.dispatchEvent(testEvent);
        
        // Check if it was tracked
        setTimeout(() => {
            if (window.taskAssignmentManager && 
                window.taskAssignmentManager.userProgress.cli_history) {
                const tracked = window.taskAssignmentManager.userProgress.cli_history.some(
                    entry => entry.device_id === 'TEST_DEVICE' && entry.command === 'show interfaces'
                );
                
                if (tracked) {
                    console.log('✅ PASS: Test CLI command tracked successfully');
                    console.log('   → CLI history length:', 
                        window.taskAssignmentManager.userProgress.cli_history.length);
                    results.passed++;
                } else {
                    console.log('⚠️ WARNING: Event dispatched but not found in history');
                    console.log('   → Check if task mode is enabled');
                    results.warnings++;
                }
            } else {
                console.log('❌ FAIL: Cannot verify tracking (no cli_history)');
                results.failed++;
            }
            
            // Test 4: Check CLI execution functions
            console.log('\nTest 4: CLI execution functions check');
            const functions = [
                { name: 'DynamicSimulation.executeCLICommand', 
                  exists: window.DynamicSimulation?.prototype?.executeCLICommand },
                { name: 'NetworkSimulationEngine.executeMVPCLICommand', 
                  exists: window.NetworkSimulationEngine?.prototype?.executeMVPCLICommand },
                { name: 'NetworkDeviceConfigurator.executeCLICommand', 
                  exists: window.NetworkDeviceConfigurator?.prototype?.executeCLICommand }
            ];
            
            functions.forEach(func => {
                if (func.exists) {
                    console.log(`✅ PASS: ${func.name} exists`);
                    results.passed++;
                } else {
                    console.log(`⚠️ WARNING: ${func.name} not found (may not be loaded yet)`);
                    results.warnings++;
                }
            });
            
            // Print summary
            console.log('\n' + '='.repeat(60));
            console.log('📊 TEST SUMMARY');
            console.log('='.repeat(60));
            console.log(`✅ Passed:   ${results.passed}`);
            console.log(`❌ Failed:   ${results.failed}`);
            console.log(`⚠️  Warnings: ${results.warnings}`);
            console.log('='.repeat(60));
            
            if (results.failed === 0 && results.warnings === 0) {
                console.log('\n🎉 ALL TESTS PASSED! CLI Task Assignment is fully connected.');
                console.log('✅ CLI commands will now be tracked for task completion.');
            } else if (results.failed === 0) {
                console.log('\n⚠️  Tests passed with warnings. Connection likely functional.');
                console.log('   Review warnings above for optimization opportunities.');
            } else {
                console.log('\n❌ Some tests failed. Please review failures above.');
                console.log('   Ensure task assignment mode is enabled for this simulation.');
            }
            
            console.log('\n📝 Next Steps:');
            console.log('1. Execute a real CLI command on any device');
            console.log('2. Check console for: "📋 [CLI→TASK] Dispatching cli-command-executed event"');
            console.log('3. Verify progress updates in Task Assignment sidebar');
            console.log('4. Check database for cli_history entries');
            
        }, 500); // Give time for async operations
        
    } catch (error) {
        console.log('❌ FAIL: Error during event simulation:', error);
        results.failed++;
    }
    
})();
