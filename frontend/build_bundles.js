const esbuild = require('esbuild');
const path = require('path');

async function build() {
  console.log('Building standalone bundles for Django integration...');

  // 1. Build Booking Form bundle
  await esbuild.build({
    entryPoints: [path.join(__dirname, 'src/entries/booking_entry.tsx')],
    bundle: true,
    outfile: path.join(__dirname, 'dist/booking_app.bundle.js'),
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

  // 2. Build Dental Chart bundle
  await esbuild.build({
    entryPoints: [path.join(__dirname, 'src/entries/dental_chart_entry.tsx')],
    bundle: true,
    outfile: path.join(__dirname, 'dist/dental_chart_app.bundle.js'),
    define: {
      'process.env.NODE_ENV': '"production"'
    },
    minify: true,
    loader: { '.tsx': 'tsx', '.ts': 'ts' },
    target: ['es2020']
  });
  console.log('✓ Successfully built dental_chart_app.bundle.js -> frontend/dist/');
}

build().catch(err => {
  console.error(err);
  process.exit(1);
});
