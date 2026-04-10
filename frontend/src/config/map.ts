/**
 * Map provider configuration.
 * Supports multiple map SDK adapters with fallback to coordinate projection.
 */

export enum MapProvider {
  COORDINATE = 'coordinate',
  AMAP = 'amap',
  BAIDU = 'baidu',
}

export interface MapConfig {
  provider: MapProvider
  apiKey?: string
  amap?: {
    version: string
    plugins: string[]
  }
  baidu?: {
    version: string
    ak: string
  }
}

const DEFAULT_CONFIG: MapConfig = {
  provider: MapProvider.COORDINATE,
  amap: {
    version: '2.0',
    plugins: ['AMap.Scale', 'AMap.ToolBar', 'AMap.Marker', 'AMap.Polyline'],
  },
  baidu: {
    version: '3.0',
    ak: '',
  },
}

export function getMapConfig(): MapConfig {
  const provider = (import.meta.env.VITE_MAP_PROVIDER as MapProvider) || MapProvider.COORDINATE
  const apiKey = import.meta.env.VITE_MAP_API_KEY || ''

  return {
    ...DEFAULT_CONFIG,
    provider,
    apiKey,
    amap: {
      version: DEFAULT_CONFIG.amap!.version,
      plugins: [...DEFAULT_CONFIG.amap!.plugins],
    },
    baidu: {
      version: DEFAULT_CONFIG.baidu!.version,
      ak: apiKey,
    },
  }
}

let amapLoadingPromise: Promise<void> | null = null

export async function loadAmapSdk(config: MapConfig): Promise<void> {
  if (window.AMap) {
    return
  }

  if (amapLoadingPromise) {
    return amapLoadingPromise
  }

  amapLoadingPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    const plugins = config.amap?.plugins?.join(',') || ''
    script.src = `https://webapi.amap.com/maps?v=${config.amap?.version}&key=${config.apiKey}&plugin=${plugins}`
    script.async = true

    window.__AMAP_INIT_CALLBACK = () => {
      delete window.__AMAP_INIT_CALLBACK
      resolve()
    }

    script.onerror = () => {
      amapLoadingPromise = null
      reject(new Error('Failed to load AMap SDK'))
    }

    document.head.appendChild(script)
  })

  return amapLoadingPromise
}

let baiduLoadingPromise: Promise<void> | null = null

export async function loadBaiduSdk(config: MapConfig): Promise<void> {
  if (window.BMap) {
    return
  }

  if (baiduLoadingPromise) {
    return baiduLoadingPromise
  }

  baiduLoadingPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = `https://api.map.baidu.com/api?v=${config.baidu?.version}&ak=${config.baidu?.ak}&callback=__BAIDU_MAP_INIT_CALLBACK`
    script.async = true

    window.__BAIDU_MAP_INIT_CALLBACK = () => {
      delete window.__BAIDU_MAP_INIT_CALLBACK
      resolve()
    }

    script.onerror = () => {
      baiduLoadingPromise = null
      reject(new Error('Failed to load Baidu Map SDK'))
    }

    document.head.appendChild(script)
  })

  return baiduLoadingPromise
}

declare global {
  interface Window {
    AMap?: unknown
    BMap?: unknown
    __AMAP_INIT_CALLBACK?: () => void
    __BAIDU_MAP_INIT_CALLBACK?: () => void
  }
}
