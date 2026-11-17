const esbuild = require('esbuild');
const path = require('path');
const fs = require('fs');

async function build() {
  console.log('Building standalone bundles for Django integration...');

  const distDir = path.join(__dirname, 'dist');
  const backendJsDir = path.join(__dirname, '../backend/static/js');

  // Ensure directories exist
  if (!fs.existsSync(distDir)) {
    fs.mkdirSync(distDir, { recursive: true });
  }

  // 1. Build Booking Form bundle
  await esbuild.build({
    entryPoints: [path.join(__dirname, 'src/entries/booking_entry.tsx')],
    bundle: true,
    outfile: path.join(distDir, 'booking_app.bundle.js'),
    alias: {
      'next/navigation': path.join(__dirname, 'src/entries/navigation_shim.ts')
    },
    define: {
      'process.env.NODE_ENV': '"production"'
    },
    minify: true,
    loader: { '.tsx': 'tsx', '.ts': 'ts' },
    target: ['es2020']
  });
  console.log('✓ Successfully built booking_app.bundle.js -> frontend/dist/');

  // Copy to backend static if directory exists
  if (fs.existsSync(backendJsDir)) {
    fs.copyFileSync(
      path.join(distDir, 'booking_app.bundle.js'),
      path.join(backendJsDir, 'booking_app.bundle.js')
    );
    console.log('✓ Synced booking_app.bundle.js -> backend/static/js/');
  }

  // 2. Build Dental Chart bundle
  await esbuild.build({
    entryPoints: [path.join(__dirname, 'src/entries/dental_chart_entry.tsx')],
    bundle: true,
    outfile: path.join(distDir, 'dental_chart_app.bundle.js'),
    define: {
      'process.env.NODE_ENV': '"production"'
    },
    minify: true,
    loader: { '.tsx': 'tsx', '.ts': 'ts' },
    target: ['es2020']
  });
  console.log('✓ Successfully built dental_chart_app.bundle.js -> frontend/dist/');

  if (fs.existsSync(backendJsDir)) {
    fs.copyFileSync(
      path.join(distDir, 'dental_chart_app.bundle.js'),
      path.join(backendJsDir, 'dental_chart_app.bundle.js')
    );
    console.log('✓ Synced dental_chart_app.bundle.js -> backend/static/js/');
  }
}

build().catch(err => {
  console.error(err);
  process.exit(1);
});
