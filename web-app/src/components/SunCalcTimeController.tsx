import { useState, useMemo, useCallback } from 'react'
import SunCalc from 'suncalc'
import './SunCalcTimeController.css'

// ── 中国城市预设 ────────────────────────────────────────────────
const PRESET_CITIES = [
  { name: '北京', lat: 39.9042, lng: 116.4074 },
  { name: '上海', lat: 31.2304, lng: 121.4737 },
  { name: '广州', lat: 23.1291, lng: 113.2644 },
  { name: '深圳', lat: 22.5431, lng: 114.0579 },
  { name: '成都', lat: 30.5728, lng: 104.0668 },
  { name: '杭州', lat: 30.2741, lng: 120.1551 },
  { name: '西安', lat: 34.3416, lng: 108.9398 },
  { name: '武汉', lat: 30.5928, lng: 114.3055 },
]

// ── 四季快捷日期 ────────────────────────────────────────────────
const SEASON_BUTTONS: { label: string; icon: string; date: Date }[] = [
  {
    label: '春分',
    icon: '🌸',
    date: new Date(new Date().getFullYear(), 2, 20), // 3月20日
  },
  {
    label: '夏至',
    icon: '☀️',
    date: new Date(new Date().getFullYear(), 5, 21), // 6月21日
  },
  {
    label: '秋分',
    icon: '🍂',
    date: new Date(new Date().getFullYear(), 8, 23), // 9月23日
  },
  {
    label: '冬至',
    icon: '❄️',
    date: new Date(new Date().getFullYear(), 11, 22), // 12月22日
  },
]

// ── 方位角 → 方向文字 ──────────────────────────────────────────
function azimuthToDirection(az: number): string {
  const dirs = ['北', '东北', '东', '东南', '南', '西南', '西', '西北']
  const idx = Math.round(az / 45) % 8
  return dirs[idx < 0 ? idx + 8 : idx]
}

// ── 数字格式化 ────────────────────────────────────────────────
function fmt2(n: number, decimals = 1): string {
  return n.toFixed(decimals)
}

// ── 角度转弧度 ────────────────────────────────────────────────
function degToRad(d: number) { return d * Math.PI / 180 }

// ── 主组件 ────────────────────────────────────────────────────
export interface SunCalcValues {
  time: Date
  lat: number
  lng: number
}

interface SunCalcTimeControllerProps {
  onChange?: (values: SunCalcValues) => void
}

export default function SunCalcTimeController({ onChange }: SunCalcTimeControllerProps) {
  const now = new Date()

  const [lat, setLat] = useState(39.9042)
  const [lng, setLng] = useState(116.4074)
  const [date, setDate] = useState<Date>(now)
  const [hour, setHour] = useState(now.getHours())
  const [minute, setMinute] = useState(now.getMinutes())

  // ── 合并时间到日期 ───────────────────────────────────────────
  const currentTime = useMemo(() => {
    const d = new Date(date)
    d.setHours(hour, minute, 0, 0)
    return d
  }, [date, hour, minute])

  // ── 太阳计算 ─────────────────────────────────────────────────
  const { times, position, sunIntensity } = useMemo(() => {
    const t = SunCalc.getTimes(currentTime, lat, lng)
    const p = SunCalc.getPosition(currentTime, lat, lng)
    const intensity = Math.max(0, Math.sin(degToRad(p.altitude)))
    return { times: t, position: p, sunIntensity: intensity }
  }, [currentTime, lat, lng])

  // ── 时分 → HH:MM 字符串 ──────────────────────────────────────
  const timeStr = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`

  // ── 拖动滑块同步更新 ─────────────────────────────────────────
  const handleTimeSlider = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const totalMin = parseInt(e.target.value)
    const h = Math.floor(totalMin / 60)
    const m = totalMin % 60
    setHour(h)
    setMinute(m)
  }, [])

  // ── 四季快捷按钮 ─────────────────────────────────────────────
  const handleSeason = useCallback((d: Date) => {
    setDate(new Date(d))
    setHour(12)
    setMinute(0)
  }, [])

  // ── 城市选择 ─────────────────────────────────────────────────
  const handleCity = useCallback((city: typeof PRESET_CITIES[0]) => {
    setLat(city.lat)
    setLng(city.lng)
  }, [])

  // ── 主动通知父组件 ───────────────────────────────────────────
  // （当需要在外部使用时 uncomment 这段）
  // useEffect(() => { onChange?.({ time: currentTime, lat, lng }) }, [currentTime, lat, lng, onChange])

  // ── 太阳是否在地平线下 ───────────────────────────────────────
  const isBelowHorizon = position.altitude < 0
  const altitudeDeg = position.altitude
  const azimuthDeg = ((position.azimuth * 180 / Math.PI) + 360) % 360 // 0-360 北=0
  const direction = azimuthToDirection(azimuthDeg)

  // ── 日出/日落时间 ────────────────────────────────────────────
  const fmtTime = (d: Date | null) => d ? d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false }) : '--:--'

  // ── 太阳图标（根据高度角变化）────────────────────────────────
  const sunIcon = isBelowHorizon
    ? '🌙'
    : altitudeDeg > 60
    ? '☀️'
    : altitudeDeg > 30
    ? '🌤️'
    : '🌅'

  return (
    <div className="sctc">
      {/* ── 标题栏 ─────────────────────────── */}
      <div className="sctc-header">
        <span className="sctc-header-icon">🕐</span>
        <span className="sctc-header-title">时空光影</span>
        <span className="sctc-header-badge">BETA</span>
      </div>

      {/* ── 城市选择 ─────────────────────────── */}
      <div className="sctc-section">
        <div className="sctc-section-label">📍 位置</div>
        <div className="sctc-city-grid">
          {PRESET_CITIES.map((city) => (
            <button
              key={city.name}
              className={`sctc-city-btn ${lat === city.lat && lng === city.lng ? 'sctc-city-btn--active' : ''}`}
              onClick={() => handleCity(city)}
              title={`${city.name} (${city.lat}, ${city.lng})`}
            >
              {city.name}
            </button>
          ))}
        </div>
        {/* 自定义经纬度输入 */}
        <div className="sctc-gps-row">
          <label className="sctc-gps-label">
            <span>LAT</span>
            <input
              className="sctc-gps-input"
              type="number"
              step="0.0001"
              value={lat}
              min={-90} max={90}
              onChange={e => setLat(parseFloat(e.target.value) || 0)}
            />
          </label>
          <label className="sctc-gps-label">
            <span>LNG</span>
            <input
              className="sctc-gps-input"
              type="number"
              step="0.0001"
              value={lng}
              min={-180} max={180}
              onChange={e => setLng(parseFloat(e.target.value) || 0)}
            />
          </label>
        </div>
      </div>

      {/* ── 日期选择 ─────────────────────────── */}
      <div className="sctc-section">
        <div className="sctc-section-label">📅 日期</div>
        <input
          className="sctc-date-input"
          type="date"
          value={date.toISOString().split('T')[0]}
          onChange={e => setDate(new Date(e.target.value + 'T12:00:00'))}
        />
        {/* 四季快捷 */}
        <div className="sctc-season-row">
          {SEASON_BUTTONS.map((btn) => (
            <button
              key={btn.label}
              className="sctc-season-btn"
              onClick={() => handleSeason(btn.date)}
            >
              <span>{btn.icon}</span>
              <span>{btn.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* ── 时间轴 ─────────────────────────── */}
      <div className="sctc-section">
        <div className="sctc-time-display">
          <span className="sctc-time-icon">{sunIcon}</span>
          <span className="sctc-time-value">{timeStr}</span>
          <span className={`sctc-time-badge ${isBelowHorizon ? 'sctc-time-badge--night' : ''}`}>
            {isBelowHorizon ? '夜间' : '白天'}
          </span>
        </div>
        <div className="sctc-slider-wrap">
          <span className="sctc-slider-label">🌅 00:00</span>
          <input
            className="sctc-slider"
            type="range"
            min={0}
            max={1439}
            value={hour * 60 + minute}
            onChange={handleTimeSlider}
          />
          <span className="sctc-slider-label">24:00</span>
        </div>
      </div>

      {/* ── 太阳信息卡片 ─────────────────────── */}
      <div className="sctc-info-grid">
        <div className="sctc-info-card">
          <div className="sctc-info-icon">🌅</div>
          <div className="sctc-info-val">{fmtTime(times.sunrise)}</div>
          <div className="sctc-info-key">日出</div>
        </div>
        <div className="sctc-info-card">
          <div className="sctc-info-icon">🌇</div>
          <div className="sctc-info-val">{fmtTime(times.sunset)}</div>
          <div className="sctc-info-key">日落</div>
        </div>
        <div className="sctc-info-card">
          <div className="sctc-info-icon">⬆️</div>
          <div className="sctc-info-val">{fmt2(altitudeDeg)}°</div>
          <div className="sctc-info-key">高度角</div>
        </div>
        <div className="sctc-info-card">
          <div className="sctc-info-icon">🧭</div>
          <div className="sctc-info-val">{direction} {fmt2(azimuthDeg, 0)}°</div>
          <div className="sctc-info-key">方位角</div>
        </div>
      </div>

      {/* ── 太阳强度条 ─────────────────────────── */}
      <div className="sctc-intensity">
        <div className="sctc-intensity-label">
          <span>☀️ 光强</span>
          <span className="sctc-intensity-val">{fmt2(sunIntensity * 100, 0)}%</span>
        </div>
        <div className="sctc-intensity-bar-bg">
          <div
            className="sctc-intensity-bar-fill"
            style={{ width: `${sunIntensity * 100}%` }}
          />
        </div>
      </div>

      {/* ── 提示文字 ─────────────────────────── */}
      <div className="sctc-hint">
        💡 拖动时间轴，观察建筑阴影随太阳位置变化
      </div>
    </div>
  )
}

// ── 导出工具函数（供 LitBuildingScene 使用）─────────────────────
export function calcSunLight(time: Date, lat: number, lng: number) {
  const position = SunCalc.getPosition(time, lat, lng)
  const altitudeDeg = position.altitude
  const azimuthDeg = ((position.azimuth * 180 / Math.PI) + 360) % 360

  const sunIntensity = Math.max(0, Math.sin(degToRad(altitudeDeg)))

  // Three.js directionalLight position:
  // azimuth: 太阳方位角（弧度），altitude: 太阳高度角（弧度）
  // 光源在球坐标系中的位置 → 转换为笛卡尔坐标
  const r = 100 // 光源距离（任意尺度）
  const altRad = degToRad(altitudeDeg)
  const aziRad = degToRad(azimuthDeg)

  // Three.js: position = [x, y, z]
  // y = r * sin(altitude), 投影半径 = r * cos(altitude)
  // x = 投影半径 * sin(azimuth - PI/2) [调整后使0度=北]
  // z = 投影半径 * cos(azimuth - PI/2)
  const proj = r * Math.cos(altRad)
  const x = proj * Math.sin(aziRad - Math.PI / 2)
  const y = r * Math.sin(altRad)
  const z = proj * Math.cos(aziRad - Math.PI / 2)

  return {
    position: [x, y, z] as [number, number, number],
    intensity: sunIntensity,
    altitudeDeg,
    azimuthDeg,
    isBelowHorizon: altitudeDeg < 0,
  }
}
