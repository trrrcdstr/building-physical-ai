export const roomSceneData = {
  "rooms": [
    {
      "id": "room_00",
      "name": "主卧 1",
      "type": "master_bedroom",
      "type_cn": "主卧",
      "area_m2": 288.0,
      "door_count": 25,
      "window_count": 0,
      "adjacent_rooms": [
        "room_01"
      ],
      "center": [
        24.0,
        0,
        -3.0
      ],
      "width": 50.0,
      "depth": 5.0,
      "height_m": 2.8,
      "position": [
        24.0,
        0,
        -3.0
      ],
      "dimensions": {
        "width": 50.0,
        "depth": 5.0,
        "height": 2.8
      },
      "wall_exposures": [],
      "drill_analysis": {
        "north_wall_load_bearing": true,
        "south_wall_safe": true,
        "east_wall_caution": false,
        "west_wall_safe": true,
        "recommended_tools": [
          "impact_drill",
          "level",
          "stud_finder"
        ],
        "prohibited_areas": [
          "near_door_frames_30cm",
          "near_window_frames_50cm"
        ]
      },
      "furniture_clearances": [
        {
          "item": "bed",
          "margin_cm": 60,
          "direction": "front"
        },
        {
          "item": "wardrobe",
          "margin_cm": 80,
          "direction": "pull"
        },
        {
          "item": "desk",
          "margin_cm": 90,
          "direction": "chair_rear"
        }
      ],
      "vr_scene": null,
      "physics_tags": [],
      "cleaning_tags": [
        "地面清扫",
        "表面擦拭"
      ]
    },
    {
      "id": "room_01",
      "name": "书房 2",
      "type": "study",
      "type_cn": "书房",
      "area_m2": 288.0,
      "door_count": 25,
      "window_count": 0,
      "adjacent_rooms": [
        "room_02",
        "room_00"
      ],
      "center": [
        74.0,
        0,
        -3.0
      ],
      "width": 50.0,
      "depth": 5.0,
      "height_m": 2.8,
      "position": [
        74.0,
        0,
        -3.0
      ],
      "dimensions": {
        "width": 50.0,
        "depth": 5.0,
        "height": 2.8
      },
      "wall_exposures": [],
      "drill_analysis": {
        "north_wall_load_bearing": true,
        "south_wall_safe": true,
        "east_wall_caution": false,
        "west_wall_safe": true,
        "recommended_tools": [
          "impact_drill",
          "level",
          "stud_finder"
        ],
        "prohibited_areas": [
          "near_door_frames_30cm",
          "near_window_frames_50cm"
        ]
      },
      "furniture_clearances": [],
      "vr_scene": {
        "vr_id": 2,
        "platform": "Justeasy",
        "title": null,
        "designer": "杭州鑫满天装饰",
        "rooms": [
          "书房",
          "主卧",
          "次卧",
          "沙发床",
          "客厅看阳台",
          "餐边柜",
          "鞋柜静帧"
        ],
        "room_count": 7,
        "physics_tags": [
          "其他",
          "主卧",
          "地面高差",
          "玄关",
          "狭窄通道",
          "入户",
          "次卧",
          "客厅"
        ],
        "room_categories": [
          "次卧",
          "主卧",
          "次卧",
          "其他",
          "客厅",
          "其他",
          "玄关"
        ]
      },
      "physics_tags": [
        "其他",
        "主卧",
        "地面高差",
        "玄关",
        "狭窄通道",
        "入户",
        "次卧",
        "客厅"
      ],
      "cleaning_tags": [
        "地面清扫",
        "表面擦拭"
      ]
    },
    {
      "id": "room_02",
      "name": "客厅 3",
      "type": "living_room",
      "type_cn": "客厅",
      "area_m2": 288.0,
      "door_count": 25,
      "window_count": 0,
      "adjacent_rooms": [
        "room_03",
        "room_01"
      ],
      "center": [
        124.0,
        0,
        -3.0
      ],
      "width": 50.0,
      "depth": 5.0,
      "height_m": 2.8,
      "position": [
        124.0,
        0,
        -3.0
      ],
      "dimensions": {
        "width": 50.0,
        "depth": 5.0,
        "height": 2.8
      },
      "wall_exposures": [],
      "drill_analysis": {
        "north_wall_load_bearing": true,
        "south_wall_safe": true,
        "east_wall_caution": false,
        "west_wall_safe": true,
        "recommended_tools": [
          "impact_drill",
          "level",
          "stud_finder"
        ],
        "prohibited_areas": [
          "near_door_frames_30cm",
          "near_window_frames_50cm"
        ]
      },
      "furniture_clearances": [],
      "vr_scene": {
        "vr_id": 3,
        "platform": "Justeasy",
        "title": null,
        "designer": "杭州鑫满天装饰",
        "rooms": [
          "客厅",
          "餐厅",
          "主卧",
          "次卧",
          "棋牌区",
          "主卫",
          "次卫"
        ],
        "room_count": 7,
        "physics_tags": [
          "其他",
          "餐厅",
          "主卧",
          "滑倒风险",
          "潮湿",
          "防水",
          "卫生间",
          "次卧",
          "客厅",
          "水渍"
        ],
        "room_categories": [
          "客厅",
          "餐厅",
          "主卧",
          "次卧",
          "其他",
          "卫生间",
          "其他"
        ]
      },
      "physics_tags": [
        "其他",
        "餐厅",
        "主卧",
        "滑倒风险",
        "潮湿",
        "防水",
        "卫生间",
        "次卧",
        "客厅",
        "水渍"
      ],
      "cleaning_tags": [
        "地面清扫",
        "表面擦拭"
      ]
    },
    {
      "id": "room_03",
      "name": "客厅 4",
      "type": "living_room",
      "type_cn": "客厅",
      "area_m2": 288.0,
      "door_count": 25,
      "window_count": 0,
      "adjacent_rooms": [
        "room_04",
        "room_02"
      ],
      "center": [
        174.0,
        0,
        -3.0
      ],
      "width": 50.0,
      "depth": 5.0,
      "height_m": 2.8,
      "position": [
        174.0,
        0,
        -3.0
      ],
      "dimensions": {
        "width": 50.0,
        "depth": 5.0,
        "height": 2.8
      },
      "wall_exposures": [],
      "drill_analysis": {
        "north_wall_load_bearing": false,
        "south_wall_safe": true,
        "east_wall_caution": false,
        "west_wall_safe": true,
        "recommended_tools": [
          "impact_drill",
          "level",
          "stud_finder"
        ],
        "prohibited_areas": [
          "near_door_frames_30cm",
          "near_window_frames_50cm"
        ]
      },
      "furniture_clearances": [],
      "vr_scene": {
        "vr_id": 4,
        "platform": "Justeasy",
        "title": null,
        "designer": "桔子空间",
        "rooms": [
          "客厅",
          "餐厅",
          "主卫",
          "负一茶室",
          "负一休闲区"
        ],
        "room_count": 5,
        "physics_tags": [
          "滑倒风险",
          "餐厅",
          "其他",
          "潮湿",
          "防水",
          "卫生间",
          "客厅",
          "水渍",
          "书房"
        ],
        "room_categories": [
          "客厅",
          "餐厅",
          "卫生间",
          "书房",
          "其他"
        ]
      },
      "physics_tags": [
        "滑倒风险",
        "餐厅",
        "其他",
        "潮湿",
        "防水",
        "卫生间",
        "客厅",
        "水渍",
        "书房"
      ],
      "cleaning_tags": [
        "地面清扫",
        "表面擦拭"
      ]
    },
    {
      "id": "room_04",
      "name": "主卧 5",
      "type": "master_bedroom",
      "type_cn": "主卧",
      "area_m2": 288.0,
      "door_count": 25,
      "window_count": 0,
      "adjacent_rooms": [
        "room_05",
        "room_03"
      ],
      "center": [
        224.0,
        0,
        -3.0
      ],
      "width": 50.0,
      "depth": 5.0,
      "height_m": 2.8,
      "position": [
        224.0,
        0,
        -3.0
      ],
      "dimensions": {
        "width": 50.0,
        "depth": 5.0,
        "height": 2.8
      },
      "wall_exposures": [],
      "drill_analysis": {
        "north_wall_load_bearing": false,
        "south_wall_safe": true,
        "east_wall_caution": false,
        "west_wall_safe": true,
        "recommended_tools": [
          "impact_drill",
          "level",
          "stud_finder"
        ],
        "prohibited_areas": [
          "near_door_frames_30cm",
          "near_window_frames_50cm"
        ]
      },
      "furniture_clearances": [
        {
          "item": "bed",
          "margin_cm": 60,
          "direction": "front"
        },
        {
          "item": "wardrobe",
          "margin_cm": 80,
          "direction": "pull"
        },
        {
          "item": "desk",
          "margin_cm": 90,
          "direction": "chair_rear"
        }
      ],
      "vr_scene": null,
      "physics_tags": [],
      "cleaning_tags": [
        "地面清扫",
        "表面擦拭"
      ]
    },
    {
      "id": "room_05",
      "name": "客厅 6",
      "type": "living_room",
      "type_cn": "客厅",
      "area_m2": 288.0,
      "door_count": 10,
      "window_count": 15,
      "adjacent_rooms": [
        "room_06",
        "room_04"
      ],
      "center": [
        259.0,
        0,
        -3.0
      ],
      "width": 20.0,
      "depth": 5.0,
      "height_m": 2.8,
      "position": [
        259.0,
        0,
        -3.0
      ],
      "dimensions": {
        "width": 20.0,
        "depth": 5.0,
        "height": 2.8
      },
      "wall_exposures": [
        "multiple_windows"
      ],
      "drill_analysis": {
        "north_wall_load_bearing": false,
        "south_wall_safe": true,
        "east_wall_caution": true,
        "west_wall_safe": true,
        "recommended_tools": [
          "impact_drill",
          "level",
          "stud_finder"
        ],
        "prohibited_areas": [
          "near_door_frames_30cm",
          "near_window_frames_50cm"
        ]
      },
      "furniture_clearances": [],
      "vr_scene": {
        "vr_id": 6,
        "platform": "Justeasy",
        "title": null,
        "designer": "杭州鑫满天装饰",
        "rooms": [
          "客厅",
          "餐厅"
        ],
        "room_count": 2,
        "physics_tags": [
          "客厅",
          "餐厅"
        ],
        "room_categories": [
          "客厅",
          "餐厅"
        ]
      },
      "physics_tags": [
        "客厅",
        "餐厅"
      ],
      "cleaning_tags": [
        "地面清扫",
        "表面擦拭"
      ]
    },
    {
      "id": "room_06",
      "name": "客厅 7",
      "type": "living_room",
      "type_cn": "客厅",
      "area_m2": 0.0,
      "door_count": 0,
      "window_count": 1,
      "adjacent_rooms": [
        "room_05"
      ],
      "center": [
        0,
        0,
        0
      ],
      "width": 5.0,
      "depth": 5.0,
      "height_m": 2.8,
      "position": [
        0,
        0,
        0
      ],
      "dimensions": {
        "width": 5.0,
        "depth": 5.0,
        "height": 2.8
      },
      "wall_exposures": [
        "single_window"
      ],
      "drill_analysis": {
        "north_wall_load_bearing": false,
        "south_wall_safe": true,
        "east_wall_caution": true,
        "west_wall_safe": true,
        "recommended_tools": [
          "impact_drill",
          "level",
          "stud_finder"
        ],
        "prohibited_areas": [
          "near_door_frames_30cm",
          "near_window_frames_50cm"
        ]
      },
      "furniture_clearances": [],
      "vr_scene": {
        "vr_id": 7,
        "platform": "Justeasy",
        "title": null,
        "designer": "杭州鑫满天装饰",
        "rooms": [
          "客厅",
          "餐厅"
        ],
        "room_count": 2,
        "physics_tags": [
          "客厅",
          "餐厅"
        ],
        "room_categories": [
          "客厅",
          "餐厅"
        ]
      },
      "physics_tags": [
        "客厅",
        "餐厅"
      ],
      "cleaning_tags": [
        "地面清扫",
        "表面擦拭"
      ]
    }
  ],
  "edges": [
    {
      "source": "room_00",
      "target": "room_01",
      "relation": "adjacent",
      "connection_type": "door",
      "distance": 2
    },
    {
      "source": "room_01",
      "target": "room_02",
      "relation": "adjacent",
      "connection_type": "door",
      "distance": 2
    },
    {
      "source": "room_02",
      "target": "room_03",
      "relation": "adjacent",
      "connection_type": "door",
      "distance": 2
    },
    {
      "source": "room_03",
      "target": "room_04",
      "relation": "adjacent",
      "connection_type": "door",
      "distance": 2
    },
    {
      "source": "room_04",
      "target": "room_05",
      "relation": "adjacent",
      "connection_type": "door",
      "distance": 2
    },
    {
      "source": "room_05",
      "target": "room_06",
      "relation": "adjacent",
      "connection_type": "door",
      "distance": 2
    }
  ],
  "meta": {
    "generated_at": "2026-04-21",
    "source": "VR_KNOWLEDGE + building_objects",
    "room_count": 7,
    "edge_count": 6
  }
}