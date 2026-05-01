import { useBuildingStore } from '../store/buildingStore'
import { worldModelStats, SCENE_CONFIGS } from '../data/sceneConfig'
import './StatusBar.css'

export default function StatusBar() {
  const activeCategory = useBuildingStore((s) => s.activeCategory)
  const activeScene = useBuildingStore((s) => s.activeScene)
  const objects = useBuildingStore((s) => s.objects)
  const selectedObject = useBuildingStore((s) => s.selectedObject)

  const sceneName = activeScene === 'all' ? '全部场景' :
    activeScene === 'ns_basement' ? '示范地下车库' :
    (SCENE_CONFIGS[activeScene]?.label || activeScene)

  const catName = activeCategory === 'all' ? '全部' :
    activeCategory === 'interior' ? '室内' :
    activeCategory === 'landscape' ? '园林' : '建筑'

  return (
    <div className="status-bar">
      <span className="status-item">
        🗺️ {catName} &gt; {sceneName}
      </span>
      <span className="status-divider" />
      <span className="status-item">🏠 {objects.length} 个空间对象</span>
      <span className="status-divider" />
      <span className="status-item">🖼️ {worldModelStats.totalVR} VR全景</span>
      <span className="status-divider" />
      <span className="status-item">📁 CAD: {worldModelStats.totalVR} VR + 17 DWG</span>
      {selectedObject && (
        <>
          <span className="status-divider" />
          <span className="status-item selected">✅ 已选中: {selectedObject.name}</span>
        </>
      )}
      <span className="status-spacer" />
      <span className="status-item hint">🖱️ 拖拽旋转 · 滚轮缩放 · 点击查看详情</span>
    </div>
  )
}
