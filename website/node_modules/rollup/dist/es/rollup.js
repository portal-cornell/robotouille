/*
  @license
	Rollup.js v4.27.2
	Fri, 15 Nov 2024 17:19:22 GMT - commit a503a4dd9982bf20fd38aeb171882a27828906ae

	https://github.com/rollup/rollup

	Released under the MIT License.
*/
export { version as VERSION, defineConfig, rollup, watch } from './shared/node-entry.js';
import './shared/parseAst.js';
import '../native.js';
import 'node:path';
import 'path';
import 'node:process';
import 'node:perf_hooks';
import 'node:fs/promises';
import 'tty';
