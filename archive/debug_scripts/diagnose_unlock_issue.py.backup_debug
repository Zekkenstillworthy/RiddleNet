"""
Diagnostic script to check Foundation Learning Path completion and unlock status
"""

print("=" * 70)
print("🔍 FOUNDATION UNLOCK DIAGNOSTICS")
print("=" * 70)

print("\n📋 Instructions:")
print("1. Open Chrome DevTools (F12)")
print("2. Go to Console tab")
print("3. Copy and paste the following JavaScript:")
print("\n" + "-" * 70)

js_code = """
console.log('\\n🔍 ===== FOUNDATION UNLOCK DIAGNOSTIC =====\\n');

// Read foundation progress
const fp = JSON.parse(localStorage.getItem('foundation_progress') || '{}');
console.log('📊 Foundation Progress Data:', fp);

// Phase completion status
console.log('\\n✅ Phase Completion:');
console.log('Phase 1:', fp.phase1Complete ? '✅ COMPLETE' : '❌ INCOMPLETE');
console.log('Phase 2:', fp.phase2Complete ? '✅ COMPLETE' : '❌ INCOMPLETE');
console.log('Phase 3:', fp.phase3Complete ? '✅ COMPLETE' : '❌ INCOMPLETE');
console.log('Phase 4:', fp.phase4Complete ? '✅ COMPLETE' : '❌ INCOMPLETE');
console.log('Phase 5:', fp.phase5Complete ? '✅ COMPLETE' : '❌ INCOMPLETE');

// Module count
const completedModules = fp.completedModules || [];
console.log('\\n📈 Module Count:', completedModules.length, '/ 16');
console.log('Completed Modules:', completedModules);

// Check if all phases complete
const allPhasesComplete = fp.phase1Complete && fp.phase2Complete && 
                         fp.phase3Complete && fp.phase4Complete && 
                         fp.phase5Complete;
console.log('\\n🎯 All Phases Complete?', allPhasesComplete ? '✅ YES' : '❌ NO');

// Emergency unlock check
const emergencyUnlock = completedModules.length >= 16;
console.log('🚨 Emergency Unlock Eligible?', emergencyUnlock ? '✅ YES (16+ modules)' : '❌ NO');

// Check difficulty unlocks
const difficultyUnlocks = JSON.parse(localStorage.getItem('difficulty_unlocks') || '{}');
console.log('\\n🔓 Difficulty Unlocks:', difficultyUnlocks);
console.log('Easy Unlocked?', difficultyUnlocks.easy ? '✅ YES' : '❌ NO');
console.log('Novice Unlocked?', difficultyUnlocks.novice ? '✅ YES' : '❌ NO');

// Check challenge results
const challengeResults = JSON.parse(localStorage.getItem('challenge_results') || '{}');
console.log('\\n🏆 Challenge Results:', challengeResults);
console.log('Foundation Status:', challengeResults.foundation?.status || 'Not set');

// Diagnosis
console.log('\\n🩺 DIAGNOSIS:');
if (allPhasesComplete || emergencyUnlock) {
    console.log('✅ Should be unlocked!');
    if (!difficultyUnlocks.easy && !difficultyUnlocks.novice) {
        console.log('🔧 FIX NEEDED: Run syncChallengeProgressStatus()');
    }
} else {
    console.log('❌ Not ready to unlock yet');
    console.log('Missing:', 
        !fp.phase1Complete ? 'Phase 1, ' : '',
        !fp.phase2Complete ? 'Phase 2, ' : '',
        !fp.phase3Complete ? 'Phase 3, ' : '',
        !fp.phase4Complete ? 'Phase 4, ' : '',
        !fp.phase5Complete ? 'Phase 5, ' : ''
    );
    const needed = 16 - completedModules.length;
    if (needed > 0) {
        console.log('Need', needed, 'more modules');
    }
}

console.log('\\n🔄 To manually trigger unlock, run:');
console.log('syncChallengeProgressStatus();');
console.log('\\n===============================================\\n');
"""

print(js_code)
print("-" * 70)

print("\n🔧 MANUAL FIX (if needed):")
print("If the diagnostic shows you should be unlocked but aren't, paste this:\n")

fix_code = """
// Manual unlock fix
const fp = JSON.parse(localStorage.getItem('foundation_progress') || '{}');
const completed = fp.completedModules?.length || 0;

if (completed >= 16) {
    console.log('🔧 Applying manual unlock fix...');
    
    // Set all phase flags to true
    fp.phase1Complete = true;
    fp.phase2Complete = true;
    fp.phase3Complete = true;
    fp.phase4Complete = true;
    fp.phase5Complete = true;
    localStorage.setItem('foundation_progress', JSON.stringify(fp));
    
    // Unlock difficulty
    let unlocks = JSON.parse(localStorage.getItem('difficulty_unlocks') || '{}');
    unlocks.easy = true;
    unlocks.novice = true;
    localStorage.setItem('difficulty_unlocks', JSON.stringify(unlocks));
    
    // Update challenge results
    let cr = JSON.parse(localStorage.getItem('challenge_results') || '{}');
    cr.foundation = {
        status: 'completed',
        completedAt: new Date().toISOString(),
        totalModules: 16,
        completedModules: completed
    };
    localStorage.setItem('challenge_results', JSON.stringify(cr));
    
    console.log('✅ Manual unlock complete! Refreshing page...');
    location.reload();
} else {
    console.log('❌ Cannot unlock - only', completed, '/ 16 modules completed');
}
"""

print(fix_code)
print("-" * 70)

print("\n📝 Summary:")
print("1. Run the DIAGNOSTIC code in browser console")
print("2. Check if you have 16+ modules completed")
print("3. If yes and still locked, run the MANUAL FIX code")
print("4. Page will refresh and Novice should be unlocked")
print("\n" + "=" * 70)
