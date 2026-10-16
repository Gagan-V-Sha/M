import fs from 'node:fs'
import { spawnSync } from 'node:child_process'

const realCwd = fs.realpathSync.native(process.cwd())
const extraArgs = process.argv.slice(2)
const vitestCommand = extraArgs.length > 0
  ? `npx vitest ${extraArgs.join(' ')}`
  : 'npx vitest run'

const result = spawnSync(vitestCommand, {
  cwd: realCwd,
  stdio: 'inherit',
  shell: true,
})

process.exit(result.status ?? 1)
