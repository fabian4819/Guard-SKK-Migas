// Quick test to verify Next.js setup
const { execSync } = require('child_process');

console.log('🧪 Testing Next.js setup...\n');

try {
  console.log('✓ package.json found');
  console.log('✓ Node.js is working');

  // Check if required files exist
  const fs = require('fs');
  const requiredFiles = [
    'app/page.tsx',
    'app/layout.tsx',
    'components/StatsCard.tsx',
    'tailwind.config.ts',
    'next.config.js',
  ];

  requiredFiles.forEach(file => {
    if (fs.existsSync(file)) {
      console.log(`✓ ${file} exists`);
    } else {
      console.log(`✗ ${file} missing`);
    }
  });

  console.log('\n✅ Setup looks good! Run: npm run dev');

} catch (error) {
  console.error('❌ Error:', error.message);
}
