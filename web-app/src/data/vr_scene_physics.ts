// VR场景物理数据 - 自动生成
export const vrScenePhysicsData = {
  "scenes": [
    {
      "id": "residential_villa",
      "name": "住宅别墅",
      "icon": "🏠",
      "defaultUrl": "https://vr.justeasy.cn/view/1597l51921h22936-1598173726.html",
      "alternatives": [
        "https://vr.justeasy.cn/view/1597l51921h22936-1598173726.html",
        "https://vr.justeasy.cn/view/176896e1x10amuo0-1775805609.html",
        "https://720yun.com/vr/5a21042f361beaf15e9ddf40"
      ],
      "physics": {
        "floor_material": "瓷砖/木地板",
        "floor_friction": 0.45,
        "floor_density": 2300,
        "wall_material": "砖墙",
        "wall_friction": 0.4,
        "wall_density": 1800,
        "wall_thickness": 240,
        "wall_load_bearing": false,
        "ceiling_material": "石膏板",
        "furniture": [
          "沙发",
          "茶几",
          "餐桌",
          "床",
          "衣柜",
          "书桌"
        ],
        "tags": [
          "住宅",
          "客厅",
          "卧室",
          "厨房",
          "卫生间"
        ]
      }
    },
    {
      "id": "garden",
      "name": "园林景观",
      "icon": "🌳",
      "defaultUrl": "https://vr.justeasy.cn/view/garden-sample-001.html",
      "alternatives": [
        "https://720yun.com/t1/5a21042f361beaf15e9ddf40",
        "https://720yun.com/t1/3d66a1c2318eaf15e9ddd40"
      ],
      "physics": {
        "floor_material": "石材/木栈道",
        "floor_friction": 0.55,
        "floor_density": 2600,
        "wall_material": "景观墙体",
        "wall_friction": 0.35,
        "wall_density": 2200,
        "wall_thickness": 200,
        "wall_load_bearing": false,
        "ceiling_material": "敞开",
        "furniture": [
          "景观石",
          "休闲椅",
          "亭子",
          "水景"
        ],
        "tags": [
          "园林",
          "庭院",
          "景观",
          "休闲"
        ]
      }
    },
    {
      "id": "commercial",
      "name": "商业综合体",
      "icon": "🏬",
      "defaultUrl": "https://vr.justeasy.cn/view/commercial-sample-001.html",
      "alternatives": [
        "https://720yun.com/t1/5a21042f361beaf15e9ddf41"
      ],
      "physics": {
        "floor_material": "石材/地砖",
        "floor_friction": 0.5,
        "floor_density": 2700,
        "wall_material": "混凝土/玻璃幕墙",
        "wall_friction": 0.3,
        "wall_density": 2400,
        "wall_thickness": 300,
        "wall_load_bearing": true,
        "ceiling_material": "铝扣板",
        "furniture": [
          "展示柜",
          "收银台",
          "休息区",
          "扶梯"
        ],
        "tags": [
          "商场",
          "店铺",
          "餐饮",
          "影院"
        ]
      }
    },
    {
      "id": "office",
      "name": "办公空间",
      "icon": "🏢",
      "defaultUrl": "https://vr.justeasy.cn/view/office-sample-001.html",
      "alternatives": [
        "https://720yun.com/t1/5a21042f361beaf15e9ddf42"
      ],
      "physics": {
        "floor_material": "地毯/地胶",
        "floor_friction": 0.55,
        "floor_density": 1500,
        "wall_material": "轻钢龙骨/玻璃",
        "wall_friction": 0.25,
        "wall_density": 800,
        "wall_thickness": 100,
        "wall_load_bearing": false,
        "ceiling_material": "矿棉板",
        "furniture": [
          "办公桌",
          "椅子",
          "文件柜",
          "会议桌"
        ],
        "tags": [
          "办公室",
          "会议室",
          "洽谈区",
          "前台"
        ]
      }
    },
    {
      "id": "hotel",
      "name": "酒店民宿",
      "icon": "🏨",
      "defaultUrl": "https://vr.justeasy.cn/view/hotel-sample-001.html",
      "alternatives": [
        "https://720yun.com/t1/5a21042f361beaf15e9ddf43"
      ],
      "physics": {
        "floor_material": "地毯/木地板",
        "floor_friction": 0.5,
        "floor_density": 1800,
        "wall_material": "轻质墙",
        "wall_friction": 0.3,
        "wall_density": 1200,
        "wall_thickness": 150,
        "wall_load_bearing": false,
        "ceiling_material": "乳胶漆",
        "furniture": [
          "床",
          "床头柜",
          "衣柜",
          "电视柜",
          "马桶",
          "淋浴房"
        ],
        "tags": [
          "客房",
          "大堂",
          "餐厅",
          "健身房",
          "游泳池"
        ]
      }
    }
  ]
} as const

export type VrSceneId = 'residential_villa' | 'garden' | 'commercial' | 'office' | 'hotel'
