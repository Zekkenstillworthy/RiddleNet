// Test Client-Side RNet Encryption Functions
// Copy and paste this into browser console to test

console.log('🧪 Testing RNet Encryption Functions...\n');

// Test 1: Basic encryption
console.log('Test 1: Basic Encryption');
const testData = {
    format: 'rnetfile',
    version: '1.0',
    simulation: {
        id: 1,
        title: 'Test Simulation',
        description: 'This is a test'
    },
    devices: ['router1', 'switch1'],
    connections: []
};

try {
    const encrypted = encryptRnetData(testData);
    console.log('✅ Encryption successful');
    console.log('  - Format:', encrypted.format);
    console.log('  - Version:', encrypted.version);
    console.log('  - Has encrypted_data:', Boolean(encrypted.encrypted_data));
    console.log('  - Encrypted data length:', encrypted.encrypted_data.length);
} catch (error) {
    console.error('❌ Encryption failed:', error);
}

console.log('\n---\n');

// Test 2: Encryption then decryption
console.log('Test 2: Round-trip (Encrypt → Decrypt)');
try {
    const encrypted = encryptRnetData(testData);
    const decrypted = decryptRnetData(encrypted);
    
    const match = JSON.stringify(testData) === JSON.stringify(decrypted);
    
    if (match) {
        console.log('✅ Round-trip successful - data matches original');
    } else {
        console.error('❌ Round-trip failed - data mismatch');
        console.log('Original:', testData);
        console.log('Decrypted:', decrypted);
    }
} catch (error) {
    console.error('❌ Round-trip test failed:', error);
}

console.log('\n---\n');

// Test 3: Detection of encrypted files
console.log('Test 3: Encrypted File Detection');
const encrypted = encryptRnetData(testData);
const unencrypted = testData;

console.log('  - Encrypted file detected:', isEncryptedRnet(encrypted) ? '✅ Yes' : '❌ No');
console.log('  - Unencrypted file detected:', !isEncryptedRnet(unencrypted) ? '✅ Correctly not detected' : '❌ False positive');

console.log('\n---\n');

// Test 4: Tampering detection
console.log('Test 4: Tampering Detection');
try {
    const encrypted = encryptRnetData(testData);
    
    // Tamper with the encrypted data
    const tamperedData = { ...encrypted };
    tamperedData.encrypted_data = tamperedData.encrypted_data.replace('A', 'B');
    
    try {
        const decrypted = decryptRnetData(tamperedData);
        console.log('⚠️ Tampering not detected - this is expected for Base64 obfuscation');
        console.log('   (For true tamper detection, use server-side AES-256 with HMAC)');
    } catch (error) {
        console.log('✅ Tampering detected:', error.message);
    }
} catch (error) {
    console.error('❌ Tampering test failed:', error);
}

console.log('\n---\n');

// Test 5: Large data handling
console.log('Test 5: Large Data Handling');
const largeData = {
    ...testData,
    devices: Array(100).fill(null).map((_, i) => ({
        id: `device_${i}`,
        type: 'router',
        label: `RTR-${i}`,
        x: Math.random() * 800,
        y: Math.random() * 600
    })),
    connections: Array(50).fill(null).map((_, i) => ({
        id: `conn_${i}`,
        from: `device_${i}`,
        to: `device_${i + 1}`
    }))
};

try {
    const startTime = performance.now();
    const encrypted = encryptRnetData(largeData);
    const encryptTime = performance.now() - startTime;
    
    const decryptStart = performance.now();
    const decrypted = decryptRnetData(encrypted);
    const decryptTime = performance.now() - decryptStart;
    
    console.log('✅ Large data handled successfully');
    console.log(`  - Original size: ${JSON.stringify(largeData).length} chars`);
    console.log(`  - Encrypted size: ${JSON.stringify(encrypted).length} chars`);
    console.log(`  - Encryption time: ${encryptTime.toFixed(2)}ms`);
    console.log(`  - Decryption time: ${decryptTime.toFixed(2)}ms`);
} catch (error) {
    console.error('❌ Large data test failed:', error);
}

console.log('\n---\n');
console.log('🎉 All encryption tests complete!');
console.log('\nNote: Current implementation uses Base64 obfuscation.');
console.log('For cryptographic security, use server-side AES-256-CBC encryption.');
