# Bug: Frontend tests fail with missing jsdom dependency

## Summary

Running frontend tests with `npm test` fails because the required `jsdom` dependency is not installed. Vitest attempts to auto-install it but the installation fails due to a peer dependency conflict (see related bug report).

## Environment

- Date observed: 2026-03-04
- OS: Linux (Debian GNU/Linux 13 / dev container)
- Working directory: `app/frontend`
- Test runner: vitest@4.0.18
- Command: `npm test -- --run`

## Steps to Reproduce

1. Open a terminal.
2. Change directory to `app/frontend`.
3. Run:
   ```bash
   npm test -- --run
   ```

## Expected Behavior

Tests should run with jsdom as the browser environment simulator. If jsdom is missing, vitest should successfully auto-install it and proceed with tests.

## Actual Behavior

Vitest detects missing jsdom dependency and prompts for installation, but the installation fails:

```text
MISSING DEPENDENCY  Cannot find dependency 'jsdom'

✔ Do you want to install jsdom? … yes
npm error code ERESOLVE
npm error ERESOLVE could not resolve
```

Test execution is blocked completely.

## Full Error (excerpt)

```text
 MISSING DEPENDENCY  Cannot find dependency 'jsdom'

✔ Do you want to install jsdom? … yes
npm error code ERESOLVE
npm error ERESOLVE could not resolve
npm error
npm error While resolving: eslint-plugin-react-hooks@7.0.1
npm error Found: eslint@10.0.2
[... peer dependency conflict details ...]

⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯ Startup Error ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯
z [Error]: Process exited with non-zero status (1)
    at VitestPackageInstaller.ensureInstalled
    at prepareVitest
    at startVitest
```

## Notes / Initial Analysis

- **Missing dependency**: `jsdom` is required for vitest to simulate a browser environment for React component tests
- **Why it's missing**:
  - `jsdom` is not listed in `package.json` devDependencies
  - Vitest can use multiple test environments (node, jsdom, happy-dom)
  - The project relies on vitest's auto-installation feature instead of explicit dependency
- **Why auto-install fails**: Unrelated peer dependency conflict prevents any npm install operations (see related bug report)

## Root Cause

**Missing explicit jsdom dependency in package.json**

The `jsdom` package should be listed as an explicit devDependency but is missing from `package.json`. The project was relying on vitest's auto-installation feature, which works in normal conditions but fails when there are peer dependency conflicts.

Current `package.json` devDependencies:

```json
{
  "devDependencies": {
    "@testing-library/jest-dom": "^6.4.2",
    "@testing-library/react": "^16.3.2",
    "@types/react": "^19.2.14",
    "@types/react-dom": "^19.2.3",
    "@typescript-eslint/eslint-plugin": "^8.56.1",
    "@typescript-eslint/parser": "^8.56.1",
    "@vitejs/plugin-react": "^5.1.4",
    "autoprefixer": "^10.4.17",
    "eslint": "^10.0.2",
    "eslint-plugin-react-hooks": "^7.0.1",
    "eslint-plugin-react-refresh": "^0.5.2",
    "postcss": "^8.4.35",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.3.3",
    "vite": "^7.3.1",
    "vitest": "^4.0.18"
  }
}
```

Note: `jsdom` is absent from the list.

## Solution Applied

**Add jsdom as an explicit devDependency**

Once the peer dependency conflict is resolved (see bug report #bug2026034), install jsdom explicitly:

```bash
cd app/frontend
npm install --save-dev jsdom
```

This will add jsdom to `package.json`:

```json
{
  "devDependencies": {
    "jsdom": "^26.0.0",
    ...
  }
}
```

## Status

**✅ RESOLVED** — 2026-03-04

Successfully resolved by installing jsdom as an explicit devDependency after fixing the peer dependency conflict.

## Resolution Applied

After resolving the ESLint peer dependency conflict (bug #2026034), jsdom was installed successfully:

```bash
cd app/frontend
npm install --save-dev jsdom
```

This added jsdom to package.json devDependencies:

```json
{
  "devDependencies": {
    "jsdom": "^26.0.0",
    ...
  }
}
```

### Verification

✅ jsdom installed successfully (added 43 packages)
✅ No vulnerabilities introduced
✅ Vitest now initializes correctly with jsdom environment
✅ All frontend checks pass (lint, type-check, build)

## Why This Should Be an Explicit Dependency

### 1. Reliability

- Explicit dependencies ensure consistent installations across environments
- Auto-installation can fail in edge cases (peer conflicts, network issues, CI restrictions)
- Makes the dependency tree clear and auditable

### 2. Version Control

- Allows pinning to specific jsdom versions
- Prevents unexpected behavior from auto-upgraded versions
- Enables security auditing of exact versions used

### 3. CI/CD Best Practices

- CI environments may have restricted network access
- Explicit dependencies make builds reproducible
- Faster installs (no interactive prompts or auto-detection)

### 4. Developer Experience

- Clear documentation of what the project needs
- No surprises during initial setup
- Matches industry standard practices

## Lessons Learned

### 1. Explicit Dependencies

- Always declare test environment dependencies explicitly
- Don't rely on auto-installation features for critical dependencies
- Test environment libraries (jsdom, happy-dom) should be in devDependencies

### 2. Hidden Dependencies

- Auto-installation features can mask missing dependencies
- Missing dependencies may only surface in specific scenarios (like peer conflicts)
- Explicit is better than implicit (Python's Zen applies here too!)

### 3. Testing Setup

- Vitest configuration should specify the environment explicitly:
  ```typescript
  // vitest.config.ts
  export default defineConfig({
    test: {
      environment: "jsdom", // explicitly specify
    },
  });
  ```
- Having the explicit dependency matching the explicit config prevents mismatches

### 4. Dependency Auditing

- Regular dependency audits should check for:
  - Missing peer dependencies
  - Auto-installed packages not in package.json
  - Implicit dependencies that should be explicit

## Next Steps

### Immediate Actions (after peer conflict resolved)

- [x] Install jsdom explicitly: `npm install --save-dev jsdom`
- [x] Verify vitest.config.ts specifies `environment: 'jsdom'`
- [x] Run tests to confirm they work: `npm test -- --run` (vitest runs, no test files found)
- [ ] Commit updated package.json and package-lock.json

### Follow-up

- [ ] Audit other potential auto-installed dependencies
- [ ] Document test setup in CONTRIBUTING.md or TESTING.md
- [ ] Add dependency completeness check to code review checklist
- [ ] Consider adding a script to detect missing peer dependencies

## Related Issues

- **Blocking issue**: [bug2026034-eslint-peer-dependency-conflict.md](bug2026034-eslint-peer-dependency-conflict.md) - Must be resolved first
- The peer dependency conflict prevents installation of jsdom and any other dependencies

## Implementation Order

1. **First**: Fix the ESLint peer dependency conflict (bug #2026034)
2. **Then**: Install jsdom explicitly (this issue)
3. **Finally**: Verify full test suite runs successfully

## References

- [Vitest environment configuration](https://vitest.dev/config/#environment)
- [jsdom documentation](https://github.com/jsdom/jsdom)
- [npm dependency best practices](https://docs.npmjs.com/cli/v10/configuring-npm/package-json#dependencies)
