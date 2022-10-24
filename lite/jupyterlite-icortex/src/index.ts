// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import { PageConfig, URLExt } from '@jupyterlab/coreutils';

import { JupyterLiteServer, JupyterLiteServerPlugin } from '@jupyterlite/server';

import * as kernelIcon32 from '!!file-loader!../style/logo-32x32.png';
import * as kernelIcon64 from '!!file-loader!../style/logo-64x64.png';

import { IKernel, IKernelSpecs } from '@jupyterlite/kernel';

import { PLUGIN_ID, UPSTREAM_PLUGIN_ID, PYODIDE_CDN_URL } from './tokens';

/**
 * A plugin to register the Pyodide kernel.
 */
const kernel: JupyterLiteServerPlugin<void> = {
  id: PLUGIN_ID,
  autoStart: true,
  optional: [IKernelSpecs],
  activate: (app: JupyterLiteServer, kernelspecs: IKernelSpecs) => {
    console.log(UPSTREAM_PLUGIN_ID, PYODIDE_CDN_URL, PageConfig, URLExt, kernelspecs);
    // const baseUrl = PageConfig.getBaseUrl();
    const config =
      JSON.parse(PageConfig.getOption('litePluginSettings') || '{}')[
        UPSTREAM_PLUGIN_ID
      ] || {};
    const url = config.pyodideUrl || PYODIDE_CDN_URL;
    const pyodideUrl = URLExt.parse(url).href;
    const rawPipUrls = config.pipliteUrls || [];
    const pipliteUrls = rawPipUrls.map((pipUrl: string) => URLExt.parse(pipUrl).href);
    const disablePyPIFallback = !!config.disablePyPIFallback;

    kernelspecs.register({
      spec: {
        name: 'icortex',
        display_name: 'ICortex',
        language: 'python',
        argv: [],
        spec: {
          argv: [],
          env: {},
          display_name: 'ICortex',
          language: 'python',
          interrupt_mode: 'message',
          metadata: {}
        },
        resources: {
          'logo-32x32': kernelIcon32.default,
          'logo-64x64': kernelIcon64.default
        }
      },
      create: async (options: IKernel.IOptions): Promise<IKernel> => {
        const { ICortexKernel } = await import('./kernel');

        return new ICortexKernel({
          ...options,
          pyodideUrl,
          pipliteUrls,
          disablePyPIFallback
        });
      }
    });
  }
};

const plugins: JupyterLiteServerPlugin<any>[] = [kernel];

export default plugins;
