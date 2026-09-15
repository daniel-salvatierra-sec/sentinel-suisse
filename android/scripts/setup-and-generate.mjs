/**
 * Non-interactive Bubblewrap setup: install Android cmdline-tools + generate TWA project.
 */
import fs from 'fs';
import path from 'path';
import os from 'os';
import { createRequire } from 'module';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
const bubblewrapRoot = path.dirname(
  require.resolve('@bubblewrap/cli/package.json', {
    paths: [path.join(os.homedir(), 'AppData', 'Roaming', 'npm', 'node_modules')],
  }),
);
const cliRequire = createRequire(path.join(bubblewrapRoot, 'package.json'));
const { AndroidSdkToolsInstaller } = cliRequire('./dist/lib/AndroidSdkToolsInstaller.js');
const { InquirerPrompt } = cliRequire('./dist/lib/Prompt.js');
const core = cliRequire('@bubblewrap/core');

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const androidDir = path.resolve(__dirname, '..');
const sdkPath = path.join(os.homedir(), '.bubblewrap', 'android_sdk');
const configPath = path.join(os.homedir(), '.bubblewrap', 'config.json');
const jdkPath = 'C:\\Program Files\\Microsoft\\jdk-17.0.20.101-hotspot';

async function ensureSdk() {
  fs.mkdirSync(sdkPath, { recursive: true });
  const hasTools = fs.existsSync(path.join(sdkPath, 'tools'));
  const hasBin = fs.existsSync(path.join(sdkPath, 'bin'));
  if (!hasTools && !hasBin) {
    console.log('Downloading Android command-line tools…');
    const prompt = new InquirerPrompt();
    const installer = new AndroidSdkToolsInstaller(process, prompt);
    await installer.install(sdkPath);
  } else {
    console.log('Android SDK tools already present.');
  }
  const config = {
    jdkPath,
    androidSdkPath: sdkPath,
  };
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  console.log('Wrote', configPath);
}

async function generateProject() {
  const manifestFile = path.join(androidDir, 'twa-manifest.json');
  const twaManifest = await core.TwaManifest.fromFile(manifestFile);
  const log = new core.ConsoleLog('generate');
  const generator = new core.TwaGenerator();
  console.log('Generating Android project in', androidDir);
  await generator.createTwaProject(androidDir, twaManifest, log, (n, total) => {
    if (n === total) console.log(`Progress ${n}/${total}`);
  });
  // Keep our curated twa-manifest (generator may rewrite icons paths)
  console.log('Project generated.');
}

await ensureSdk();
await generateProject();
console.log('Done.');
