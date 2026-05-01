# 机器人执行器与SDK技术知识库

> 本文档提取自技术手册，已去除厂商名称、联系方式等商业信息，仅保留技术参数与使用说明
>
> **处理时间**: 2025-04-24
> **数据来源**: 
> - 伺服电缸厂商F - 微型伺服电缸选型手册（扫描件，未提取）
> - 控制系统厂商G - 光纤陀螺及惯导产品手册
> - 协作机器人厂商H - xCore SDK C++使用手册V3.0
> - 协作机器人厂商H - xCore SDK Python使用手册V3.0

---

## 微型伺服电缸选型手册.pdf

> **注意**: 该PDF为扫描件/图片格式，无法直接提取文本内容。以下为该文档的基本信息：
> - 文件类型: 微型伺服电缸产品选型手册
> - 厂商类别: 伺服电缸厂商F
> - 建议: 如需获取该文档中的技术参数（行程、推力、速度、精度等），请使用OCR工具或手动查阅原PDF文件

---

## CN(PDF版）天陆海产品手册（CN-V3.0-25.11.18）.pdf

### 产品概述

P01-06
P04-15
TLH-INS-J 机载捷联惯导系统
TLH-INS-A 车载定位定向导航系统
TLH-INS-K 矿车定位定向导航系统
TLH-IMU 惯性测量单元
TLH-M 组合导航模块
P03-04
P05
P07
P08
P09-10
P11-12
P13-14
P15-16
P17-18
P19-20
让导航更精准
光纤陀螺及惯导提供商
控制系统厂商G（四川）导航智能设备有限公司及其深圳子公司（深
圳市控制系统厂商G导航设备技术有限责任公司）是目前全球唯一一家垂
直集成了光纤器件、高精度光纤陀螺仪、光纤混合惯导、MEMS
惯导、惯性测量单元、光纤惯导及光纤组合导航定位产品的全链
条企业，拥有行业领先的自有高标准光纤陀螺仪和惯性测量单元
惯导、惯导算法、多传感器融合算法、系统及整体解决方案等领
作为全球惯导技术的领导者，控制系统厂商G导航独家首创并实现了
革命性的光纤陀螺仪与 MEMS 混合惯导技术，成功突破了传统
惯导技术的局限，实现了高精度与低成本的双重优势。控制系统厂商G产
导弹、军民用飞机、无人机、EVTOL、自动驾驶、矿山、无人
矿卡、石油勘测、煤矿机械、机器人、船舶等移动载体，以及测
量测绘、地理信息系统(GIS)数据采集等领域，提供高性价比、
高精度的定位服务。
未来，控制系统厂商G导航将持续加大研发创新投入，秉承 “十年磨
一剑” 的坚韧精神，坚守核心技术研发，为中国惯性组合导航及
水下机器人
AGV
工程机械服务机器人
从关键器件、惯性测量单元到组合导航系统全部掌握核心技术
发明名称 ：具有自检功能的光纤陀螺仪及其自检方法
至智荟公园A4栋103
发明名称 ：具有自检功能的光纤陀螺仪及其自检方法
至智荟公园A4栋103

### 技术参数

等导航参数
组合导航系统算法应用
高精度、高可靠性导航算法
针对客户应用场景进行多传感器融合定制开发
基于信号定位
全球卫星导航
V2X定位
UWB
视觉定位
定位方式 融合定位
系统参数
可融合空速管、磁力计、高度计、等多传感器
可实时输出载体位置、速度、航向、姿态等信息
具备多种串口通信方式
采样频率高、带宽高、动态适应性强
配套的上位机软件功能完整，在线监测系统和惯性器件的工作状态和性能
系统精度
系统参数
输出频率高，数据稳定可靠
电路集成度高，导航解算、加表 IF 转换等电路集成化设计
整机一体化设计，结构紧凑，可内置GNSS模组和高程计
系统参数
系统快速响应能力强
具有参数标定功能，可接受标定参数写入
具备接收外部控制信号，接收标定参数并对陀螺以及加表信息重新补偿并输出的功能
陀螺精度
系统参数
载体三个轴向的角速率和线加速度测量精度高
具备防水密闭性能，抗电磁干扰能力强，满足系统在复杂电磁环境下使用的要求
该系统内部集成陀螺仪、加速度计、温度传感器等多传感器，采用高性能小体积  MCU，自适应宽电源输入，可接入里
系统参数
TLH-IMU-600M 型
各类L3级辅助驾驶车辆 各类无人叉车 各类机器人 各类AGV/AMR
0.1°
0.1°
辅助传感器
数据更新频率（默认）
输入电压
系统参数

### 使用说明

使用多个器件来测量同一信
光纤陀螺关键技术 高精度惯导技术
TLH-INS-370D-26A型
高精度三轴光纤惯导
TLH-INS-170M-26A混合型
混合光纤组合导航系统
TLH-INS-600M-21A型
MEMS组合导航系统
TLH-IMU-600M型
TLH-INS-J
机载捷联惯性导航系统
TLH-INS-J 型机载惯性导航系统内置自研三轴光纤陀螺仪和三轴加速度计(石英/MEMS),可配置接收外部发送
的辅助定位信息或外接GNSS接收机等多传感器实现组合导航，可良好的满足长时间、高精度、高可靠性导航应用
需求。TLH-INS-J 系列可广泛应用于各种类型运输机、各类无人机等飞控平台。
系统精度
具有在线标定功能，避免人为安装误差
自主性强，基于车载配置的里程计等其他传感器进行自主导航与定位
具有安装基准靠面，可根据用户需求提供方位基准棱镜
程计外部辅助信息 ,  并配置 CAN、422/232 多种外部接口， 具有良好的扩展性。
系统精度

### API接口

发明名称 ：自定义协议支持多接口的通讯方法
路全至智荟公园A4栋103
通过捷联惯导算法对惯性器件
到运载体的姿态、速度和位置
输出协议、接口定义、外形均可根据需求进行定制
光电吊舱 各类无人机 各类低轨卫星 各类水下机器人 各类无人船
TLH-INS-370D-26J 型
光纤陀螺捷联惯导系统
TLH-INS-350M-03J 型
光纤陀螺捷联惯导系统
航向精度(RMS)
水平姿态(RMS)
纯惯性导航(CEP)
组合导航(融合 RTK)
组合导航速度(RMS)
通讯接口
数据更新频率（默认）
供电电压
尺寸（mm）
重量（kg）
陀螺类型
陀螺角度随机游走
TLH-INS-370D-26J
±450°/s
≤ 0.03°/h
≤ 0.03°/h
≤0.003°/√h
±30g
≤ 30μg
TLH-INS-370M-05J
TLH-INS-370D-26J TLH-INS-370M-05J
±500°/s
≤ 0.3°/h
≤ 0.3°/h
≤0.02°/√h
±20g
≤50μg
TLH-INS-350M-03J
TLH-INS-350M-03J
TLH-INS-370D-26J TLH-INS-370M-05J TLH-INS-350M-03J
±500°/s
≤ 0.07°/h
≤ 0.07°/h
≤0.006°/√h
±20g
≤50μg
RS232*2(RTK和数据线)；RS422*2(数据线)；CAN*1(里程计及数据线)；PPS*1(同步)
200Hz （可定制）
5g@20~2000Hz
40g，11ms，1/2Sine
18~36VDC
≤ 25W@24VDC
≤ 10W@24VDC
≥1nmile/1h
1.5m/s
3.0 nmile/1h
5m/s
2.0 nmile/1h
2cm+1ppm(融合RTK)，1.5m(单点定位)
3m/s
TLH-INS-370M-05J 型
光纤陀螺捷联惯导系统
≤ 25W@24VDC
TLH-INS-370D-26A型
光纤陀螺定位定向
导航系统
TLH-INS-170M-26A混合型
光纤陀螺定位定向
导航系统
TLH-INS-150M-23A混合型
光纤陀螺定位定向
导航系统
TLH-INS-600M-21A型
MEMS陀螺定位定向
导航系统
TLH-INS-A
车载定位定向导航系统
TLH-INS-A 型车载定位定向导航系统是基于国产高精度光纤陀螺仪/MEMS陀螺仪和石英挠性加表/MEMS加表构成的
惯性导航装置，可以与里程计、高程计等多传感器融合，实现组合导航，可自主、实时、连续为载体提供高精度的位置、
速度、航向、姿态角等信息，可满足陆用各类载体对高精度定位、定向的需求。
具有时统接口，可与其他设备进行时间同步
接口丰富，适应性强，具有双CAN、RS422、RS232、同步秒冲等各类接口，可根据用户需求进行定制
矿卡 港口平板车 各类应急车 各类特种车 各类低速无人车
TLH-INS-370D-26A型
高精度光纤 组合导航定位系统
TLH-INS-170M-26A混合型
光纤+MEMS混合型
组合导航定位系统
TLH-INS-600M-21A型
MEMS组合导航定位系统
航向角精度
姿态角精度
水平位置精度
数据更新频率（默认）
速度精度
TLH-INS-370D-26A TLH-INS-170M-26A TLH-INS-150M-23A TLH-INS-600M-21A
机型 TLH-INS-370D-26A TLH-INS-170M-26A TLH-INS-150M-23A TLH-INS-600M-21A
≤ 0.1°×Sec(Lati),
10min (自寻北精对准)
≤ 0.1°，1m基线，
≤ 0.1°，1m基线，
≤ 0.1°，1m基线，
≤ 0.1°，1m基线，
≤0.02° (实时)；
≤0.015° (后处理) ≤0.1° ≤0.1° ≤0.1°
≤ 0.8‰（GNSS失锁30min） ≤0.2%（GNSS失锁30min） ≤0.2%（GNSS失锁15min） ≤0.2%
（GNSS失锁1Km或120s）
200Hz（可定制）
≤ 3.0 m/s (纯惯性 1h)
≤ 0.05 m/s (卫导组合)
≤ 0.1 m/s (卫导组合) ≤ 0.1 m/s (卫导组合) ≤ 0.1 m/s (卫导组合)
≤ 5min（粗对准）
5g@20~2000Hz
40g，11ms，1/2Sine
18V～36V； 额定电压：24V 9V～36V；额定电压：12V 9V～36V；额定电压：12V 9V～36V；额定电压：12V
≤ 20W@24VDC ≤10W@12VDC ≤8W@12VDC ≤6W@12VDC
RS232*2(RTK和数据线)；
RS422*2(数据线)；
CAN*1(里程计及数据线)；
PPS*1(同步)
RS232*2(RTK和数据线)；
RS422*1(数据线)；
CAN*1(里程计及数据线)；
PPS*1(同步)
陀螺类型
陀螺角度随机游走
TLH-INS-370D-26A
±450°/s
≤ 0.03°/h
0.003°/√h
±20g
≤ 30μg
TLH-INS-170M-26A
70 型光纤陀螺+MEMS型陀螺
±450°/s
≤ 0.07°/h+15°/h
0.003°/√h+0.25°/√h
±6g
≤200μg
TLH-INS-150M-23A
50 型光纤陀螺+MEMS型陀螺
±500°/s
≤ 0.3°/h+1.5°/h(Allan）
≤0.02°/√h+0.25°/√h
±6g
≤200μg
TLH-INS-600M-21A
MEMS型陀螺
±300°/s
≤ 1.5°/h(Allan）
≤0.25°/√h
±6g
≤200μg
供电电压
尺寸（mm）
重量（kg）
通讯接口
TLH-INS-K
矿车定位定向导航系统
矿车定位定向导航系统是基于三只全国产化光纤陀螺和三只石英挠性加速度计构成的惯性导航装置，支持多种
对准模式，可实现矿内定位定向功能，可融合里程计、UWB等技术实现组合导航。该产品自主性强、可靠性高，
可连续为采煤机、掘锚机等设备提供高精度的位置、速度、航向、姿态等信息。
系统精度
整机一体化设计，电路集成度高、预留多个扩展功能接口
惯性器件的带宽高、采样频率高，动态误差抑制效果好
各类采煤机 各类盾构机 各类大型矿车
TLH-INS-370D-56K 型
高精度光纤定位定向导航系统
航向角精度
姿态角精度
纯惯位置精度
通讯接口
陀螺类型
TLH-INS-398D-59K
±200°/s
≤ 0.002°/h
≤ 0.002°/h
≤ 10μg
±30g
≤ 10μg
±300°/s
≤ 0.005°/h
≤ 0.005°/h
≤ 20μg
±30g
≤ 20μg
±450°/s
≤ 0.03°/h
≤ 0.03°/h
≤ 30μg
±30g
≤ 30μg
TLH-INS-398D-58K TLH-INS-370D-56K
TLH-INS-398D-59K TLH-INS-398D-58K TLH-INS-370D-56K
TLH-INS-398D-59K TLH-INS-398D-58K TLH-INS-370D-56K
0.0025° 0.005° 0.02°
0.6nmile/h 0.8nmile/h 1nmile/h
RS232*2(RTK和数据线)；RS422*2(数据线)；CAN*1(里程计及数据线)；PPS*1(同步)
5g@20~2000Hz
40g，11ms，1/2Sine
0.03°（自寻北）
≤ 0.1°,（1m基线，双天线 ）
0.05°（自寻北）
≤ 0.1°,（1m基线，双天线 ）
0.075°（自寻北）
≤ 0.1°,（1m基线，双天线 ）
纯惯速度精度
数据更新频率（默认）
200Hz（可定制）
3.0m/s1.5m/s1m/s
初始对准 ≤ 5 min
工作电压 18~36VDC
功耗 ≤ 50 W ≤ 35 W ≤ 25 W
尺寸 (mm) 350×225×215 350×225×215 151.1×100×118.5
10 6 ≤ 4重量(kg)
TLH-IMU
TLH-IMU 系列惯性测量单元是基于国产高精度光纤陀螺仪和石英挠性加速度计构成的惯性测量装置，可实时测量和
输出载体三个轴向的角速率和线加速度信号以及三维姿态信息。该系列产品具有精度高、体积小、重量轻、功耗低等特点
具有实时输出沿三个轴向（X, Y ,Z）的线加速度以及绕三个轴向角运动的角速度的功能
具备 RS422 数字接口输出，可根据用户需求进行定制
各类电动飞机 各类L4级自动驾驶车辆 各类高精度自适应无人叉车
加速度计精度
TLH-IMU-370D-06J 型
TLH-IMU-370M-05J 型
TLH-IMU-170M-04J 型
TLH-IMU-600M-31A 型
MEMS惯性测量单
数据更新频率（默认）
TLH-IMU-370D-06J TLH-IMU-370M-05J TLH-IMU-350M-03J TLH-IMU-170M-04J
±450° /s
≤ 0.03° /h
≤ 0.03° /h
0.003°/√h
±450° /s
≤ 0.07° /h
≤ 0.07° /h
0.006°/√h
±300° /s
≤ 0.3° /h
≤ 0.3° /h
0.03°/√h
±300° /s
≤ 0.1° /h+1.5°/h(Allan)
≤ 0.1° /h+10°/h
0.01°/√h+0.2°/√h
TLH-IMU-600M-31A
TLH-IMU-370D-06J TLH-IMU-370M-05J TLH-IMU-350M-03J TLH-IMU-170M-04J TLH-IMU-600M-31A
TLH-IMU-370D-06J TLH-IMU-370M-05J TLH-IMU-350M-03J TLH-IMU-170M-04J TLH-IMU-600M-31A
±300° /s
1.5°/h(Allan)
10°/h
0.2°/√h
供电电压
尺寸（mm）
重量（kg）
通讯接口
5g@20~2000Hz
40g，11ms，1/2Sine
18~36 VDC
25W@28VDC
18~36 VDC
15W@28VDC
9~36VDC
10W@28 VDC
9~36VDC
5W@28 VDC
9~36VDC
1W@12 VDC
RS232*2 (RTK和数据线)；
RS422*2 (数据线)；
CAN*1 (里程计及数据线)；
PPS*1 (同步)
RS422*2(数据线)；PPS*1(同步) RS232/RS422、PPS
分辨率
±20g (或 ±30g 可选)
≥ 200Hz
≤ 70μg
≤ 0.1mg
≤ 50μg
≤ 50μg
±20g (或 ±30g 可选)
≥ 200Hz
≤ 70μg
≤ 0.1mg
≤ 50μg
≤ 50μg
±20g (或 ±30g 可选)
≥ 200Hz
≤ 70μg
≤ 0.1mg
≤ 50μg
≤ 50μg
±6g
≥ 200Hz
≤ 100μg
≤ 0.5mg
≤200μg
≤200μg
±6g
≥ 200Hz
≤ 100μg
≤ 0.5mg
≤200μg
≤200μg
5g@20~2000Hz
40g，11ms， 1/2Sine
TLH-IMU-350M-03J 型
200Hz（可定制）
组合导航模块
TLH-M 型产品为 MEMS 惯性导航模块，可用于测量载体的姿态、航向、速度、位置等信息，  具有体积小、精度高
接口类型
重量（g）
尺寸（mm）
陀螺类型
陀螺角度随机游走
TLH-IMU-600M
TLH-IMU-600M
TLH-IMU-600M
200 Hz（可定制）
3.3 VDC
≤0.5 w
UART*1; SPI*1
25±3g
支持外接GNSS，实现松耦合
工作范围广，采用硅微 MEMS 器件，抗振动冲击能力强
适应性强， 支持 GPS/BD2/GLONASS 三模卫星导航系统, 具有高跟踪灵敏度，适用于街道、丛林等复杂环境
用户体验好，支持串口、SPI 等多种通信方式
输出协议、接口定义、可根据需求进行定制 MEMS型陀螺
±300°/s
≤ 1.5°/h
≤0.25°/√h
±6g
≤100μg
速度
类型
姿态测量范围
0.1m/s
IMU
360°
TLH-F 系列该产品属于干涉型数字单轴光纤陀螺仪，具有工作带宽大、分辨率高、体积小，零点漂移小、线性度高、启
动时间短、抗冲击、成本低等特点，具备极低的零偏稳定性和角度随机游走以及强大的抗振能力。
陀螺精度
TLH-F50 型
TLH-F70 型
TLH-F98 型
各类高精度惯性测量单元 各类高精度惯性导航系统 各类高精度测量测绘系统 各类高精度姿态监测系统
角度随机游走系数
数据更新频率（默认）
0.3°/h
0.5°/h
0.3°/h
±500°/s
0.02°/√h
0.1°/h
0.2°/h
0.1°/h
±500°/s
0.009°/√h
0.07°/h
0.09°/h
0.07°/h
±500°/s
0.006°/√h
200Hz(可定制）
0.03°/h
0.05°/h
0.03°/h
±450°/s
0.003°/√h
0.01°/h
0.03°/h
0.01°/h
±300°/s
0.001°/√h
0.001°/h
0.004°/h
0.001°/h
±200°/s
0.0002°/√h
TLH-F50-3J TLH-F60-4J TLH-F70-5J TLH-F70-6J TLH-F98-7J TLH-F98-AJ
通讯接口
插件类型
供电电压
尺寸（mm）
重量（g）
功率谱密度4.2,20～2000（g,Hz）
RS422*1(数据线)；PPS*1(同步)；
DB15(主机线束，可定制)
40g,11ms,1/2Sine
±5V
2.5w
2.5w
2.5w
2.5w
5w
5w
光纤陀螺零偏稳定性精度可选范围为：0.5°~0.001°/h
控制更简单可靠
具备 RS422 数字接口输出，可根据用户需求进行定制
TLH-F50-3J TLH-F60-4J TLH-F70-5J TLH-F70-6J TLH-F98-7J TLH-F98-AJ
让导航更精准

### 其他信息

控制系统厂商G产品手册
CN-V3.0-25.11.18
控制系统厂商G Technology Co., Ltd
先进制造产业园A栋A2-301
Contents

---

## xCore_SDK_C++使用手册V3.0_A.pdf

### 产品概述

运行 RL 工程，等等。该使用说明书主要介绍编程接口库的使用方法，以及各接口函数的功能。用户可编写自己的
应用程序，集成到外部软硬件模块中。
⚫ 控制器版本：xCore v3.0.1 及以后。
本章介绍如何配置并运行一个 xCore SDK C++程序。
其他语言版本（Python、Java、C#）请参考分手册。

### 技术参数

如果只使用非实时控制，对于网络性能要求不高，可以通过无线连接。
运行 SDK 程序并连接到机器人之后，SDK 会在调用设置数据、执行操作等接口时打印日志到文件，包含调用参数
和返回结果等信息。可在遇到问题时将日志提供给协作机器人厂商H技术支持人员，以便分析排查。
简述 接口 参数 返回
连接机器人 connectToRobot()
断开连接 disconnectFromRobot()
查询机器人基本信息 robotInfo()  控制器版本，机型，轴数
机器人上下电急停状态 powerState()  on/off/Estop/Gstop
机器人上下电 setPowerState(state) state - on/off
置参数
获取当前关节角度 jointPos()  各轴角度 rad
获取当前关节速度 jointVel()  各轴速率 rad/s
获取关节力矩 jointTorque()  各轴力矩 Nm
速度覆盖值
查询基坐标系 baseFrame()  [ X, Y , Z, Rx, Ry, Rz ]
设置基坐标系 setBaseFrame(frame) frame – 坐标系
查询当前工具工件组 toolset()  末端坐标系, 参考坐标系, 负
设置工具工件组 setToolset(toolset)
setToolset(toolName, wobjName)
toolset – 工具工件组信息
toolName – 工具名字
wobjName – 工件名字
计算逆解 calcIk(posture)
calcIk(posture,toolset)
posture - 末端相对于外部参
toolset - 工具工件组信息
关节角度
计算正解 calcFk(joints)
calcFk(joints,toolset)
joints – 关节角度
toolset – 工具工件组信息
末端相对于外部参考坐标系
清除伺服报警 clearServoAlarm()
查询控制器日志 queryControllerLog(count, level) count - 查询个数
level - 日志等级
控制器日志列表
设置碰撞检测相关参数,
enableCollisionDetection
(sensitivity, behaviour, fallback)
sensitivity – 灵敏度
behaviour – 碰撞后行为
fallback – 回退距离/柔顺都
关闭碰撞检测功能 disableCollisionDetection()
坐标系标定 calibrateFrame(type, points,
is_held, base_aux)
type – 坐标系类型
points – 标定轴角度列表
is_held – 手持/外部工具工
base_aux – 基坐标系标定辅
获取当前软限位数值 getSoftLimit(limits) limits - 各轴软限位 已打开/已关闭
设置软限位 setSoftLimit(enable, limits) enable – 打开/关闭
limits -各轴软限位
恢复状态 recoverState(item) item - 恢复选项
设置导轨参数 setRailParameter(name, value) name – 参数名
value – 参数值
读取导轨参数 getRailParameter(name, value) name – 参数名
value – 参数值
简述 接口 参数 返回
设置运动控制模式 setMotionControlMode(mode) mode - NRT/RT/RL 工程
开始/继续运动 moveStart()
运动重置 moveReset()
暂停机器人运动 stop()
添加运动指令 moveAppend(command, id) command - 一条或多条
MoveL/MoveJ/MoveAbsJ/Mov
eC/MoveCF/MoveSP 指令
设置默认运动速度 setDefaultSpeed(speed) speed - 末端最大线速度
设置默认转弯区 setDefaultZone(zone) zone - 转弯区半径
threshold – 阈值参数
简述 接口 参数 返回
重新连接实时控制服务器 reconnectNetwork()
断开连接 disconnectNetwork()
设置周期调度 setControlLoop(callback,
priority, useStateDataInLoop)
设置限幅滤波参数 setFilterLimit(limit, frequency) limit – 是否开启限幅
frequency - 截止频率
设置笛卡尔空间运动区域 setCartesianLimit(length,
frame)
length - 区域长宽高
frame - 区域中心坐标系
设置关节阻抗系数 setJointImpedance(factor) factor – 各关节阻抗系数
设置笛卡尔空间阻抗控制系
setCartesianImpedance(factor) factor - 系数
设置碰撞检测阈值 setCollisionBehaviour(threshol
threshold – 各关节阈值
设置末端执行器位姿 setEndEffectorFrame(frame) frame - 末端相对于法兰的位
设置负载 setLoad(load) load - 负载信息
设置滤波截止频率 setFilterFrequency(joint, cart,
joint - 关节位置截止频率
cart - 笛卡尔空间位置截止频
torque - 关节力矩截止频率
设置笛卡尔空间阻抗控制末
setCartesianImpedanceDesired
torque - 末端期望力
设置滤波参数 setTorqueFilterCutoffFrequenc
frequency - 频率
设置力控坐标系 setFcCoor(frame, type) frame – 坐标系
type – 力控任务坐标系类别
发生错误后自动恢复机器人 automaticErrorRecovery()
设置网络延迟阈值 setNetworkTolerance(percent) percent – 阈值半分比
设置开始运动前的参数。所有参数都只用于实时模式运动，与非实时运动、通过 RobotAssist 操作的运动均不互相
简述 接口 参数 返回值
查询 DI 信号值 getDI(board, port) board - IO 板序号
设置 DI 信号值 setDI(board, port, state) board - IO 板序号
state - 信号值
查询 DO 信号值 getDO(board, port) board - IO 板序号
设置 DO 信号值 setDO(board, port, state) board - IO 板序号
state - 信号值
查询 AI 信号值 getAI(board, port) board - IO 板序号
设置 AO 信号 setAO(board, port, value) board - IO 板序号
value - 信号值
设置输入仿真模式 setSimulationMode(state) state – 打开/关闭
读取寄存器值 readRegister(name, index, value) name - 寄存器名称
value - 读取的数值
写入寄存器值 writeRegister(name, index, value) name - 寄存器名称
value - 写入的数值
设置 xPanel 对外供电模式 setxPanelV out(opt) opt – 模式
获取末端按键状态 getKeypadState()  末端按键的状态
末端工具 485 通信开关 setxPanelRS485(V opt,if_rs485) V opt  - 输出电压
if_rs485 - 是否打开 485 通信
485 通信读写寄存器 XPRWModbusRTUReg( slave_addr,
fun_cmd,  reg_addr data_type, num,
data_array, if_crc_reverse)
data_type - 数据类型
data_array - 数据数组
if_crc_reverse - 是否需要
485 通信读写线圈或离散输
XPRWModbusRTUCoil(slave_addr,
fun_cmd,  coil_addr, int num,
data_array, if_crc_reverse)
data_array  - 数据数组
if_crc_reverse - 是否需要
485 通信裸传数据 XPRS485SendData(send_byte,
rev_byte, send_data, rev_data,)
send_byte  - 发送数据长度
rev_byte - 接收数据长度
send_data - 发送数据
rev_data - 接收数据
控制器中需要有已创建好的 RL 工程，支持查询工程信息和运行。
简述 接口 参数 返回值
加载工程 loadProject(name, tasks) name - 工程名称
tasks – 任务列表
pp-to-main ppToMain()
暂停运行工程 pauseProject()
设置运行速率和循环模式 setProjectRunningOpt(rate,
rate – 运行速率
查询工具信息 toolsInfo()  工具名称, 位姿, 负载等信息
查询工件信息 wobjsInfo()  工件名称, 位姿, 负载等信息
简述 接口 参数 返回值
打开拖动 enableDrag(space, type,
enable_drag_button)
space – 拖动空间
type – 拖动类型
enable_drag_button – 无需按键
关闭拖动 disableDrag()
开始录制路径 startRecordPath(duration) duration – 录制时长
停止录制路径 stopRecordPath()
取消录制 cancelRecordPath()
保存路径 saveRecordPath(name, saveAs) name – 路径名称
saveAs – 重命名为
路径回放 replayPath(name, rate) name – 路径名称
rate – 回放速率
删除保存的路径 removePath(name, all) name – 路径名称
all – 是否删除所有路径
查询路径列表 queryPathLists()  路径名称列表
力传感器标定 calibrateForceSensor(all_axes,
axis_index)
all_axes – 标定所有轴
axis_index – 单轴标定下标
简述 接口 参数 返回值
获取当前力矩信息 getEndTorque(ref_type, joint,
external, cart_torque,
cart_force)
external -各轴外部力
cart_torque - 笛卡尔空间力矩
cart_force - 笛卡尔空间力
力控初始化 fcInit(frame_type) frame_type - 力控坐标系
开始力控 fcStart()
停止力控 fcStop()
设置阻抗控制类型 setControlType(type) type - 阻抗类型
常，并设置合理的力控保护参数
-28708 参数错误 重新设置数据
-28709 机器人处于碰撞停止 上电恢复碰撞状态
-28710 机器人处于急停状态 恢复急停
-28711 请求被拒绝 阻抗控制时多由于力控模型偏差，重新标定力矩传感器
并设置正确的负载
-41419 TCP 长度超限，力控初始化失败 末端工具长度限制为 0.3m
-41420 未进行力控初始化; 或未正确设置负载; 或力控模型偏差
- 标定零点、力矩传感器；
- 设置正确的负载质量和质心；
- 开启拖动时机器人没有收到外力
-41421 停止力控失败，当前不处于力控运行状态 机器人不处于力控状态
-41425 非阻抗控制模式，或搜索运动在运行中 - 保证当前处于阻抗模式下，且搜索运动处于停止状态
- 请检查参数设置
-41426 非阻抗控制模式，或搜索运动在运行中 - 保证当前处于阻抗模式下，且搜索运动处于停止状态
- 请检查参数设置
-41427 当前不处于笛卡尔阻抗控制模式或未设置搜索运动 检查控制模式指令，设置搜索运动参数后再尝试
-41428 当前不处于笛卡尔阻抗控制模式或未开始搜索运动 请保证搜索运动已开启且处于笛卡尔阻抗运行状态
-41429 当前未处于笛卡尔阻抗模式或搜索运动未暂停 暂停当前的力控任务并检查控制模式，切换到笛卡尔阻
抗控制模式后再尝试
-41430 不支持的阻抗控制类型或力控坐标系 停止当前的力控任务并重新参数初始化
-41431 当前未处于关节阻抗控制模式或未初始化 运行力控前设置轴空间阻抗控制模式
-41432 当前未处于笛卡尔阻抗控制模式或未初始化 运行力控前设置笛卡尔阻抗控制模式
-41433 当前未处于笛卡尔阻抗控制模式或未初始化 检查当前的阻抗控制模式后再进行尝试。确保力值输入
正确，且设定笛卡尔阻抗控制模式
-41434 关节期望力超过限制 检查当前的阻抗控制模式后再进行尝试。确保期望力值
输入正确，且设定轴空间阻抗控制模式
-41435 笛卡尔空间期望力超过限制 检查当前的阻抗控制模式后再进行尝试。确保期望力值
输入正确，且设定笛卡尔阻抗控制模式
-41442 机器人不满足软限位要求，开启力控失败 请确认机器人开启阻抗时机器人在软限位内
-41444 阻抗刚度设置失败，数值不合理或当前状态不能设置刚
请重新设置阻抗刚度数值在合理范围内
数等参数
- 如果当前机型为三轴或者四轴机器人 ,请检查输入位
-50512 轴数不匹配 轴空间 Jog 的下标参数不能超出轴数+外部轴数
-50513 速度设置无效，机器人无法运动 传入 0.01~1 范围内的速度参数
-50514 步长设置无效，机器人无法运动 传入大于 0 的步长参数
-50515 参考坐标系设置无效，机器人无法运动 传入支持的坐标系类型参数
-50516 运动轴设置无效，机器人无法运动 按照说明传入 index 参数
-50519 生成轨迹失败, 目标点位可能超出机器人工作范围 请在机器人正常工作范围内，重新示教点位
-50525 该机型不支持奇异规避模式运动 , 或机器人锁轴失败 , 4
轴角度不为 0 不运行运动, 请调整 4 轴角度
调整四轴角度至 0 或者正负 180 度
-60014 控制器当前状态不允许开始运动 确保机器人上电并处于空闲中
-60200 负载信息错误, 设置失败 - 负载信息错误 ,请检查负载重量是否超过额定负载，
质心不超过 0.3m
258 参数错误,数值超出范围 按照函数说明检查参数数值范围
259 参数错误,参数类型或个数错误 按照函数说明检查参数类型或数组长度
260 不是合法的变换矩阵 检查传入参数是否符合其次变换矩阵要求
261 数组元素个数与机器人轴数不符 传入和机器人轴数一致的数组长度
262 运动控制模式错误,请切换到正确的模式 根据实际情况调用 setMotionControlMode 切换模式
263 超时前未收到机器人回复, 可能由于网络通信问题 检查网络连接状态，或反馈技术支持人员
位姿初始化接收 6 或 16 个参数 初始化 trans&rpy 应传入长度为 6 的数组；初始化 pos（实时
xMate 模型库暂不支持的机型 请参考 xMateModel 类注释，查看支持的机型
已经开始运动, 请勿重复调用 同时只允许一个运动回调运行，调用 stopMove 之后再开始下
未调用开始运动 先调用 startMove，再调用 startLoop
用户下发的运动指令需要满足建议条件和必要条件。建议条件是为了让机器人运动更加平稳，性能最优。必要条
件则是必须满足的，若不满足，机器人将会停止。
轴空间轨迹平滑，至少保证速度是连续可导的：
qmin < qc < qmax
−q̇ max < q̇ c < q̇ max
−q̈ max < q̈ c < q̈ max
−q⃛max < q⃛c < q⃛max
−τjmax < τjc < τjmax
−τ̇ jmax < τ̇ jc < τ̇ jmax
−ṗ max < ṗ c < ṗ max
−p̈ max < p̈ c < p̈ max
−p⃛max < p⃛c < p⃛max
−τjmax < τjc < τjmax
−τ̇ jmax < τ̇ jc < τ̇ jmax
−τ̇ jmax < τ̇ jc < τ̇ jmax
−τjmax < τjc < τjmax
xMateER3 Pro、xMateER7 Pro、xMateER3、xMateER7 笛卡尔空间运动限制条件：
参数 平移 旋转
速度 1.0 m/s 2.5 rad/s
加速度 10.0 m/s2 10.0 rad/s2
加加速度 5000.0 m/s3 5000.0 rad/s3
xMateER3 Pro 和 xMateER7 Pro 轴空间运动限制条件：
参数 一轴 二轴 三轴 四轴 五轴 六轴 七轴 单位
速度上限 2.175 2.175 2.175 2.175 2.610 2.610 2.610 rad/s
加速度上限 15 7.5 10 10 15 15 20 rad/s2
加加速度上限 5000 3500 5000 5000 7500 7500 7500 rad/s3
xMate3 和 xMate7 轴空间运动限制条件：
参数 一轴 二轴 三轴 四轴 五轴 六轴 单位
速度上限 2.175 2.175 2.175 2.610 2.610 2.610 rad/s
加速度上限 15 7.5 10 15 15 20 rad/s2
加加速度上限 5000 3500 5000 7500 7500 7500 rad/s3
xMateER3 Pro 和 xMateER7 Pro 直接力矩控制限制条件
参数 一轴 二轴 三轴 四轴 五轴 六轴 七轴 单位
力矩上限 85 85 85 85 36 36 36 Nm
力矩微分上限 1500 1500 1500 1500 1000 1000 1000 Nm/s
xMate3 和 xMate7 直接力矩控制限制条件
参数 一轴 二轴 三轴 四轴 五轴 六轴 单位
力矩上限 85 85 85 36 36 36 Nm
力矩微分上限 1500 1500 1500 1000 1000 1000 Nm/s
xMateER3 Pro DH 参数表：
Joint A(mm) Alpha(rad) D(mm) Theta(rad)
xMateER7 Pro DH 参数表：
Joint A(mm) Alpha(rad) D(mm) Theta(rad)
xMate3 DH 参数表：
Joint A(mm) Alpha(rad) D(mm) Theta(rad)
xMate7 DH 参数表：
Joint A(mm) Alpha(rad) D(mm) Theta(rad)
实时运动指令和状态信息都通过 UDP 协议单播发送。如果出现“超时前未收到机器人状态反馈”的实时状态异常，
Windows 系统请检查防火墙设置，UDP 入站规则是否是允许的状态。
等问题，可能是由于力控模型不准的原因。首先需要确认 每项力控参数是否准确；其次可以根据实机情况调整发
// 读整个数组，赋值给val_af, val_af 的长度也变为10。此时index 参数是多少都无所谓
robot->readRegister("register0", 9, val_af, ec);
// 读取int 类型寄存器数组
std::vector<int> val_ai;
robot->readRegister("register1", 1, val_ai, ec);
// 写入bool/bit 类型寄存器
robot->writeRegister("register2", 0, true, ec);
// 打开关闭导轨，设置导轨参数
// 设置导轨参数和基坐标系需要重启控制器生效, 这里仅展示接口调用方法
robot->setRailParameter("enable", true, ec); // 打开导轨功能
robot->setRailParameter("maxSpeed", 1, ec); // 设置最大速度1m/s
robot->setRailParameter("softLimit", std::vector<double>({-0.8, 0.8}), ec); // 设置软限位为
+-0.8m
robot->setRailParameter("reductionRatio", 1.0, ec); // 设置减速比
auto curr = robot->BaseRobot::jointPos(ec);
print(os, "当前轴角度", robot->BaseRobot::jointPos(ec));
参数 [out] ec 错误码
template<WorkType Wt, unsigned short DoF>
void rokae::Robot_T< Wt, DoF >::connectToRobot  (const std::string &remoteIP,
const std::string &localIP = "" )
连接到机器人
disconnectFromRobot()
void rokae::BaseRobot::disconnectFromRobot (error_code & ec)
断开与机器人连接。断开前会停止机器人运动, 请注意安全
参数 [out] ec 错误码
Info rokae::BaseRobot::robotInfo (error_code &ec ) const
查询机器人基本信息
参数 [out] ec 错误码
返回 机器人基本信息：控制器版本，机型，轴数
powerState()
PowerState rokae::BaseRobot::powerState(error_code &ec ) const
机器人上下电以及急停状态
参数 [out] ec 错误码
返回 on-上电 | off-下电 | estop-急停 | gstop-安全门打开
setPowerState()
void rokae::BaseRobot::setPowerState (bool on,
机器人上下电。注: 只有无外接使能开关或示教器的机器人才能手动模式上电。
参数 [in] on true-上电 | false-下电
operateMode()
OperateMode rokae::BaseRobot::operateMode (error_code & ec) const
参数 [out] ec 错误码
setOperateMode()
void rokae::BaseRobot::setOperateMode ( OperateMode  mode,
参数 [in] mode 手动/自动
operationState()
OperationState rokae::BaseRobot::operationState ( error_code & ec ) const
查询机器人当前运行状态 (空闲,运动中, 拖动开启等)
参数 [out] ec 错误码
返回 运行状态枚举类
posture()
std::array< double, 6 > rokae::BaseRobot::posture(CoordinateType ct, error_code & ec )
获取机器人法兰或末端的当前位姿
参数 [in] ct 坐标系类型
1) flangeInBase: 法兰相对于基坐标系;
2) endInRef: 末端相对于外部参考坐标系。例如,当设置了手持工具及外部工件后，该坐标系类型
cartPosture()
CartesianPosition rokae::BaseRobot::cartPosture(CoordinateType ct, error_code & ec )
获取机器人法兰或末端的当前位姿
参数 [in] ct 坐标系类型
jointPos() [1/2]
template<WorkType Wt, unsigned short DoF>
std::array< double, DoF > rokae::Robot_T< Wt, DoF >::jointPos ( error_code &  ec )
机器人当前轴角度, 单位: 弧度
参数 [out] ec 错误码
返回 轴角度值
jointPos() [2/2]
std::vector<double> rokae::BaseRobot::jointPos (error_code & ec)
机器人当前轴角度, 机器人本体+外部轴, 单位: 弧度, 外部轴导轨单位米
参数 [out] ec 错误码
返回 关节角度值，和外部轴值
jointVel() [1/2]
template<WorkType Wt, unsigned short DoF>
std::array< double, DoF > rokae::Robot_T< Wt, DoF >::jointV el ( error_code &  ec )
机器人当前关节速度，单位：弧度/秒
参数 [out] ec 错误码
返回 关节速度
jointVel() [2/2]
std::vector<double> rokae:: BaseRobot::jointVel (error_code &  ec)
机器人当前关节速度, 机器人本体+外部轴，单位：弧度/秒,外部轴单位米/秒
参数 [out] ec 错误码
返回 关节速度
参数 [out] ec 错误码
template<WorkType Wt, unsigned short DoF>
std::array< double, DoF > rokae::Robot_T< Wt, DoF >::jointTorque ( error_code &ec )
关节力传感器数值，单位: Nm
参数 [out] ec 错误码
baseFrame()
std::array< double, 6 > rokae::BaseRobot::baseFrame ( error_code &ec ) const
参数 [out] ec 错误码
setBaseFrame()
void rokae::BaseRobot::setBaseFrame(const Frame &frame, error_code &ec)
设置基坐标系, 设置后仅保存数值，重启控制器后生效
参数 [in]  frame 坐标系，默认使用自定义安装方式
toolset()
Toolset rokae:: BaseRobot::toolset ( std::error_code & ec ) const
参数 [out] ec 错误码
返回 见 Toolset 数据结构
setToolset()
void rokae:: BaseRobot::setToolset ( const Toolset & toolset,
参数 [in] toolset 工具工件组信息
setToolset()
void rokae:: BaseRobot::setToolset (const std::string &toolName, const std::string &wobjName,
参数 [in] toolName  工具名称
[in] wobjName 工件名称
calcIk() [1/2]
template<unsigned short DoF>
JointArray rokae::Model_T< DoF >::calcIk (CartesianPosition  posture,
参数 [in] posture 机器人末端位姿，相对于外部参考坐标系
返回 轴角度, 单位:弧度
calcIk() [2/2]
template<unsigned short DoF>
JointArray rokae::Model_T< DoF >::calcIk (CartesianPosition  posture, const Toolset & toolset
参数 [in] posture 机器人末端位姿，相对于外部参考坐标系
[in] toolset 工具工件组信息
返回 轴角度, 单位:弧度
calcFk()
template<unsigned short DoF>
CartesianPosition rokae::Model_T< DoF >::calcFk ( const JointArray &  joints,
根据轴角度计算正解
参数 [in] joints 轴角度, 单位: 弧度
返回 机器人末端位姿，相对于外部参考坐标系
calcFk()
template<unsigned short DoF>
CartesianPosition rokae::Model_T< DoF >::calcFk ( const JointArray &  joints, const Toolset & toolset
根据轴角度计算给定工具工件坐标系下正解
参数 [in] joints 轴角度, 单位: 弧度
[in] toolset 工具工件组信息
返回 机器人末端位姿，相对于外部参考坐标系
setToolset()
void rokae:: BaseRobot::setToolset (const std::string &toolName, const std::string &wobjName,
参数 [in] toolName  工具名称
[in] wobjName 工件名称
calibrateFrame ()
template<WorkType Wt, unsigned short DoF>
FrameCalibrationResult rokae::Robot_T< Wt, DoF >::calibrateFrame  (  FrameType   type,
const std::vector< std::array< double, DoF > > &points,
bool is_held,
const std::array< double, 3 > &   base_aux = {} )
注解 各坐标系类型支持的标定方法及注意事项：
3) 基坐标系: 六点标定。标定前请确保动力学约束和前馈已关闭。 若标定成功(无错误码)，控制器
会自动保存标定结果，重启控制器后生效。
4) 导轨基坐标系: 三点标定。若标定成功(无错误码)，控制器会自动保存标定结果，重启控制器后
参数 [in] points 轴角度列表，列表长度为 N。例如，使用三点法标定工具坐标系，应传入 3 组轴角
度。轴角度的单位是弧度。
[in] is_held true - 机器人手持 | false - 外部。仅影响工具/工件的标定
[in] base_aux 基坐标系标定时用到的辅助点, 单位[米]
clearServoAlarm()
void rokae::BaseRobot::clearServoAlarm ( error_code & ec )
清除伺服报警
参数 [out] ec 错误码，当有伺服报警且清除失败的情况下错误码置为-1
enableCollisionDetection()
template<unsigned short DoF>
void Cobot<DoF>::enableCollisionDetection(const std::array<double, DoF> sensitivity,
StopLevel behaviour,
double fallback_compliance,
设置碰撞检测相关参数, 打开碰撞检测功能
参数 [in] sensitivity 碰撞检测灵敏度，范围 0.01-2.0
[in] behaviour 碰撞后机器人行为, 支持 stop1(安全停止, stop0 和 stop1 处理方式相同)和 stop2(触发暂
停）, suppleStop(柔顺停止)
[in] fallback_compliance 1) 碰撞后行为是安全停止或触发暂停时，该参数含义是碰撞后回退距
离，单位: 米 2) 碰撞后行为是柔顺停止时，该参数含义是柔顺度，范围 [0.0, 1.0]
disableCollisionDetection()
void BaseCobot::disableCollisionDetection(error_code &ec)
参数 [out] ec 错误码
getSoftLimit()
template<WorkType Wt, unsigned short DoF>
bool rokae::Robot_T< Wt, DoF >::getSoftLimit ( std::array< double[2], DoF > &limits,
参数 [out] limits 各轴软限位 [下限, 上限]，单位: 弧度
返回 true - 已打开 | false - 已关闭
setSoftLimit()
template<WorkType Wt, unsigned short DoF>
void rokae::Robot_T< Wt, DoF >::setSoftLimit  ( bool enable,
const std::array< double[2], DoF > &   limits = {{DBL_MAX, DBL_MAX}} )
设置软限位。软限位设定要求： 1) 打开软限位时，机械臂应下电且处于手动模式; 2) 软限位不能超过机械硬限位
3) 机械臂当前各轴角度应在设定的限位范围内
参数 [in] enable true - 打开 | false - 关闭。
[in] limits 各轴[下限, 上限]，单位：弧度。 1) 当 limits 为默认值时，视为仅打开软限位不修改数
queryControllerLog()
std::vector< LogInfo > rokae::BaseRobot::queryControllerLog ( unsigned  count,
const std::set< LogInfo::Level > &  level,
查询控制器最新的日志
参数 [in]    count 查询个数，上限是 10 条
[in] level 指定日志等级，空集合代表不指定
recoverState()
void rokae::BaseRobot::recoverState(int item, error_code &ec)
根据选项恢复机器人状态
参数 [in]    item  恢复选项，1：急停恢复
setRailParameter()
template<typename R>
void rokae::setRailParameter(const std::string &name, R value, error_code &ec)
设置导轨参数
模板参数 参数类型
参数 [in]  name 参数名，见 value 说明
[in] value
参数                      |    参数名                      |   数据类型
开关                      | enable                          | bool
基坐标系             | baseFrame                 | Frame
导轨名称             |  name                          | std::string
编码器分辨率    | encoderResolution | int
减速比                                     | reductionRatio    | double
电机最大转速(rpm)            | motorSpeed         | int
软限位(m), [下限,上限]     | softLimit                | std::vector<double>
运动范围(m), [下限,上限] | range                      | std::vector<double>
最大速度(m/s)                     | maxSpeed            | double
最大加速度（m/s^2)         | maxAcc                 | double
最大加加速度(m/s^3)       | maxJerk                | double
getRailParameter()
template<typename R>
void rokae::getRailParameter (const std::string &name, R &value, error_code &ec)
读取导轨参数
模板参数 参数类型
参数 [in]   name 参数名，见setRailParameter()
[out] value  参数数值，见 setRailParameter()
[out] ec 错误码，参数名不存在或数据类型不匹配返回错误码
configNtp()

### 使用说明

使用手册
xCore SDK(C++)使用手册
[类别]
感谢您购买本公司的机器人系统。
本手册记载了正确安装使用机器人的以下说明：
⚫ 机器人二次开发接口 SDK(C++)的使用。
安装使用该机器人系统前，请仔细阅读本手册与其他相关手册。
⚫ 机器人应用开发工程师。
请务必保证以上人员具备基础的机器人操作、C++编程等所需的知识，并已接受本公司的相关培训。
本手册包含单独的安全章节，必须在阅读安全章节后，才能进行安装或维护作业。
V1.5 2022.6 初始版本；
xCore 系统的机器人进行一系列控制和操作，包括实时和非实时的运动控制，机器人通信相关的读写操作，查询及
操作系统 编译器 平台 语言
Ubuntu 18.04/20.04/22.04 build-essential x86_64
aarch64
C++, Python
Windows 10 MSVC 14.1+ x86_64 C++, Python, C#
Android  armeabi-v7a，
arm64-v8a，
Java
xCore SDK 提供对机器人的非实时控制，主要通过给机器人发送运动指令，使用控制器内部的轨迹规划，完成路径
规划和运动执行。非实时模式提供的操作有：
⚫ 运动：轴空间运动（MoveAbsJ, MoveJ）, 笛卡尔空间运动（MoveL, MoveC, MoveCF, MoveSP ）,支持导轨联
动。及可达性校验，设置加速度等
⚫ 机器人通信: 数字量和模拟量 I/O，寄存器读写，XMS 和 XMC 机型末端 485 通信
⚫ 拖动与路径回放（只针对 xMate 协作机器人）
⚫ 其他操作：Jog，设置碰撞检测，软限位，清除报警，查询控制器日志等等
xCore SDK 的实时控制包含了一系列底层控制接口，科研或二次开发用户可以使用该软件包实现最高达 1KHz 的实
时控制，用于算法验证以及新应用的开发。
xMate 协作机器人支持 5 种控制模式：
⚫ 轴空间位置控制
⚫ 笛卡尔空间位置控制
⚫ 轴空间阻抗控制
⚫ 笛卡尔空间阻抗控制
⚫ 直接力矩控制
6 轴工业机器人支持 2 种位置控制模式：
⚫ 轴空间位置控制
⚫ 笛卡尔空间位置控制
关于机器人本体和控制柜等硬件的设置，请参考《 xCore 控制系统使用手册 V3.0.1》。除 了网络配置外，使用
xCore SDK 通过以太网（TCP/IP）连接机器人。通过有线或无线连接皆可，使用户 PC 和机器人连接同一局域网。
使用实时控制的话推荐通过有线直连到机器人。机器人配置有 2 个网口，一个是外网口，一个是直连网口。直连网
⚫ 连接方式 1：机器人与用户 PC 采用网线直连的方式连接。如果用户工控机与机器人不处于同一个网段，需
⚫ 连接方式 2：机器人外网口连接路由器或者交换机，用户 PC 也连接路由器或者交换机，两者处于同一局域
注：推荐使用方式 1 进行连接，连接方式 2 网络通信质量差时可能会造成机器人运动不稳定现象。
├── doc: 文档和使用手册
└── lib: 各操作系统和架构的库文件
xCore SDK 版本使用 CMake 构建工程，CMake 版本不低于 3.12。
Linux
以编译示例程序 sdk_example 为例，设置安装路径为根目录下 out:
cmake .. -DCMAKE_INSTALL_PREFIX=../out
cmake --build . --target install
Windows
1. 下载并安装 Microsoft Visual Studio 2017 或以后版本，选择安装“使用 C++的桌面应用”。
2. 打开 CMake 工程，选择根目录下的 CMakeLists.txt
1. 下载并安装 Qt 5.15.2 或以后版本，并将编译器勾选为 MSVC2019 编译器；
4. 进入配置文件（.pro 文件），输入以下配置语句：
DEFINES += _USE_MATH_DEFINES
#Eigen 配置
INCLUDEPATH += <path-to-external-directory>
_log_storage_directory_ 为用户指定的日志存储目录路径，替换默认日志存储目录  _rokae_log_，建议使用相对路径
的方式写入；_retention_days_ 为日志保留天数。
目前也提供了全局日志，全局日志的输出位置固定在运行程序所在目录下名为 logs 的文件夹，最多保留 7 天的全局
实时模式接收状态数据默认的等待超时时间是 1ms，根据现场实际的网络情况，可以在可执行文件同目录下，增加
配置文件（xcoresdk_config.json）来设置超时时间，以适应实际情况和优化实时效果 。若设备网络情况较好，并出
现控制一段时间后，发送的运动指令有延迟执行的现象，可适当将超时时间调大，设置范围为 1~4ms，具体的 json
安装实时内核。
1. 安装依赖
apt-get install build-essential bc curl ca-certificates fakeroot gnupg2 libssl-dev lsb-release libelf-dev bison flex cmake
libeigen3-dev
通过 uname -r 命令可以知道本机正在使用的内核；
$ xz -d linux-4.14.12.tar.xz
$ xz -d patch-4.14.12-rt10.patch.xz
检查 sign 文件完整性
$ gpg2 --verify linux-4.14.12.tar.sign
会得到类似于如下的信息：
$ gpg2 --verify linux-4.14.12.tar.sign gpg: assuming signed data in 'linux-4.14.12.tar
gpg: Signature made Fr 05 Jan 2018 06:49:11 PST using RSA key ID 6092693E
gpg: Can't check signature: No public key
$ gpg2 --keyserver hkp://keys.gnupg.net --recv-keys 0x6092693E
同理对于 patch 文件，执行相同的操作。
下载完成 server key 后再次验证，若得到如下信息就说明是正确的。
$ gpg2 --verify linux-4.14.12.tar.sign
gpg: assuming signed data in 'linux-4.14.12.tar'
gpg: Signature made Fr 05 Jan 2018 06:49:11 PST using RSA key ID 6092693E
gpg: aka "Greg Kroah-Hartman (Linux kernel stable release signing key)
gpg: WARNING: This key is not certified with a trusted signature!
gpg: There is no indication that the signature belongs to the owner. Primary key
fingerprint: 647F 2865 4894 E3BD 4571 99BE 38DB BDC8 6092 693E
同理验证一下 patch 文件。
$ tar xf linux-4.14.12.tar
$ cd linux-4.14.12
$ patch -p1 < ../patch-4.14.12-rt10.patch
配置内核：
$ make oldconfig
1. No Forced Preemption (Server) (PREEMPT_NONE)
2. Voluntary Kernel Preemption (Desktop) (PREEMPT_VOLUNTARY)
3. Preemptible Kernel (Low-Latency Desktop) (PREEMPT__LL) (NEW)
4. Preemptible Kernel (Basic RT) (PREEMPT_RTB) (NEW)
> 5. Fully Preemptible Kernel (RT) (PREEMPT_RT_FULL) (NEW)
$ fakeroot make -j4 deb-pkg
dpkg 安装：
$ sudo dpkg -i ../linux-headers-4.14.12-rt10_*.deb ../linux-image-4.14.12-rt10_*.deb
4. 验证是否安装成功
重启一下，进 ubuntu 高级选项，可以看到你安装的内核。选择新安装的内核进入后，通过 uname -r 查看对应内核
版本，如果版本正确，/sys/kernel/realtime 里内容是 1。
rokae::Robot 基本操作 全部支持 全部支持 全部支持
Jog 机器人 全部支持 全部支持 全部支持
通信 全部支持 全部支持 全部支持
rokae::Model 运动学计算 全部支持 全部支持 全部支持
rokae::ForceControl 力控指令 全部支持 全部支持 全部支持
rokae::RtMotionControl 实时模式 全部支持 不支持 不支持
rokae::Planner 上位机路径规划 全部支持 不支持 不支持
rokae::xMateModel 运动学和动力学计算 全部支持 不支持 不支持
查询当前操作模式 operateMode()  auto/manual
切换手自动模式 setOperateMode(mode) mode - auto/manual
查询机器人运行状态 operationState()  idle/jog/RLprogram/moving 等
获取当前末端/法兰位姿 posture(ct) ct – 坐标系类型 [ X, Y, Z, Rx, Ry, Rz ]
获取当前末端/法兰位姿 cartPosture(ct) ct – 坐标系类型 [ X, Y, Z, Rx, Ry, Rz ] 及轴配
配置NTP configNtp(server_ip) server_ip - NTP 服务端 IP
手动同步一次NTP 时间 syncTimeWithServer()
设置是否使用 conf setDefaultConfOpt(forced) forced – 是/否使用
设置最大缓存指令个数 setMaxCacheSize(number) number – 个数
开始 Jog 机器人 startJog(space, rate, step, index,
space - 参考坐标系
rate - 速率
step - 步长
index - XYZABC/J1-7
动态调整机器人运动速率 adjustSpeedOnline(scale) scale – 速率
切换使用 RCI 客户端 useGen1RciClient(use) use – 是否切换
简述 类
S 速度规划的笛卡尔空间运动 CartMotionGenerator
S 速度规划的轴空间运动 JointMotionGenerator
点位跟随, 点位可以是笛卡尔位姿或轴角度 FollowPosition
使用运动学与动力学计算库需要在编译时加上下列选项：
cmake .. -DXCORE_USE_XMATE_MODEL=ON
具体使用方法参见 SDK 中 planner.h 文件。
设置力控模块使用的负载 setLoad(load) load - 负载
设置关节阻抗刚度 setJointStiffness(stiffness) stiffness - 刚度
设置笛卡尔阻抗刚度 setCartesianStiffness(stiffness) stiffness - 刚度
设置笛卡尔零空间阻抗刚度 setCartesianNullspaceStiffness(s
tiffness)
stiffness - 刚度
设置关节期望力矩 setJointDesiredTorque(torque) torque - 力矩值
设置笛卡尔期望力/力矩 setCartesianDesiredForce
(value)
value -期望力/力矩
setSineOverlay(line_dir,
amplify, frequency, phase, bias)
amplify -幅值
frequency - 频率
phase - 相位
bias - 偏置
设置平面内的莉萨如搜索运动 setLissajousOverlay (int plane,
double amplify_one, double
amplify_two,
frequency_two, double
phase_diff, error_code &ec)
plane - 参考平面
amplify_one - 一方向幅值
frequency_one - 一方向频率
amplify_two - 二方向幅值
frequency_two - 二方向频率
phase_diff 相位偏差
开启搜索运动 startOverlay()
停止搜索运动 stopOverlay()
暂停搜索运动 pauseOverlay()
重新开启暂停的搜索运动 restartOverlay()
设置与接触力有关的终止条件 setForceCondition (range,
isInside, timeout)
range - 力限制
isInside - 超出/符合限制条件
setTorqueCondition (range,
isInside, timeout)
range - 力矩限制
isInside - 超出/符合限制条件
setPoseBoxCondition(supervisin
g_frame, box, isInside, timeout)
supervising_frame - 长方体所
isInside - 超出/符合限制条件
激活设置的终止条件并等待 waitCondition()
启动/关闭力控模块保护监控 fcMonitor(enable) enable - 打开|关闭
设置力控模式下的轴最大速度 setJointMaxV el(velocity) velocity – 轴速度
设置机械臂末端相对基坐标系
的最大速度
setCartesianMaxV el(velocity) velocity – 末端速度
设置力控模式下轴最大动量 setJointMaxMomentum(momen
设置力控模式下轴最大动能 setJointMaxEnergy(energy) energy - 动能
非 实 时 接 口 的 调 用 结 果 通 过 错 误 码 反 馈 ， 每 个 接 口 都 会 传 入 一 个std::error_code 类 型 的 参 数 ， 可 通 过
error_code::message()来获取错误码对应的信息。
数值 错误信息 原因及处理方法
0 操作成功完成 无
-3 机器人急停按钮被按下, 请先恢复 恢复急停状态
-16 该操作不允许在当前模式下执行 (手动/自动), 请切换到
-17 该操作不允许在当前上下电状态下执行 切换上下电状态
-18 该操作不允许在机器人当前运行状态下执行 机器人非空闲，可能处于拖动/实时模式控制/辨识中等
-19 该操作不允许在当前控制模式(位置/力控)下执行 切换位置控制/力控
-20 机器人运动中 停止机器人运动
-34 逆解超出机器人软限位 检查软限位设置时候合适，传入限位内位姿
-38 配置数据 cfx 错误逆解无解 检查 conf data
-41 算法失效，无法计算逆解 可能由于控制器计算问题，请反馈技术支持人员
-257 通信协议解析失败 请反馈技术支持人员
-513 切换手动/自动操作模式失败 - 停止机器人运动
- 清除伺服报警
-515 打开/关闭拖动失败, 请检查机器人是否处于下电 机器人手动模式下电时打开拖动
-10005 标定中, 或标定时重置负载失败 - 等待标定完成
- 正确设置负载
-10030 未打开仿真模式或信号不存在 打开仿真模式后再设置 DI/AI
-10040 开始拖动失败,正确设置负载并标定力矩传感器 正确地设置工具负载质量和质心；设置完成后执行力矩
传感器标定
-10065 同步 NTP 时间失败 - 安装好 NTP 功能
-10079 力控模块处于错误状态 触发了力控保护，请检查力控模式下机器人状态是否正
-10141 负载质量超过了机器人额定负载 使用并设置额定负载范围内的负载
- 使用其它信号
- 用匹配的数据类型读取
- 或用匹配的数据类型写入
-17320 执行过 RL 程序, 需要重置运动缓存后再开始运动 调用 moveReset 重置
-28688 切换运动控制模式失败 - 停止机器人运动
- 重启控制器
-28689 该频率不支持 状态数据发送频率支持 1kHZ, 500Hz, 250Hz, 125Hz
-28706 无法执行该操作，可能由于机器人未处于空闲状态 停止机器人运动
-28707 起始位置为奇异点 运动机器人到非奇异点
-41459 处于力控模式，不允许执行的操作 停止力控后再回放路径
-50001 控制器状态错误，无法生成轨迹 调用 moveReset()重置
- 用关节方式移动机器人
- 检查 confdata 配置
-50019 生成轨迹失败 重新调整目标点的位置、姿态和臂角(仅 7 轴机器人需要
confData
- 调用 setDefaultConfOpt(false) 取消 confdata
- 重新示教点位，传入正确的 confdata
-50033 机器人处于锁轴状态，目标点锁轴角度发生了偏离，请
-50101 轴角度超出运动范围 , 尝试取消软限位后恢复各轴到允
- 手动将机器人各轴移动到正常的工作范围内
- 将笛卡尔空间运动指令改为关节空间运动指令
-50103 笛卡尔路径终点不符合给定的 ConfData - 调用 setDefaultConfOpt(false)不使用 confdata
- 改为 MoveJ 或 MoveAbsJ
- 更改目标点 confdata
-50104 关节力矩超限 - 检查负载数值是否符合实际负载情况
- 检查机器人摩擦力系数、电机过载系数、传动过载系
- 如果使用了 setAvoidSingularity(lock4axis)，请检查目
-50113 改变的姿态超过设定的阈值 - 请规避奇异点
- 重新设置奇异规避姿态改变的阈值
- 使用其他方式的奇异规避
- 手动将机器人各轴移动到正常的工作范围内
- 更换 Jog 方式，尝试轴空间 Jog
- 将笛卡尔空间运动指令改为关节空间运动指令
-50118 改变姿态后求解的终点与所需要终点不一致 - 请规避奇异点
-50120 奇异规避下搜索路径终点角度失败 - 请规避奇异点
-50121 奇异规避下搜索路径终点角度失败 - 请规避奇异点
- 尝试更改指令形式，例如 MoveL 改为 MoveJ
-50208 内部轨迹错误 - 请调用 moveReset()重置运动指令缓存
-50401 检测到碰撞 - 请检查机器人运行环境，确认人员、设备安全后，重
-60511 路径不存在 使用已保存的回放路径
-60702 当前四轴角度不为 0, 不允许切换到四轴固定模式, 或机
请检查第四轴当前角度是否为 0°或 180°
-60704 不满足牺牲姿态奇异规避的开启条件 请检查当前状态是否满足牺牲姿态奇异规避开启状态
264 重复操作 碰撞检测已打开，需要先关闭
265 通过 UDP 端口接收数据失败，请检查网络及防火墙配
- 检查防火墙设置，是否允许 UDP 连接
266 客户端校验失败，请检查控制器版本，授权状态和机器
- 按照手册或 README 将控制器升级到匹配版本
- 创建类型匹配的机器人实例
273 点位距离过近，坐标系标定失败 参考《xCore 控制系统使用手册》工具工件标定方法，
513 设置了不支持的字段, 或总长度超出限制 支持的字段见 RtSupportedFields，总长度限制为 1024 字
768 没有可执行的运动指令 先调用 moveAppend 下发运动指令，再开始运动
769 机器人停止中或当前状态无法暂停 可能由于调用 stop()前刚刚手动模式下电，或者按下急
停，控制器正在响应停止中，请等待
实 时 模 式 下 发 送 运 动 指 令 、 周 期 调 度 、 读 取 状 态 数 据 等 接 口 在 调 用 过 程 中 会 抛 出 异 常 ， 异 常 类 型 见
rokae/exception.h。
异常信息 原因及处理方法
运动控制模式错误, 非实时模式 - 调用 setMotionControlMode(RtCommand)切换模式
- 前一次阻抗控制发生错误，控制器切回到非实时模式，需
创建实时控制客户端失败 网络连接错误，检查工控机运行状态
控制器无法设置发送的状态数据 可能由于版本不匹配，请反馈技术支持人员
设置控制指令失败  可能由于版本不匹配，请反馈技术支持人员
控制器无法发送机器人状态信息. 控制器 UDP 端口设置出错，请反馈技术支持人员查看控制器
未开始接收数据 调用 startReceiveRobotState 开始接收数据
- 检查防火墙设置，是否允许 UDP 连接
接收机器人状态数据错误  状态数据解析失败，可能由于版本不匹配，请反馈技术支持
xCore 最低版本要求 按照提示信息升级控制器版本
开始运动失败  - 确保机器人空闲，未处于急停等非正常使用的状态
- 多出现于阻抗控制，请标定零点、力矩传感器，并正确设
置负载后再次尝试
工业机型仅支持位置控制 工业机型使用位置控制
起点和终点的臂角格式不一样 笛卡尔指令 hasElbow 值不一致
指令和控制模式不一致 回 调 函 数 返 回 的 数 据 类 型(JointPosition/ CartesianPosition/
Torque) 应和控制类型匹配
未初始化 FollowPosition 默认构造需要调用 init()函数之后在使用
目前如果使用 xCore SDK 控制机器人，并不会限制通过 RobotAssist 的控制。机器人的一些状态，通过 xCore SDK
更改后也会体现在 Robot Assist 界面上；一些工程运行，运动控制则是分离的。大致总结如下：
会同步更新的组件 ⚫ 底部状态栏：手自动，机器人状态，上下电；
RobotAssist 修改会
⚫ 工具工件组: 更改 RobotAssist 右上角选择的工具工件会改变 toolset；通过 setToolset()
设置了工具工件，右上角会显示”toolx”, “wobjx”
⚫ 下发的运动指令无法通过点击开始按钮让机器人开始执行；
⚫ 大部分机器人设置界面显示的功能打开状态和设定值等；
建议的控制方式是单一控制源，避免混淆。
对于原 RCI 客户端的用户，可以在控制器升级到 v3.0.1（v1.7 及之后的版本也同样可以）之后直接使用 xCoreSDK。
1. 确保 RobotAssist – 通信 – RCI 设置是关闭的状态，也可通过状态栏中间的机器人状态确认；
3. 之后就可通过上述接口或 RobotAssist 打开关闭 RCI 功能。需要注意的是，如果进行了抹除配置操作，那么同样
视为首次使用，需要再通过 SDK 的接口打开 RCI。
在用过 SDK 后，RCI 客户端就无法同时使用了。如果想切换回去，需调用 useRciClient(true)，调用前按照函数说
明，确保 RCI 是关闭的状态。然后再通过 RobotAssist 打开关闭 RCI 功能。
* @brief 示例 - 设置轴配置数据(confData)处理多逆解问题, 点位适用机型xMateCR7
void multiplePosture(xMateRobot &robot) {
std::string id;
// 本段示例使用默认工具工件
Toolset defaultToolset;
robot.setToolset(defaultToolset, ec);
MoveJCommand moveJ({0.2434, -0.314, 0.591, 1.5456, 0.314, 2.173});
// 同样的末端位姿，confData 不同，轴角度也不同
moveJ.target.confData =  {-67, 100, 88, -79, 90, -120, 0, 0};
robot.moveAppend({moveJ}, id, ec);
moveJ.target.confData =  {-76, 8, -133, -106, 103, 108, 0, 0};
robot.moveAppend({moveJ}, id, ec);
moveJ.target.confData =  {-70, 8, -88, 90, -105, -25, 0, 0};
robot.moveAppend({moveJ}, id, ec);
robot.moveStart(ec);
waitForFinish(robot, id, 0);
// 本段示例使用默认工具工件, 速度v500, 转弯区fine
Toolset defaultToolset;
robot.setToolset(defaultToolset, ec);
robot.setDefaultSpeed(500, ec);
robot.setDefaultZone(0, ec);
// 示例程序使用机型: xMateER7 Pro
// 1. 从当前位置MoveJ 运动到拖拽位置
std::array<double,7> q_drag_xm7p = {0, M_PI/6, 0, M_PI/3, 0, M_PI/2, 0};
robot.updateRobotState(std::chrono::milliseconds(1));
rtCon->MoveJ(0.4,  robot.jointPos(ec), q_drag_xm7p);
CartesianPosition start, aux, target;
robot.updateRobotState(std::chrono::milliseconds(1));
Utils::postureToTransArray(robot.posture(rokae::CoordinateType::endInRef, ec),
start.pos);
Eigen::Matrix3d rot_start;
Eigen::Vector3d trans_start, trans_aux, trans_end;
Utils::arrayToTransMatrix(start.pos, rot_start, trans_start);
trans_end = trans_start; trans_aux = trans_start;
trans_aux[0] -= 0.28;
trans_aux[1] -= 0.05;
trans_end[1] -= 0.15;
Utils::transMatrixToArray(rot_start, trans_aux, aux.pos);
Utils::transMatrixToArray(rot_start, trans_end, target.pos);
rtCon->MoveC(0.2, start, aux, target);
Utils::postureToTransArray(robot.posture(rokae::CoordinateType::endInRef, ec),
start.pos);
Utils::arrayToTransMatrix(start.pos, rot_start, trans_start);
trans_end = trans_start;
// 沿 x-0.1m, y-0.3m, z-0.25
trans_end[0] -= 0.1;
trans_end[1] -= 0.3;
trans_end[2] -= 0.25;
Utils::transMatrixToArray(rot_start, trans_end, target.pos);
print(os, "MoveL start position:", start.pos, "Target:", target.pos);
rtCon->MoveL(0.3, start, target);
robot.setMotionControlMode(rokae::MotionControlMode::NrtCommand, ec);
robot.setOperateMode(rokae::OperateMode::manual, ec);
} catch (const std::exception &e) {
std::cout << e.what();
idle 机器人静止
jog Jog 状态(未运动)
rtControlling 实时模式控制中
drag 拖动已开启
rlProgram RL 工程运行中
OperateMode operation_mode 操作模式
double speed_override 速度覆盖比例
std::array< double, 3 > trans 平移量, [X, Y , Z], 单位:米
std::array< double, 3 > rpy XYZ 欧拉角, [A, B, C], 单位:弧度
std::array< double, 16 >  pos 行优先变换矩阵。只用于实时模式笛卡尔位置/阻抗控制。
std::array< double, 3 > trans 平移量, [x, y, z], 单位:米
std::array< double, 3 > rpy XYZ 欧拉角, [A, B, C], 单位:弧度
double  elbow 臂角, 适用于 7 轴机器人, 单位：弧度
bool  hasElbow 是否有臂角
std::vector< int >  confData 轴配置数据，元素个数应和机器人轴数一致
std::vector< double >  external 外部关节数值 单位:弧度|米。导轨单位米
Type type 类型: Offs/RelTool
Frame frame 偏移坐标
std::vector< double >  joints 关节角度值, 单位:弧度
std::vector< double >  external 外部关节数值 单位:弧度|米。导轨单位米
std::vector< double >  tau 期望关节扭矩，单位: Nm
double  mass 负载质量, 单位:千克
std::array< double, 3 >  cog 质心 [x, y, z], 单位:米
std::array< double, 3 >  inertia 惯量 [ix, iy, iz], 单位:千克·平方米
根据一对工具工件的坐标、负载、机器人手持设置计算得出。
Load  load 机器人末端手持负载
Frame  end 机器人末端坐标系相对法兰坐标系转换
Frame  ref 机器人参考坐标系相对世界坐标系转换
Frame frame 标定结果
std::array<double, 3>  errors 样本点与 TCP 标定值的偏差, 依次为最小值,平均值,最大值, 单
std::string  name 工程名称
std::vector< std::string >  taskList 任务名称列表
std::string  name 名称
std::string  alias  别名, 暂未使用
bool  robotHeld 是否机器人手持
Frame  pos 位姿。工件的坐标系已相对其用户坐标系变换
Load  load 负载
JointPosition  target 目标关节点位
int  speed 末端线速度, 单位 mm/s, 关节速度根据末端线速度大小划分几个
区间，详见 setDefaultSpeed()
double jointSpeed 关节速度百分比
int  zone 转弯区大小, 单位 mm
std::string customInfo 自定义信息，可在运动信息反馈中返回出来
CartesianPosition  target 目标笛卡尔点位
int  speed 末端线速度, 单位 mm/s, 关节速度根据末端线速度大小划分几个
区间，详见 setDefaultSpeed()
double jointSpeed 关节速度百分比
int  zone 转弯区大小, 单位 mm
CartesianPosition::Offset offset 偏移量
std::string customInfo 自定义信息，可在运动信息反馈中返回出来
CartesianPosition  target 目标笛卡尔点位
int  speed 末端线速度, 单位 mm/s
double rotSpeed 空间旋转速度
int  zone 转弯区大小, 单位 mm
CartesianPosition ::Offset offset 偏移量
std::string customInfo 自定义信息，可在运动信息反馈中返回出来
CartesianPosition  target 目标笛卡尔点位
CartesianPosition  aux 辅助点位
int  speed 末端线速度, 单位 mm/s
double rotSpeed 空间旋转速度
int  zone 转弯区大小, 单位 mm
CartesianPosition ::Offset targetOffset 目标点偏移量
CartesianPosition ::Offset auxOffset 辅助点偏移量
std::string customInfo 自定义信息，可在运动信息反馈中返回出来
CartesianPosition  target 辅助点位1
CartesianPosition  aux 辅助点位 2
int  speed 末端线速度, 单位 mm/s
double rotSpeed 空间旋转速度
int  zone 转弯区大小, 单位 mm
double angle 全圆执行角度, 单位: 弧度
CartesianPosition ::Offset targetOffset 目标点偏移量
CartesianPosition ::Offset auxOffset 辅助点偏移量
RotType rotType 全圆姿态旋转模式
std::string customInfo 自定义信息，可在运动信息反馈中返回出来
CartesianPosition  target 终点笛卡尔点位
CartesianPosition::Offset targetOffset 偏移选项
double radius 初始半径, 单位: 米
double radius_step 每旋转单位角度，半径的变化，单位: 米/弧度
double angle 合计旋转角度, 单位: 弧度
bool direction 旋转方向, true - 顺时针 | false - 逆时针
std::string customInfo 自定义信息，可在运动信息反馈中返回出来
std::chrono::steady_clock::duration duration_ 停留时长, 最小有效时长1ms
const int  id 日志 ID 号
const std::string  timestamp 日期及时间
const std::string  content 日志内容
const std::string  repair 修复办法
bool key1_state CR1 号
bool key2_state CR2 号
bool key3_state CR3 号
bool key4_state CR4 号
bool key5_state CR5 号
bool key6_state CR6 号
bool key7_state CR7 号
template<WorkType Wt, unsigned short DoF>
void rokae::Robot_T< Wt, DoF >::connectToRobot (error_code &ec )
查询机器人当前操作模式
查询当前位置, IO 信号, 操作模式, 速度覆盖值
注解 此工具工件组仅为 SDK 运动控制使用, 不与 RL 工程相关.
注解 此工具工件组仅为SDK运动控制使用, 不与RL工程相关。设置后RobotAssist右上角会显示“toolx",
使用已创建的工具和工件，设置工具工件组信息
"tool0"和"wobj0"。一组工具工件无法同时为手持或外部；如果有冲突，以工具的位置为准，例如
使用已创建的工具和工件，设置工具工件组信息
1) 使用RL 工程中创建的工具工件: 需要先加载对应RL 工程;
2) 全局工具工件: 无需加载工程，直接调用即可。e.g. setToolset("g_tool_0", "g_wobj_0")
配置NTP。非标配功能，需要额外安装
手动同步一次时间，远端 IP 是通过 configNtp 配置的。耗时几秒钟，阻塞等待同步完成，接口预设的超时时间
设置是否使用轴配置数据(confData)计算逆解。初始值为 false
使用，逆解时会选取机械臂当前轴角度的最近解
setMaxCacheSize()
void rokae::BaseRobot::setMaxCacheSize(int number, error_code &ec)
设置最大缓存指令个数，指发送到控制器待规划的路径点个数，允许的范围[1,300]，初始值为 30。
注解 如果轨迹多为短轨迹，可以调大这个数值，避免因指令发送不及时导致机器人停止运动(停止后如
果有未执行的指令，可 moveStart()继续;
1) 对于 Event::moveExecution, 回调函数在同一个线程执行, 请避免函数中有执行时间较长的操作;
2) Event::safety 则每次独立线程回调, 没有执行时间的限制
queryEventInfo()
EventInfo rokae::BaseRobot::queryEventInfo(Event eventType, error_code &ec)
开始 jog 机器人，需要切换到手动操作模式。
操作，否则机器人会一直处于 jog 的运行状态。
1) 工具/工件坐标系使用原则同 setToolset();
2) 工业六轴机型和 xMateCR/SR 六 轴 机 型 支 持 两 种 奇 异 规 避 方 式 Jog：
Space::singularityAvoidMode, Space::baseParallelMode
3) CR5 轴机型支持平行基座模式 Jog：Space::baseParallelMode
[in] rate 速率, 范围 0.01 - 1
[in] step 步长。单位: 笛卡尔空间-毫米 | 轴空间-度。步长大于 0 即可，不设置上限， 如果机器
人机器人无法继续 jog 会自行停止运动。
创建实时运动控制类实例，通过此实例指针进行实时模式相关的操作。
接 disconnectFromRobot()，切换到非实时运动控制模式等，但做上述操作之后再进行实时模式控
返回 控制器对象
异常 RealtimeControlException 创建 RtMotionControl 实例失败，由于网络问题
ExecutionException 没有切换到实时运动控制模式
reconnectNetwork()
void rokae::MotionControl< MotionControlMode::RtCommand >::reconnectNetwork ( error_code &  ec )
重新连接到实时控制服务器
使用周期调度，设置回调函数。
尔位姿/力矩。其中笛卡尔位姿使用旋转矩阵表示旋转量，pos 为末端相对于基坐标系的位姿。
startMove()。 在调用 startMove 后执行其他指令可能会失败，例如下电等操作。正确停止方法是调
设置末端执行器相对于机器人法兰的位姿，设置 TCP 后控制器会保存配置，机器人重启后恢复默认设置。
设置工具和负载的质量、质心和惯性矩阵。设置负载后控制器会保存负载配置，机器人重启后恢复默认设置。
兼容 RCI 客户端设置的接口。通过 SDK 设置运动控制模式为实时模式之后，无法再使用原 RCI 客户端控制机器
人。 若有使用原版的需求，可在切换到非实时模式后，调用此接口。然后再在 RobotAssist 上打开 RCI 功能，即
可使用 RCI 客户端。
返回 末端按键的状态。末端按键编号见《xCore 机器人控制系统使用手册》末端把手的图示。

### API接口

xCore SDK(C++)
V1.6 2022.09 Rokae SDK 初版，适配 xCore 版本 v1.6.2；
V1.7 2023.02 Rokae SDK 正式版本，适配 xCore 版本 v1.7；
V1.8 2023.06 新增接口，优化和修复一些问题，适配 xCore 版本 v2.0;
V1.9 2023.10 新增接口，修复问题，适配 xCore 版本 v2.1
V2.0 2024.04 新增若干接口，修复问题，适配 xCore 版本 v2.2
v0.4.1 2024.07 新增急停复位等接口，适配 xCore 版本 v2.2.2
v0.5.0 2024.12 新增若干接口，修复问题，适配 xCore 版本 v3.0.1
xCore SDK 编程接口库是协作机器人厂商H机器人提供给客户用于二次开发的软件产品，通过编程接口库，客户可以对配套了
⚫ 机器人型号：支持控制所有机型，根据协作和工业机器人支持的功能不同，可调用的接口有所差别。
xCore SDK 无需其他额外的硬件设置。
无需通过 RobotAssist 进行任何设置，用户可直接用 xCore SDK 控制机器人。
切换到实时模式后，机器人重启后会保持打开状态，并自动切换成自动模式。
xCoreSDK
cd xCoreSDK-v0.5.0
cmake --build . --target sdk_example
2. 将 SDK 工程包保存到本地（无中文路径）；
3. 创建新工程文件，并将编译器选用为 MSVC2019；
LIBS += -L<path-to-library-directory> -lxCoreSDK
INCLUDEPATH += <path-to-include-directory>
#SDK
LIBS += -L$$PWD/xCoreSDK-v0.5.0/lib/Windows/Debug/64bit -lxCoreSDK
INCLUDEPATH += xCoreSDK-v0.5.0/include
#Eigen
INCLUDEPATH += xCoreSDK-v0.5.0/external
⚫ 文件路径：<当前工作目录>/_rokae_log_/<机器人 uid>/xCoreSDK_<YYYY-MM-DD>.log
user_log_settings.json 的文件，文件结构如下：
"_log_storage_directory_": "user_defined_log_storage_directory",
"_retention_days_": 5
xCore SDK 的错误码信息和异常信息支持中文和英文，根据用户 PC 设置的系统语言而定。设置显示中文则返回中
xCore 控制器实时模式接收运动命令的周期为 1ms，客户端需保证至少 1kHZ 的发送周期。如果计算量较大，推荐
本章列出各版本 xCore SDK 所支持的接口和功能简述。不同开发语言的版本对接口的功能定义基本一致，但是参
数、返回值和调用方法会有区别。
下表是各语言版本接口支持情况概览。
模块 API 功能 C++ Python & C# Android
根据机器人构型和轴数不同，C++版本的 SDK 提供了下列几个可供实例化的 Robot 类，初始化时会检查所选构型和
轴数是否和连接的机器人匹配：
类名 适用机型
xMateRobot 协作 6 轴
xMateErProRobot 协作 7 轴
StandardRobot 工业 6 轴
xMateCr5Robot 协作 CR5 轴
PCB4Robot 工业 4 轴
PCB3Robot 工业 3 轴
查询 SDK 版本号 sdkVersion()  版本号
非实时模式运动控制相关接口。
设置接收事件的回调函数 setEventWatcher(eventType,
callback)
eventType – 事件类型
callback – 处理事件的回调函
查询事件信息 queryEventInfo(eventType) eventType – 事件类型 事件信息
执行运动指令 executeCommand(command) command - 一条或多条
MoveL/MoveJ/MoveAbsJ/Mov
eC/MoveCF/MoveSP 指令
读取当前加速度 getAcceleration(acc, jerk) acc – 加速度
jerk – 加加速度
设置运动加速度 adjustAcceleration(acc, jerk) acc – 加速度
jerk – 加加速度
打开奇异规避功能 setAvoidSingularity(method,
enable, threshold)
enable – 打开/关闭
查询是否打开规避奇异功能 getAvoidSingularity(method) method – 奇异规避方式 已打开/已关闭
检验笛卡尔轨迹是否可达 checkPath(start, start_joint,
target)
start – 起始点
start_joint – 起始关节角度
target – 目标点
callback - 回调函数
useStateDataInLoop – 是否在
开始执行调度任务 startLoop(blocking) blocking – 是否阻塞
停止调度任务 stopLoop()
开始运动 startMove(mode) mode – 控制模式
停止运动 stopMove()
开始接收实时状态数据 startReceiveRobotState(timeout
, fields)
fields – 接收的数据列表
停止接收实时状态数据 stopReceiveRobotState()
更新机器人状态数据到当前
updateRobotState(timeout) timeout – 超时等待时间
获取机器人状态数据 getStateData(name, data) name - 数据名
data – 数据值
PTP 轴空间规划运动 MoveJ(speed, start, target) speed – 速度系数
start – 起始关节角度
target – 目标关节角度
MoveL(speed, start, target) speed – 速度系数
start – 起始位姿
target – 目标位姿
3 点圆弧规划运动 MoveC(speed, start, aux, target) speed – 速度系数
start – 起始位姿
aux – 辅助点位姿
target – 目标位姿
通过 setControlLoop()设置回调函数，函数内计算出每周期的运动指令，作为函数返回值返回。SDK 将返回的指令
滤波后发送给控制器。指令的数据类型（关节角度 /笛卡尔位姿/关节力矩）应与控制模式匹配。控制器的控制周期
是 1ms。控制器的监测窗口是 2 秒，根据网络延迟阈值的高低，如果在监测窗口内没有收到足够的指令，将返回
在开始运动之前，通过 startReceiveRobotState()设置要接收的数据和控制器发送的时间间隔。根据是否在上述的回
调函数中读取状态数据，更新的方式也不同。如果需要在回调函数中读取状态数据，为保证 1ms 的控制周期，
xCore-SDK 会在每次执行回调前更新状态数据，在回调函数内部直接调用 getStateDate()读取。
如果不需要在回调函数里读取状态数据，则需要用户程序按照设置的发送周期调用 updateStateData()更新状态数据，
然后再通过 getStateDate()接口读取。
SDK 为用户提供了 xMate 运动学与动力学计算的库，方便计算机器人正逆解和雅克比矩阵等，目前支持的机型有：
xMateER 系列所有机型, XMC7/12/18/20, XMS3/4；兼容性上支持 Linux x86_64、Windows 64bit 。主要接口功能包
括：运动学正解 getCartPose()，运动学逆解 getJointPos()，雅可比矩阵计算 jacobian()，动力学正解 getTorque()。
详见附录 A - C++ API。
然后通过 robot.model()接口获取。
S 规划指规划轨迹速度是 S 曲线，能保证速度加速度的连续可导，使得运动高效平稳。用户可根据需求进行轴空间
或者笛卡尔空间的 S 规划，是一种离线的规划方法，应该明确的是此方法不涉及到路径规划，路径应由用户定义与
以轴空间的 s 规划为例：
JointMotionGenerator joint_s(0.2, q_end)；   //创建一个目标关节角度为 q_end 的规划器，0.2 为速度系数；
joint_s.calculateSynchronizedValues(q_start);  //指定初始关节角度 q_start，并做同步处理；
joint_s.calculateDesiredValues(t, q_delta);     //计算在时间 t 时的关节角度相对于 q_start 的增量 q_delta；
机器人在运动过程中会检测机器人状态，检测到异常会上报给 SDK，用户可以通过以下 20 个错误位判断异常类型。
错误位 错误名称 错误原因 解决方法
0 kActualJointPositionLimitsViolation 实际轴角度超限
度和角速度连续可
导，机器人运行不平
1 kActualCartesianPositionLimitsViolation 实际末端位姿超限
2 kActualCartesianMotionGeneratorElbowLimitViolation 实际臂角超限
3 kActualJointVelocityLimitsViolation 实际轴速度超限
4 kActualCartesianVelocityLimitsViolation 实际末端速度超限
5 kActualJointAccelerationLimitsViolation 实际轴加速度超限
6 kActualCartesianAccelerationLimitsViolation 实际末端加速度超限
7 kCommandJointPositionLimitsViolation 指令轴角度超限
8 kCommandCartesianPositionLimitsViolation 指令末端位姿超限
9 kCommandCartesianMotionGeneratorElbowLimitViolation 指令臂角超限
10 kCommandJointVelocityLimitsViolation 指令轴速度超限
11 kCommandCartesianVelocityLimitsViolation 指令末端速度超限
12 kCommandJointAccelerationLimitsViolation 指令轴加速度超限
13 kCommandCartesianAccelerationLimitsViolation 指令末端加速度超限
14 kCommandJointAccelerationDiscontinuity 指令轴加速度不连续
17 kCommandTorqueDiscontinuity 指令力矩不连续
18 kCommandTorqueRangeViolation 指令力矩超限
15 kCollision 检测到碰撞
16 kCartesianPositionMotionGeneratorInvalidFrame 机器人奇异
19 kInstabilityDetection 检测到不稳定
2 伺服报错，通常需要
重启机器人；
-258 未找到匹配的数据名称 可能由于控制器和 SDK 版本不适配
-259 未找到匹配的指令名称 可能由于控制器和 SDK 版本不适配
-260 数据值错误, 可能是通信协议不匹配 可能由于控制器和 SDK 版本不适配
-272 未找到要查询的数据名称 可能由于控制器和 SDK 版本不适配
-273 数据不可读 可能由于控制器和 SDK 版本不适配
-288 数据不可写 可能由于控制器和 SDK 版本不适配
-338 录制的路径中存在超过关节软限位的情况。请重新录制 在软限位内拖动
-339 录制的路径中存在关节速度过快的情况, 请重新录制 放慢拖动动作
-340 未从机器人静止状态开始录制路径 机器人静止时再开始录制
-341 停止录制路径时机器人未停止运动 机器人静止时再停止录制
-342 机器人处于下电状态, 保存路径失败 机器人上电
-353 保存路径到磁盘失败 重新录制拖动轨迹，或重启机器人
- 实例类型错误或 SDK 未授权，连接被拒绝
255 未初始化连接机器人 一般不会发生，正常构造 Robot 类实例即可
257 无法解析机器人消息, 可能由于 SDK 版本与控制器版本
可能由于控制器和 SDK 版本不适配
- 联系技术支持人员授权 SDK 功能
272 事件未监听 先调用 setEventWatcher开始监听数据
未授权 SDK 功能 联系技术支持人员授权 SDK 功能
机器人实例类型与连接的机型不符 按照手册说明创建对应的机器人实例
滤波错误,输入数据非正数 检查指令数据，回调函数是否返回了未赋值的指令
滤波错误, 需滤波数据无限大 检查指令数据，回调函数是否返回了未赋值的指令
2. 调用 setMotionControlMode(RtCommand) 接口来打开 RCI 功能，若打开成功，机器人状态变为 RCI，状态栏的
print(os, "xCore-SDK 版本:", robot->sdkVersion());
// *** 获取机器人当前位姿，轴角度，基坐标系等信息 ***
auto joint_pos = robot->jointPos(ec); // 轴角度 [rad]
auto joint_vel = robot->jointVel(ec); // 轴速度 [rad/s]
auto joint_torque = robot->jointTorque(ec); // 轴力矩 [Nm]
auto tcp_xyzabc = robot->posture(CoordinateType::endInRef, ec);
auto flan_cart = robot->cartPosture(CoordinateType::flangeInBase, ec);
robot->baseFrame(ec); // 基坐标系
print(os, "末端相对外部参考坐标系位姿", tcp_xyzabc);
print(os, "法兰相对基坐标系 -", flan_cart);
auto model = robot->model();
auto ik = model.calcIk(tcp_xyzabc, ec);
auto fk_ret = model.calcFk(ik, ec);
// 可选: 设置碰撞检测事件回调函数
robot.setEventWatcher(Event::safety, [&](const EventInfo &info){
recoverFromCollision(robot, info);
MoveAbsJCommand moveAbsj({0, M_PI/6, 0, M_PI/3, 0, M_PI_2, 0});
MoveLCommand moveL1({0.562, 0, 0.432, M_PI, 0, -M_PI});
moveL1.target.elbow = 1.45;
robot.moveAppend({moveAbsj}, id, ec);
robot.moveAppend({moveL1}, id, ec);
moveL1.target.elbow = -1.51;
robot.moveAppend({moveL1}, id, ec);
robot.moveStart(ec);
// 最后一次moveAppend()发送一条指令，故index = 0
waitForFinish(robot, id, 0);
// ** 2) 60°臂角圆弧 **
CartesianPosition circle_p1({0.472, 0, 0.342, M_PI, 0, -M_PI}),
circle_a1({0.537, 0.065, 0.342, M_PI, 0, -M_PI}),
circle_a2({0.537, -0.065, 0.342, M_PI, 0, -M_PI});
// 臂角都是60°
circle_p1.elbow = M_PI/3;
circle_p2.elbow = M_PI/3;
circle_a1.elbow = M_PI/3;
circle_a2.elbow = M_PI/3;
MoveLCommand moveL2(circle_p1);
robot.moveAppend({moveL2}, id, ec);
MoveCCommand moveC1(circle_p2, circle_a1), moveC2(circle_p1, circle_a2);
std::vector<MoveCCommand> movec_cmds = {moveC1, moveC2};
robot.moveAppend(movec_cmds, id, ec);
robot.moveStart(ec);
// 最后一次moveAppend()发送2 条指令，故需要等待第二个点完成后返回，index 为第二个点的下标
waitForFinish(robot, id, (int)movec_cmds.size() - 1);
"wobjx", 状态监控显示的末端坐标也会变化。除此接口外, 如果通过 RobotAssist 更改默认工具工件
sdkVersion()
static std::string rokae::BaseRobot::sdkVersion ( )
查询 xCore-SDK 版本
setMotionControlMode()
void rokae::BaseRobot::setMotionControlMode ( MotionControlMode  mode,
设置运动控制模式
注解 在调用各运动控制接口之前, 须设置对应的控制模式。
注解 Robot 类在初始化时会调用一次运动重置。RL 程序和 SDK 运动指令切换控制，需要先运动重置。
注解 目前支持 stop2 停止类型 , 规划停止不断电 , 参见 StopLevel。 调用此接口后 , 暂停后可调用
moveStart()继续运动。若需要完全停止，不再执行已添加的指令，可调用 moveReset()
template<class Command >
void rokae::BaseRobot::moveAppend (const std::vector<Command> &cmds, std::string &cmdID,
添加单条或多条运动指令, 添加后调用 moveStart()开始运动
template<class Command >
void rokae::BaseRobot::moveAppend (std::initializer_list< Command > cmds, std::string &cmdID,
添加单条或多条运动指令, 添加后调用 moveStart()开始运动
template<class Command >
void rokae::BaseRobot::moveAppend(const  Command  &cmds, std::string &cmdID, error_code &ec )
添加单条运动指令, 添加后调用 moveStart()开始运动
template<class Command >
void rokae::BaseRobot::executeCommand ( std::initializer_list< Command >  cmds,
执行单条或多条运动指令，调用后机器人立刻开始运动
template<class Command >
void rokae::BaseRobot::executeCommand ( std::vector< Command >  cmds,
执行单条或多条运动指令，调用后机器人立刻开始运动
设置接收事件的回调函数
[in] callback 处理事件的回调函数。说明:
查询事件信息。与 setEventWatcher()回调时的提供的信息相同，区别是这个接口是主动查询的方式
注解 调用此接口并且机器人开始运动后，无论机器人是否已经自行停止，都必须调用 stop()来结束 jog
void rokae::xMateRobot::setAvoidSingularity (AvoidSingularityMethod method, bool enable,
void rokae::StandardRobot::setAvoidSingularity (AvoidSingularityMethod method, bool enable,
1) 四轴锁定: 支持工业六轴，xMateCR 和 xMateSR 六轴机型；
2) 牺牲姿态: 支持所有六轴机型；
bool rokae::xMateRobot::getAvoidSingularity  (AvoidSingularityMethod method, error_code &ec)
bool rokae::StandardRobot::getAvoidSingularity  (AvoidSingularityMethod method, error_code &ec)
bool rokae::xMateRobot::getAvoidSingularity  (AvoidSingularityMethod method, error_code &ec)
bool rokae::StandardRobot::getAvoidSingularity  (AvoidSingularityMethod method, error_code &ec)
注解 除非重复调用此接口，客户端内部逻辑不会主动析构返回的对象， 包括但不限于断开和机器人连
template<class Command>
void rokae::MotionControl< MotionControlMode::RtCommand >::setControlLoop (const
std::function<Command(void)>& callback, int priority = 0, bool useStateDataInLoop = false )
注解 1) 回调函数应按照 1 毫秒为周期规划运动命令，规划结果为函数的返回值。SDK 对返回值进行滤
波处理后发送给控制器。
2) JointPosition 的关节角度数组长度，和 Torque 的关节力矩值数组长度应和机器人轴数相同。若
3) 一次运动循环结束时，可以通过返回的 Command.setFinish()的方式来标识，SDK 内部会负责停
止运动以及停止调用回调函数
1) xCore -SDK 会 在 回 调 函 数 之 前 更 新 实 时 状 态 数 据(updateStateData()),在 回 调 函 数 内 直 接
getStateData()即可;
2) 状态数据的发送周期应和控制周期一致, 为 1ms: startReceiveRobotState(interval = milliseconds(1));
startLoop()
void rokae::MotionControl< MotionControlMode::RtCommand >::startLoop (bool blocking = true )
指定控制模式，机器人准备开始运动，在每段回调执行前需要先调用此接口。  调用此接口机器人不会立即开始
注解 1) 在 startMove 之 前 应 将 参 数 依 次 设 置 好 ， 例 如 滤 波 阻 抗 参 数 等 等 ， 设 置 完 成 后 再 调 用
用 stopMove; 2) 如果没有通过 startReceiveRobotState()设置要接收的状态数据, 调用此函数时会自动
后会机器人停止运动， 呈现的效果和调用 stopMove()一样。 此函数仅用于实时控制，不可以用于
startReceiveRobotState()
template<WorkType Wt, unsigned short DoF>
void rokae::Robot_T::startReceiveRobotState (std::chrono::steady_clock::duration interval, const std::vector<std::string>&
fields)
让机器人开始发送实时状态数据。阻塞等待收到第一帧消息，超时时间为3 秒
接收一次机器人状态数据。在每周期读取数据前，需调用此函数；建议按照设定的发送频率来调用，以获取最新
[in]  if_rs485 接口工作模式，是否打开末端 485 通信
XPRWModbusRTUReg ()
void rokae::BaseCobot::XPRWModbusRTUReg (int slave_addr, int fun_cmd, int reg_addr, std::string data_type, int num,
std::vector<int>& data_array, bool if_crc_reverse, error_code& ec)
通过 xPanel 末端读写 modbus 寄存器
[in]  data_type 支持的数据类型  int32、int16、uint32、uint16
点位跟随功能, 点位可以是笛卡尔位姿或轴角度。默认构造函数, 必须调用 init()来初始化
template<unsigned short DoF>
void FollowPosition<DoF>::init(Cobot<DoF>& robot, XMateModel<DoF>& model)
初始化 FollowPosition。
开始目标跟随 - 笛卡尔位姿。该接口非阻塞。
开始目标跟随 - 轴角度。该接口非阻塞

### 示例代码

├── example: 示例程序
├── external:  Eigen
3. 选择编译 Release 或 Debug，编译示例程序
静态库编译示例：
DEFINES += _USE_MATH_DEFINES
Linux 系统(Debian 发行版): 打开终端，输入命令 “nc –vul –p 1337”, 然后再任意运行一个实时模式控制的示例程序，
力控和机器本身硬件状态有关系。如果出现开启直接力矩控制之后没有发 送任何指令，但是机器人下坠或者发飘
本章展示一些 C++示例程序，更多示例请见软件包中 examples。
* @brief 示例 - 基础的信息查询，计算正逆解
template <WorkType wt, unsigned short dof>
void example_basicOperation(Robot_T<wt, dof> *robot){
auto robotinfo = robot->robotInfo(ec);
print(os, "控制器版本号:", robotinfo.version, "机型:", robotinfo.type);
* @brief 示例 - 打开关闭拖动
void example_drag(BaseCobot *robot) {
robot->setOperateMode(rokae::OperateMode::manual, ec);
robot->setPowerState(false, ec); // 打开拖动之前，需要机械臂处于手动模式下电状态
robot->enableDrag(DragParameter::cartesianSpace, DragParameter::freely, ec);
print(os, "打开拖动", ec, "按回车继续");
std::this_thread::sleep_for(std::chrono::seconds(2)); //等待切换控制模式
while(getchar() != '\n');
robot->disableDrag(ec);
std::this_thread::sleep_for(std::chrono::seconds(2)); //等待切换控制模式
* @brief 示例 - 读写IO, 寄存器
void example_io_register(BaseRobot *robot) {
print(os, "DO1_0 当前信号值为:", robot->getDO(1,0,ec));
robot->setSimulationMode(true, ec); // 只有在打开输入仿真模式下才可以设置DI
robot->setDI(0, 2, true, ec);
print(os, "DI0_2 当前信号值:", robot->getDI(0, 2, ec));
robot->setSimulationMode(false, ec); // 关闭仿真模式
// 读取单个寄存器，类型为float
// 假设"register0"是个寄存器数组, 长度是10
float val_f;
std::vector<float> val_af;
// 读第1 个，即状态监控里的register0[1], 读取结果赋值给val_f
robot->readRegister("register0", 0, val_f, ec);
// 读第10 个，即状态监控里的register0[10], 读取结果赋值给val_f
robot->readRegister("register0", 9, val_f, ec);
* @brief 示例 - Jog 机器人
* @param robot
void example_jog(BaseRobot *robot) {
robot->setMotionControlMode(rokae::MotionControlMode::NrtCommand, ec);
robot->setOperateMode(rokae::OperateMode::manual, ec); // 手动模式下jog
print(os, "准备Jog 机器人, 需手动模式上电, 请确认已上电后按回车键");
robot->setPowerState(true, ec);
print(os, "-- 开始Jog 机器人-- \n 世界坐标系下, 沿Z+方向运动50mm, 速率50%，等待机器人停止运动后按回
robot->startJog(JogOpt::world, 0.5, 50, 2, true, ec);
while(getchar() != '\n');
print(os, "轴空间，6 轴负向连续转动，速率5%，按回车停止Jog");
robot->startJog(JogOpt::jointSpace, 0.05, 5000, 5, false, ec);
while(getchar() != '\n'); // 按回车停止
robot->stop(ec); // jog 结束必须调用stop()停止
* @brief 示例 - 打开和关闭碰撞检测
template <unsigned short dof>
void example_setCollisionDetection(Cobot<dof> *robot) {
// 设置各轴灵敏度，范围0.01 ~ 2.0，相当于RobotAssist 上设置的1% ~ 200%
// 触发行为：安全停止；回退距离0.01m
robot->enableCollisionDetection({1.0, 1.0, 0.01, 2.0, 1.0, 1.0, 1.0}, StopLevel::stop1,
std::this_thread::sleep_for(std::chrono::seconds(2));
robot->disableCollisionDetection(ec);
* @brief 示例 - 七轴冗余运动 & 发生碰撞检测后恢复运动, 点位适用机型xMateER3 Pro
void redundantMove(xMateErProRobot &robot) {
std::string id;
* @brief 示例 - 带导轨运动。点位适配机型xMateSR4
template <WorkType wt, unsigned short dof>
void moveWithRail(Robot_T<wt, dof> *robot) {
bool is_rail_enabled;
robot->getRailParameter("enable", is_rail_enabled, ec);
if(!is_rail_enabled) {
print(os, "未开启导轨");
// *** Jog 导轨示例 ***
robot->setOperateMode(OperateMode::manual, ec);
robot->setPowerState(true, ec);
std::vector<double> soft_limit;
robot->getRailParameter("softLimit", soft_limit, ec);
// 在软限位内Jog
double step = (curr.back() - soft_limit[0] > 0.1 ? 0.1 : (curr.back() - soft_limit[0])) *
// 导轨轴空间负向运动100mm
robot->startJog(JogOpt::jointSpace, 0.6, step, ex_jnt_index, false, ec);
// 等待Jog 结束
while(true) {
std::this_thread::sleep_for(std::chrono::milliseconds(50));
if(robot->operationState(ec) != OperationState::jogging) break;
robot->stop(ec);
// *** 带导轨的运动指令示例 ***
CartesianPosition p0({0.56, 0.136, 0.416, M_PI, 0, M_PI}), p1({0.56, 0.136, 0.3, M_PI, 0,
p0.external = { 0.02 }; // 导轨运动到0.02m, 下同
p1.external = { -0.04 };
MoveAbsJCommand abs_j_command({0, M_PI/6, -M_PI_2,0, -M_PI/3, 0 });
abs_j_command.target.external = { 0.1 }; // 导轨运动到0.1m
MoveJCommand j_command(p0);
MoveLCommand l_command(p1);
MoveCCommand c_command(p1, p0);
l_command.customInfo = "hello";
std::string id;
robot->moveAppend(abs_j_command, id, ec);
robot->moveAppend(j_command, id, ec);
robot->moveAppend(l_command, id, ec);
robot->moveAppend(abs_j_command, id, ec);
robot->moveAppend(c_command, id, ec);
robot->moveStart(ec);
waitForFinish(*robot, id, 0);
int main() {
using namespace std;
std::string ip = "192.168.0.160";
std::error_code ec;
robot.setOperateMode(rokae::OperateMode::automatic,ec);
robot.setMotionControlMode(MotionControlMode::RtCommand, ec);
robot.setPowerState(true, ec);
auto rtCon = robot.getRtMotionController().lock();
// 设置要接收数据。其中jointPos_m 是本示例程序会用到的
rtCon->startReceiveRobotState({RtSupportedFields::jointPos_m,
RtSupportedFields::tauVel_c,
RtSupportedFields::tcpPose_m, RtSupportedFields::elbow_m});
rtCon->updateRobotState();
std::array<double,7> array7 {};
rtCon->getStateData(RtSupportedFields::tauVel_c, array7);
std::array<double, 16> init_position {};
static bool init = true;
rtCon->getStateData(RtSupportedFields::jointPos_m, array7);
std::array<double,7> q_drag_xm7p = {0, M_PI/6, 0, M_PI/3, 0, M_PI/2, 0};
// 获取机器人当前轴角度(需要设置"jointPos_m"为要接收的状态数据)
// 从当前位置MoveJ 运动到拖拽位姿
rtCon->MoveJ(0.5, array7, q_drag_xm7p);
rtCon->setCartesianImpedance({1000, 1000, 1000, 100, 100, 100}, ec);
rtCon->startMove(RtControllerMode::cartesianImpedance);
std::atomic<bool> stopManually { true };
std::function<CartesianPosition()> callback = [&, rtCon] {
rtCon->getStateData(RtSupportedFields::tcpPose_m, init_position);
init = false;
constexpr double kRadius = 0.2;
double angle = M_PI / 4 * (1 - std::cos(M_PI / 2 * time));
double delta_z = kRadius * (std::cos(angle) - 1);
CartesianPosition output{};
output.pos = init_position;
output.pos[7] += delta_z;
output.setFinished(); // 20 秒后结束
stopManually.store(false);  // loop 为非阻塞，和主线程同步停止状态
rtCon->setControlLoop(callback);
rtCon->startLoop(false);
while(stopManually.load());
} catch (const std::exception &e) {
std::cout << e.what();
int main() {
using namespace std;
std::string ip = "192.168.0.160";
std::error_code ec;
rokae::xMateErProRobot robot(ip, "192.168.0.180"); // ****   XMate 7-axis
robot.setOperateMode(rokae::OperateMode::automatic,ec);
robot.setRtNetworkTolerance(20, ec);
robot.setMotionControlMode(MotionControlMode::RtCommand, ec);
robot.setPowerState(true, ec);
auto rtCon = robot.getRtMotionController().lock();
print(os, "Start receive");
robot.startReceiveRobotState(std::chrono::milliseconds(1),
{RtSupportedFields::jointPos_m, RtSupportedFields::elbow_m, RtSupportedFields::tcpPose_m});
dynamicIdentify 动力学辨识中
loadIdentify 负载辨识中
moving 机器人运动中
jogging Jog 运动中
unknown 未知
industrial 工业机器人
collaborative 协作机器人
manual 手动
automatic 自动
unknown 未知(发生异常)
estop 急停被按下
gstop 安全门打开
unknown 未知(发生异常)
flangeInBase 法兰相对于基坐标系
endInRef 末端相对于外部坐标系
NrtCommand 非实时模式执行运动指令
NrtRLTask 非实时模式运行 RL 工程
RtCommand 实时模式控制
jointPosition 实时轴空间位置控制
cartesianPosition 实时笛卡尔空间位置控制
jointImpedance 实时轴空间阻抗控制
cartesianImpedance 实时笛卡尔空间阻抗控制
torque 实时力矩控制
stop0 快速停止机器人运动后断电
stop1 规划停止机器人运动后断电, 停在原始路径上
stop2 规划停止机器人运动后不断电, 停在原始路径上
suppleStop 柔顺停止，仅适用于协作机型
Space::jointSpace 轴空间拖动
Space::cartesianSpace 笛卡尔空间拖动
Type::translationOnly 仅平移
Type::rotationOnly 仅旋转
world 世界坐标系
base 基坐标系
flange 法兰坐标系
wobj 工件坐标系
path 路径坐标系, 力控任务坐标系需要跟踪轨迹变化的过程
rail 导轨基坐标系
world 世界坐标系
flange 法兰坐标系
baseFrame 基坐标系
toolFrame 工具坐标系
wobjFrame 工件坐标系
jointSpace 轴空间
singularityAvoidMode 奇异规避模式，适用于工业六轴, xMateCR 和 xMateSR 六轴机
baseParallelMode 平行基座模式，适用于工业六轴, xMateCR 和 xMateSR 六轴机
lockAxis4 四轴锁定
wrist 牺牲姿态
jointWay 轴空间短轨迹插补
constPose 不变姿态
rotAxis 动轴旋转
fixedAxis 定轴旋转
reserve 保留
supply12v 输出 12V
supply24v 输出 24V
full 关节力矩，由动力学模型计算得到
inertia 惯性力
coriolis 科氏力
gravity 重力
moveExecution 非实时运动指令执行信息
safety 安全 (是否碰撞)
std::string  id 机器人 uid, 可用于区分连接的机器人
std::string  version 控制器版本
std::string  type 机器人机型名称
std::vector<double> joint_pos  轴角
CartesianPosition cart_pos 笛卡尔位姿
std::vector<std::pair<std::string, bool>>
digital_signals 数字量 IO
std::vector<std::pair<std::string,  double>>
analog_signals; 模拟量 IO

---

## xCore_SDK_Python使用手册V3.0_A.pdf

### 产品概述

运行 RL 工程，等等。该使用说明书主要介绍编程接口库的使用方法，以及各接口函数的功能。用户可编写自己的
应用程序，集成到外部软硬件模块中。
⚫ 控制器版本：xCore v3.0.1 及以后。
本章介绍如何配置并运行一个 xCore SDK Python 程序。
其他语言版本（C++、Java）请参考分手册。
返回值和调用方法会有区别。本章节介绍主要针对 Python 版本的开发接口，其他语言开发接口请见分手册。

### 技术参数

如果只使用非实时控制，对于网络性能要求不高，可以通过无线连接。
本章列出各版本 xCore SDK 所支持的接口和功能简述。 不同开发语言的版本对接口的功能定义基本一致， 但是参数、
简述 接口 参数 返回
连接机器人 connectToRobot()
connectToRobot(remoteIP,
localIP)
remoteIP - 机器人 IP 地
断开连接 disconnectFromRobot()
查询机器人基本信息 robotInfo()  控制器版本，机型，轴数
查询上电状态 powerState()  on/off/Estop/Gstop
机器人上下电 setPowerState(state) state - on/off
置参数
获取当前关节角度 jointPos()  各轴角度 rad
获取当前关节速度 jointVel()  各轴速率 rad/s
获取关节力矩 jointTorque()  各轴力矩 Nm
查询基坐标系 baseFrame()  [ X, Y , Z, A, B, C ]
查询当前工具工件组 toolset()  末端坐标系, 参考坐标系,
负载信息
设置工具工件组 setToolset(toolset) toolset – 工具工件组信
setToolset(toolName,
wobjName)
toolName – 工具名称
wobjName - 工件名称
计算逆解 calcIk(posture) posture – 末端相对于外
关节角度
计算逆解 calcIk(posture,tool_set) posture – 末端相对于外
tool_set - 工具坐标
关节角度
计算正解 calcFk(joints) joints – 关节角度 末端相对于外部参考坐标
计算正解 calcFk(joints, tool_set) joints – 关节角度
tool_set - 工具坐标
末端位姿
清除伺服报警 clearServoAlarm()
查询控制器日志 queryControllerLog(count,
level)
level - 日志等级
控制器日志列表
enableCollisionDetection
(sensitivity, behaviour,
fallback)
sensitivity – 灵敏度
behaviour – 碰撞后行为
fallback – 回退距离/柔
关闭碰撞检测功能 disableCollisionDetection()
坐标系标定  calibrateFrame(type, points,
is_held, base_aux)
type – 坐标系类型
points – 标定轴角度列表
is_held – 手持/外部工具
base_aux – 基坐标系标
获取当前软限位数值  getSoftLimit(limits) limits - 各轴软限位 已打开/已关闭
设置软限位 setSoftLimit(enable, limits) enable – 打开/关闭
limits -各轴软限位
恢复状态 recoverState(item) item - 恢复选项
设置导轨参数 setRailParameter(name, value) name – 参数名
value – 参数值
读取导轨参数 getRailParameter(name, value) name – 参数名
value – 参数值
简述 接口 参数 返回
设置运动控制模式 setMotionControlMode(m
重置运动缓存 moveReset()
机器人开始/继续运动 moveStart()
停止机器人运动 stop()
暂停机器人运动 pause()
添加运动指令  moveAppend(command,
command - 一条或多条
MoveL/MoveJ/MoveAbsJ/
MoveC/MoveCF/MoveSP
设置默认运动速度 setDefaultSpeed(speed) speed - 末端最大线速度
设置默认转弯区 setDefaultZone(zone) zone - 转弯区半径
threshold – 阈值参数
getAvoidSingularity(metho
简述 接口 参数 返回值
查询 DI 信号值 getDI(board, port) board - IO 板序号
设置 DI 信号值  setDI(board, port, state) board - IO 板序号
state - 信号值
查询 DO 信号值 getDO(board, port) board - IO 板序号
设置 DO 信号值 setDO(board, port, state) board - IO 板序号
state - 信号值
查询 AI 信号值 getAI(board, port)  board - IO 板序号
设置 AO 信号  setAO(board, port, value)  board - IO 板序号
value - 信号值
设置输入仿真模式  setSimulationMode(state)  state – 打开/关闭
读取寄存器值 readRegister(name, index,  name - 寄存器名称
value) index - 寄存器数组索引
value - 读取的数值
写入寄存器值 writeRegister(name, index,
value)
name - 寄存器名称
value - 写入的数值
设置 xPanel 对外供电
setxPanelVout(opt) opt – 模式
获取末端按键状态 getKeypadState()   末端按键的状态
简述 接口 参数 返回值
加载工程 loadProject(name, tasks) name - 工程名称
tasks – 任务列表
pp-to-main ppToMain()
暂停运行工程 pauseProject()
setProjectRunningOpt(rate,
rate – 运行速率
查询工具信息 toolsInfo()  工具名称, 位姿, 负载等信
查询工件信息 wobjsInfo()  工件名称, 位姿, 负载等信
简述 接口 参数 返回值
打开拖动 enableDrag(space, type,
enable_drag_button)
space – 拖动空间
type – 拖动类型
enable_drag_button - 打开
动机器人，不需要按住末
关闭拖动 disableDrag()
开始记录拖动路径 startRecordPath(duration) duration – 记录时间
停止记录拖动路径 stopRecordPath()
保存拖动路径 saveRecordPath(name,
saveAs)
name – 拖动路径保存名称
saveAs – 如名称存在的命
取消记录拖动路径 cancelRecordPath()
回放路径 replayPath(name, rate) name – 回放路径名称
rate – 回放速率
删除保存的拖动路径 removePath(name) name – 希望删除的路径名
查询已保存的拖动路径 queryPathLists()  已保存的路径名称列表
力传感器标定 calibrateForceSensor(all_ax
es, axis_index)
all_axes – 标定所有轴
axis_index – 单轴标定下标
简述 接口 参数 返回值
获取当前力矩信息 getEndTorque(ref_type,
joint, external, cart_torque,
cart_force)
external -各轴外部力
cart_torque - 笛卡尔空间力
cart_force - 笛卡尔空间力
力控初始化 fcInit(frame_type) frame_type - 力控坐标系
开始力控 fcStart()
停止力控  fcStop()
设置阻抗控制类型 setControlType(type)  type - 阻抗类型
否正常，并设置合理的力控保护参数
-28708 参数错误 重新设置数据
-28709 机器人处于碰撞停止 上电恢复碰撞状态
-28710 机器人处于急停状态 恢复急停
-28711 请求被拒绝 阻抗控制时多由于力控模型偏差，重新标定力矩传
感器并设置正确的负载
-41419 TCP 长度超限，力控初始化失败 末端工具长度限制为 0.3m
-41420 未进行力控初始化; 或未正确设置负载; 或力控
- 标定零点、力矩传感器；
- 设置正确的负载质量和质心；
- 开启拖动时机器人没有收到外力
-41421 停止力控失败，当前不处于力控运行状态 机器人不处于力控状态
-41425 非阻抗控制模式，或搜索运动在运行中 - 保证当前处于阻抗模式下，且搜索运动处于停止
- 请检查参数设置
-41426 非阻抗控制模式，或搜索运动在运行中 - 保证当前处于阻抗模式下，且搜索运动处于停止
- 请检查参数设置
-41427 当前不处于笛卡尔阻抗控制模式或未设置搜索
检查控制模式指令，设置搜索运动参数后再尝试
-41428 当前不处于笛卡尔阻抗控制模式或未开始搜索
-41429 当前未处于笛卡尔阻抗模式或搜索运动未暂停 暂停当前的力控任务并检查控制模式，切换到笛卡
尔阻抗控制模式后再尝试
-41430 不支持的阻抗控制类型或力控坐标系 停止当前的力控任务并重新参数初始化
-41431 当前未处于关节阻抗控制模式或未初始化 运行力控前设置轴空间阻抗控制模式
-41432 当前未处于笛卡尔阻抗控制模式或未初始化 运行力控前设置笛卡尔阻抗控制模式
-41433 当前未处于笛卡尔阻抗控制模式或未初始化 检查当前的阻抗控制模式后再进行尝试。确保力值
输入正确，且设定笛卡尔阻抗控制模式
-41434 关节期望力超过限制 检查当前的阻抗控制模式后再进行尝试。确保期望
力值输入正确，且设定轴空间阻抗控制模式
-41435 笛卡尔空间期望力超过限制 检查当前的阻抗控制模式后再进行尝试。确保期望
力值输入正确，且设定笛卡尔阻抗控制模式
-41442 机器人不满足软限位要求，开启力控失败 请确认机器人开启阻抗时机器人在软限位内
-41444 阻抗刚度设置失败， 数值不合理或当前状态不能
设置刚度
请重新设置阻抗刚度数值在合理范围内
-50021 指定 conf 参数下目标点无解, 请检查数值或不
设置 confData
- 调用 setDefaultConfOpt(false) 取消 confdata
- 重新示教点位，传入正确的 confdata
-50033 机器人处于锁轴状态， 目标点锁轴角度发生了偏
轴角度要求为 0 度或 180 度或-180 度
-50101 轴角度超出运动范围 , 尝试取消软限位后恢复
- 手动将机器人各轴移动到正常的工作范围内
- 将笛卡尔空间运动指令改为关节空间运动指令
载系数等参数
为关节空间指令
- 如果当前机型为三轴或者四轴机器人 ,请检查输
-50512 轴数不匹配 轴空间 Jog 的下标参数不能超出轴数+外部轴数
-50513 速度设置无效，机器人无法运动 传入 0.01~1 范围内的速度参数
-50514 步长设置无效，机器人无法运动 传入大于 0 的步长参数
-50515 参考坐标系设置无效，机器人无法运动 传入支持的坐标系类型参数
-50516 运动轴设置无效，机器人无法运动 按照说明传入 index 参数
-50519 生成轨迹失败 , 目标点位可能超出机器人工作
请在机器人正常工作范围内，重新示教点位
-50525 该机型不支持奇异规避模式运动 , 或机器人锁
轴失败, 4 轴角度不为 0 不运行运动, 请调整 4 轴
角度
调整四轴角度至 0 或者正负 180 度
-60014 控制器当前状态不允许开始运动 确保机器人上电并处于空闲中
-60200 负载信息错误, 设置失败 - 负载信息错误 ,请检查负载重量是否超过额定负
载，质心不超过 0.3m
258 参数错误,数值超出范围 按照函数说明检查参数数值范围
259 参数错误,参数类型或个数错误 按照函数说明检查参数类型或数组长度
260 不是合法的变换矩阵 检查传入参数是否符合其次变换矩阵要求
261 数组元素个数与机器人轴数不符 传入和机器人轴数一致的数组长度
262 运动控制模式错误,请切换到正确的模式 根据实际情况调用 setMotionControlMode 切换模式
263 超时前未收到机器人回复 , 可能由于网络通信
155.     # 设置 toolset 参数
156.     robot.setToolset(toolset, ec)
157.     print_log("setToolset",ec)
159. def set_toolset_by_name(robot,ec):
161.     print_separator("set_toolset_by_name",length=80)
163.     toolset = robot.setToolset("tool0", "wobj0", ec)
164.     print_log("setToolset",ec)
166.           load mass: {toolset.load.mass}
167.           load cog: {', '.join(map(str, toolset.load.cog))}
168.           load inertia:{','.join(map(str,toolset.load.inertia))}
169.           end trans:{','.join(map(str,toolset.end.trans))}
170.           end rpy:{','.join(map(str,toolset.end.rpy))}
171.           end pos:{','.join(map(str,toolset.end.pos))}
172.           ref trans:{','.join(map(str,toolset.ref.trans))}
173.           ref rpy:{','.join(map(str,toolset.ref.rpy))}
174.           ref pos:{','.join(map(str,toolset.ref.pos))}
177. def clear_servo_alarm(robot,ec):
178.     '''清除伺服报警'''
179.     print_separator("clear_servo_alarm",length=80)
180.     robot.clearServoAlarm(ec)
181.     print_log("clearServoAlarm",ec)
183. def calcFk(robot,ec):
184.     '''计算正解，关节角度->笛卡尔坐标'''
185.     print_separator("calcFk",length=80)
186.     start_angle = [0, 0.557737,-1.5184888, 0,-1.3036738, 0] # 单位弧度
188.     cart_pose = robot_model.calcFk(start_angle, ec)
189.     print_log("calcFk",ec)
190.     print(f"elbow,{cart_pose.elbow}")
191.     print(f"hasElbow,{cart_pose.hasElbow}")
192.     print(f"confData,f{','.join(map(str,cart_pose.confData))}")
193.     print(f"external size,{len(cart_pose.external)}")
194.     print(f"trans,{','.join(map(str,cart_pose.trans))}")
195.     print(f"rpy,{','.join(map(str,cart_pose.rpy))}")
196.     print(f"pos,{','.join(map(str,cart_pose.pos))}")
198. def calcIk(robot,ec):
199.     '''计算逆解，笛卡尔坐标 -> 关节角度'''
200.     print_separator("calcIk",length=80)
参数 [out] ec： 错误码
def connectToRobot(self, remoteIP: str, localIP: str = '')
连接到机器人
disconnectFromRobot()
def disconnectFromRobot(self, ec: dict)
断开与机器人连接。断开前会停止机器人运动, 请注意安全
参数 [out] ec： 错误码
def robotInfo(self, ec: dict) -> Info
查询机器人基本信息
参数 [out] ec ：错误码
返回 机器人基本信息：控制器版本，机型，轴数
powerState()
def powerState(self, ec: dict) -> PowerState
机器人上下电以及急停状态
参数 [out] ec ：错误码
返回 0：on-上电 | 1：off-下电 |2： estop-急停 | 3：gstop-安全门打开
setPowerState()
def setPowerState(self, on: bool, ec: dict)
机器人上下电。注: 只有无外接使能开关或示教器的机器人才能手动模式上电。
参数 [in] on： true-上电 | false-下电
operateMode()
def operateMode(self, ec: dict) -> OperateMode
参数 [out] ec： 错误码
返回 0：mannual-手动 | 1：automatic-自动
setOperateMode()
def setOperateMode(self, mode: OperateMode, ec: dict)
参数 [in] mode： manual：手动 | automatic：自动
operationState()
def operationState(self, ec: dict) -> OperationState
查询机器人当前运行状态 (空闲,运动中, 拖动开启等)
参数 [out] ec： 错误码
返回 运行状态枚举类
posture()
def posture(self, ct: CoordinateType, ec: dict) -> List[float]
获取机器人法兰或末端的当前位姿
参数 [in] ct 坐标系类型
1) flangeInBase: 法兰相对于基坐标系;
2) endInRef: 末端相对于外部参考坐标系。例如,当设置了手持工具及外部工件后，该坐
标系类型返回的是工具相对于工件坐标系的坐标。
cartPosture()
def cartPosture(self, ct: CoordinateType, ec: dict) -> CartesianPosition
获取机器人法兰或末端的当前位姿
参数 [in] ct 坐标系类型
jointPos()
def jointPos(self, ec: dict) -> List[float]
机器人当前轴角度, 机器人本体+外部轴, 单位: 弧度, 外部轴导轨单位米
参数 [out] ec：错误码
返回 轴角度值
jointVel()
def jointVel(self, ec: dict) ->  List[float]
机器人当前关节速度, 机器人本体+外部轴，单位：弧度/秒,外部轴单位米/秒
参数 [out] ec： 错误码
返回 关节速度
def jointTorque(self, ec: dict) ->  List[float]
关节力传感器数值，单位: Nm
参数 [out] ec： 错误码
baseFrame()
def baseFrame(self, ec: dict) ->  List[float]
参数 [out] ec ：错误码
返回 数组, [X, Y , Z, A, B, C]，其中平移量单位为米旋转量单位为弧度
toolset()
def toolset(self, ec: dict) -> Toolset
参数 [out] ec： 错误码
setToolset() [1/2]
def setToolset(self, toolset: Toolset, ec: dict)
参数 [in] toolset：工具工件组信息
setToolset() [2/2]
def setToolset(self, toolName: str, wobjName: str, ec: dict) -> Toolset
工件， 即"tool0"和"wobj0"。 一组工具工件无法同时为手持或外部； 如果有冲突， 以工具
参数 [in] toolName：工具名称
[in] wobjName: 工件名称
返回 设置后的工具工件组信息。当发生错误设置失败时，返回 Toolset 类型初始化默认值
calcIk() [1/2]
def calcIk(self, posture : CartesianPosition, ec: dict) -> list[float]
参数 [in] posture： 法兰末端位姿,相对于基坐标系
返回 轴角度数组（单位:弧度）
calcIk() [2/2]
def calcIk(self, posture : CartesianPosition, toolset: Toolset, ec: dict) -> list[float]
参数 [in] posture： 法兰末端位姿
[in] toolset : 工具工件组信息
返回 轴角度数组（单位:弧度）
calcFk() [1/2]
def calcFk(self, joints: list[float], ec: dict) -> CartesianPosition
根据轴角度计算正解
参数 [in] joints： 轴角度, 单位: 弧度
返回 机器人末端位姿，相对于外部参考坐标系
calcFk() [2/2]
def calcFk(self, joints: list[float],toolset: Toolset, ec: dict) -> CartesianPosition
根据轴角度计算正解
参数 [in] joints： 轴角度, 单位: 弧度
[in] toolset : 工具工件组信息
返回 机器人末端位姿，相对于外部参考坐标系
calibrateFrame ()
def calibrateFrame(self, type: FrameType, points: list[float], is_held: bool, ec: dict, base_aux: list[float]) ->
FrameCalibrationResult
注解 各坐标系类型支持的标定方法及注意事项：  1) 工具坐标系: 三点/四点/六点标定法 2)
前馈已关闭。 若标定成功(无错误码)， 控制器会自动保存标定结果， 重启控制器后生效。
参数 [in] points 轴角度列表， 列表长度为N。 例如， 使用三点法标定工具坐标系， 应传入3 组
轴角度。轴角度的单位是弧度。
[in] is_held true - 机器人手持 | false - 外部。仅影响工具/工件的标定
[in] base_aux 基坐标系标定时用到的辅助点, 单位[米]
clearServoAlarm()
def clearServoAlarm(self, ec: dict)
清除伺服报警
参数 [out] ec：错误码，当有伺服报警且清除失败的情况下错误码置为-1
enableCollisionDetection()
def enableCollisionDetection(self, sensitivity: list[float], behaviour: StopLevel, fallback_compliance: float,
设置碰撞检测相关参数, 打开碰撞检测功能
参数 [in] sensitivity 碰撞检测灵敏度，范围 0.01-2.0
[in] behaviour 碰撞后机器人行为, 支持 stop1(安全停止, stop0 和 stop1 处理方式相同)和
stop2(触发暂停）, suppleStop(柔顺停止)
[in] fallback_compliance 1) 碰撞后行为是安全停止或触发暂停时，该参数含义是碰撞后
回退距离， 单位: 米 2) 碰撞后行为是柔顺停止时， 该参数含义是柔顺度， 范围 [0.0, 1.0]
disableCollisionDetection()
def disableCollisionDetection(self, ec: dict)
参数 [out] ec 错误码
getSoftLimit()
def getSoftLimit(self, limits: PyTypeVectorArrayDouble2, ec: dict) -> bool
参数 [out] limits 各轴软限位 [下限, 上限]，单位: 弧度
返回 true - 已打开 | false - 已关闭
setSoftLimit()
def setSoftLimit(self, enable: bool, ec: dict, limits: list[float])
设置软限位。软限位设定要求： 1) 打开软限位时，机械臂应下电且处于手动模式; 2) 软限位不能超
过机械硬限位 3) 机械臂当前各轴角度应在设定的限位范围内
参数 [in] enable true - 打开 | false - 关闭。
[in] limits 各轴[下限, 上限]，单位：弧度。 1) 当 limits 为默认值时，视为仅打开软限
queryControllerLog()
def queryControllerLog(self, count: int, level: set[LogInfoLevel], ec: dict) -> list[LogInfo]
查询控制器最新的日志
参数 [in]  count 查询个数，上限是 10 条
[in] level 指定日志等级，空集合代表不指定
recoverState()
def recoverState(self, item: int, ec: dict)
根据选项恢复机器人状态
参数 [in]  item  恢复选项，1：急停恢复
设置导轨参数
参数 [in] name 参数名，见 value 说明
[in] value
参数            |    参数名                 |   数据类型
开关            | enable                    | bool
基坐标系        | baseFrame                | Frame
导轨名称        |  name                     | str
编码器分辨率    | encoderResolution        | int
减速比                       | reductionRatio     | float
电机最大转速(rpm)            | motorSpeed       | int
软限位(m), [下限,上限]         | softLimit           | list[float]
运动范围(m), [下限,上限]       | range              | list[float]
最大速度(m/s)                | maxSpeed          | float
最大加速度（m/s^2)           | maxAcc            | float
最大加加速度(m/s^3)          | maxJerk            | float
getRailParameter()
def getRailParameter(name, value, ec)
设置导轨参数
模板参数 参数类型
参数 [in]  name 参数名，见 setRailParameter()
[out] value  参数数值，见 setRailParameter()
[out] ec 错误码，参数名不存在或数据类型不匹配返回错误码
syncTimeWithServer()
def syncTimeWithServer(ec)
参数 [out] ec 错误码，参数名不存在或数据类型不匹配返回错误码
setMotionControlMode()
def setMotionControlMode(self, mode: MotionControlMode, ec: dict)
设置运动控制模式
参数 [in] mode 模式
moveReset()
def moveReset(self, ec: dict)
参数 [out] ec 错误码
pause()
def pause(self, ec: dict)
停止机器人运动
注解 同 stop()
参数 [out] ec： 错误码
stop()
def stop(self, ec: dict)
停止机器人运动
参数 [out] ec： 错误码
moveStart()
def moveStart(self, ec: dict)
参数 [out] ec 错误码
moveAppend() [1/2]
def moveAppend(self, cmds: list[Command], cmdID: PyString, ec: dict)
添加单条或多条运动指令, 添加后调用 moveStart()开始运动
模板参数 Command 运 动 指 令 类 : MoveJCommand | MoveAbsJCommand | MoveLCommand |
MoveCCommand | MoveCFCommand | MoveSPCommand
参数 [in] cmds 指令列表, 允许的个数为 1-100, 须为同类型的指令
moveAppend() [2/2]
def moveAppend(self, cmd: Command, cmdID: PyString, ec: dict)
添加单条运动指令, 添加后调用 moveStart()开始运动
模板参数 Command 运 动 指 令 类 : MoveJCommand | MoveAbsJCommand | MoveLCommand |
MoveCCommand | MoveCFCommand | MoveSPCommand
参数 [in] cmd 运动指令
executeCommand()
def executeCommand(self, cmds: list[Command], ec: dict)
执行单条或多条运动指令，调用后机器人立刻开始运动
模板参数 Command 运 动 指 令 类 : MoveJCommand | MoveAbsJCommand | MoveLCommand |
MoveCCommand | MoveCFCommand | MoveSPCommand;
参数 [in] cmds 指令列表, 允许的个数为 1-1000
setDefaultSpeed()
def setDefaultSpeed(self, speed: int, ec: dict)
设定默认运动速度，初始值为 100
注解 该数值表示末端最大线速度(单位 mm/s), 自动计算对应关节速度
参数 [in] speed：该接口不对参数进行范围限制。末端线速度的实际有效范围分别是 5-
4000(协作), 5-7000(工业)。 关节速度百分比划分为 5 个的范围: < 100 : 10% ；100 ~ 200 :
setDefaultZone()
def setDefaultZone(self, zone: int, ec: dict)
注解 该数值表示运动最大转弯区半径 (单位:mm), 自动计算转弯百分比 . 若不设置, 则为 0
参数 [in] zone： 该接口不对参数进行范围限制。 转弯区半径大小实际有效范围是0-200。 转
setDefaultConfOpt()
def setDefaultConfOpt(self, forced: bool, ec: dict)
参数 [in] forced true -使用运动指令的 confData 计算笛卡尔点位逆解, 如计算失败则返回错
参数 [in]  number 个数
adjustSpeedOnline()
def adjustSpeedOnline(self, scale: float, ec: dict)
动态调整机器人运动速率，非实时模式时生效。
参数 [in]  scale 运动指令的速度的比例，范围 0.01 - 1。当设置 scale 为 1 时，机器人将以路
径原本速度运动。
getAcceleration()
def getAcceleration(self, acc: float, jerk: float, ec: dict)
读取当前加/减速度和加加速度
参数 [out] acc 系统预设加速度的百分比
[out] jerk 系统预设的加加速度的百分比
adjustAcceleration()
def adjustAcceleration(self, acc: float, jerk: float, ec: dict)
调节运动加/减速度和加加速度。 如果在机器人运动中调用， 当前正在执行的指令不生效， 下一条指令
参数 [in]  acc 系统预设加速度的百分比，范围[0.2, 1.5], 超出范围不会报错，自动改为上限
[in]  jerk 系统预设的加加速度的百分比， 范围[0.1, 2], 超出范围不会报错， 自动改为上
setEventWatcher()
def setEventWatcher(self, eventType: Event, callback: typing.Callable[[dict], None], ec: dict)
参数 [in] eventType 事件类型
参数 [in] eventType 事件类型
startJog()
def startJog(self, space: JogOptSpace, rate: float, step: float, index: int, direction: bool, ec: dict)
参数 [in] space jog 参考坐标系。
[in] index 根据不同的 space，该参数含义如下：
1) 世界坐标系,基坐标系,法兰坐标系,工具工件坐标系: 0~5 分别对应 X, Y , Z, Rx, Ry,
2) 轴空间: 关节序号，从 0 开始计数
a) 6 轴机型：0~5 分别对应 X, Y , Z, J4(4轴), Ry, J6(6 轴);
b) 5 轴机型：0~4 分别对应 X, Y , Z, Ry, J5(5 轴)
[in] direction 根据不同的 space 和 index，该参数含义如下：
1) 奇异规避模式 J4: true - ±180° | false - 0°;
2) 平行基座模式 J4 & Ry: true - ±180° | false - 0°
3) 其它，true - 正向 | false - 负向
setAvoidSingularity()
参数 [in]  method 奇异规避方式
[in] enable true - 打开功能 | false - 关闭。 对于四轴锁定方式, 打开之前要确保 4 轴处
[in]  limit 不同的规避方式，该参数含义分别为:
1) 牺牲姿态: 允许的姿态误差, 范围 (0, PI*2], 单位弧度
3) 四轴锁定: 无参数
getAvoidSingularity()
参数 [in]  method 奇异规避的方式
返回 true - 已打开 | false – 已关闭
checkPath() [1/3]
checkPath(self, start: CartesianPosition, start_joint: list[float], target: CartesianPosition, ec: dict) -> list[float]
参数 [in]   start 起始点
[in]   start_joint 起始轴角 [弧度]
[in]   target 目标点
checkPath() [2/3]
def checkPath(self, start_joint: list[float], points: list[CartesianPosition], target_joint_calculated:
PyTypeVectorDouble, ec: dict) -> int
[in]   start_joint 起始轴角 [弧度]
[in]   points 笛卡尔点位，至少需要 2 个点，第一个点是起始点

### 使用说明

使用手册
使用手册
[类别]
感谢您购买本公司的机器人系统。
本手册记载了正确使用机器人的以下说明：
⚫ 机器人二次开发接口 SDK（Python）的使用。
使用该机器人系统前，请仔细阅读本手册与其他相关手册。
⚫ 机器人应用开发工程师。
请务必保证以上人员具备基础的机器人操作、Python 编程等所需的知识，并已接受本公司的相关培训。
本手册包含单独的安全章节，必须在阅读安全章节后，才能进行操作作业。
xCore 系统的机器人进行一系列控制和操作，包括实时和非实时的运动控制，机器人通信相关的读写操作，查询及
操作系统 语言
Ubuntu 18.04/20.04/22.04 默认 Python3.10.X
Windows 10 默认 Python3.12.X
xCore SDK 提供对机器人的非实时控制，主要通过给机器人发送运动指令，使用控制器内部的轨迹规划，完成路径
规划和运动执行。非实时模式提供的操作有：
⚫ 轴空间运动（MoveAbsJ）
⚫ 笛卡尔空间运动（MoveL，MoveJ，MoveC）
⚫ 机器人通信: 数字量和模拟量 I/O
⚫ 其他操作：清除报警，查询控制器日志等等
关于机器人本体和控制柜等硬件的设置，请参考《xCore 控制系统使用手册 V3.0.1》。除网络配置外，使用 xCore
xCore SDK 通过以太网（TCP/IP）连接机器人。通过有线或无线连接皆可，使用户 PC 和机器人连接同一局域网。
使用实时控制的话推荐通过有线直连到机器人。机器人配置有 2 个网口，一个是外网口，一个是直连网口。直连网
⚫ 连接方式 1： 机器人与用户PC 采用网线直连的方式连接。 如果用户工控机与机器人不处于同一个网段， 需要配
⚫ 连接方式 2： 机器人外网口连接路由器或者交换机， 用户PC 也连接路由器或者交换机， 两者处于同一局域网。
注：推荐使用方式 1 进行连接，连接方式 2 网络通信质量差时可能会造成机器人运动不稳定现象。
└── Release: 各操作系统库文件
1. 根据系统配置将对应的软件包下载到本地；
2. 创建项目后配置路径，将软件包下的 lib 路径加入到工作路径中（sys.path.append(库路径或者文件夹路径)）。
rokae::Robot 基本操作 全部支持 全部支持 全部支持
Jog 机器人 全部支持 全部支持 不支持
通信 全部支持 全部支持 部分支持
rokae::Model 运动学计算 全部支持 全部支持 不支持
rokae::RtMotionControl 实时模式 全部支持 不支持 不支持
rokae::Planner 上位机路径规划 全部支持 不支持 不支持
rokae::xMateModel 运动学和动力学计算 全部支持（仅 Linux） 不支持 不支持
查询当前操作模式 operateMode()  auto/manual
切换手自动模式 setOperateMode(mode) mode - auto/manual
查询机器人运行状态 operationState()  idle/jog/RLprogram/movin
g 等状态
获取当前末端/法兰位
posture(ct)  ct – 坐标系类型 [ X, Y, Z, Rx, Ry, Rz ]
获取当前末端/法兰位
cartPosture(ct)  ct – 坐标系类型 [ X, Y, Z, Rx, Ry, Rz ] 及
配置 NTP configNtp(server_ip) server_ip - NTP 服务端
IP
syncTimeWithServer()
设置是否使用 conf setDefaultConfOpt(forced) forced – 是/否使用
设置最大缓存指令个数  setMaxCacheSize(number) number – 个数
开始 Jog 机器人  startJog(space, rate, step,
space - 参考坐标系
rate - 速率
step - 步长
index - XYZABC/J1-7
调整速度指令 adjustSpeedOnline(per) per – 速度百分比
使用 CR 和 SR 末端的
485 通信功能
setxPanelRS485(opt, if_rs485) opt - 对外供电模式
num - 一次连续操作寄存
data_array - 发送或接收
if_crc_reverse - 是否改变
通过 xPanel 末端读写
modbus 线圈或离散输
XPRWModbusRTUCoil(slave_addr,
fun_cmd, coil_addr, num,
data_array, if_crc_reverse)
coil_addr 线圈或离散输
data_array 发送或接收数
if_crc_reverse 是否改变
通过 xPanel 末端直接
传输 RTU 协议裸数据
XPRS485SendData(send_byte,
rev_byte, send_data, rev_data)
send_byte 发送字节长度
rev_byte 接收字节长度
send_data 发送字节数据
rev_data 接收字节数据
控制器中需要有已创建好的 RL 工程，支持查询工程信息和运行。
设置力控模块使用的负
setLoad(load)  load - 负载
设置关节阻抗刚度 setJointStiffness(stiffness) stiffness - 刚度
设置笛卡尔阻抗刚度
setCartesianStiffness(stiffn
ess)
stiffness - 刚度
刚度
setCartesianNullspaceStiffn
ess(stiffness)
stiffness - 刚度
设置关节期望力矩 setJointDesiredTorque(torqu
设置笛卡尔期望力/力矩  setCartesianDesiredForce
(value)
value -期望力/力矩
setSineOverlay(line_dir,
amplify, frequency, phase,
bias)
amplify -幅值
frequency - 频率
phase - 相位
bias - 偏置
setLissajousOverlay (int
plane, double amplify_one,
double amplify_two,
frequency_two, double
phase_diff, error_code &ec)
plane - 参考平面
amplify_one - 一方向幅值
amplify_two - 二方向幅值
frequency_two - 二方向频
phase_diff 相位偏差
开启搜索运动  startOverlay()
停止搜索运动 stopOverlay()
暂停搜索运动 pauseOverlay()
restartOverlay()
setForceCondition (range,
isInside, timeout)
range - 力限制
isInside - 超出/符合限制条
setTorqueCondition (range,
isInside, timeout)
range - 力矩限制
isInside - 超出/符合限制条
setPoseBoxCondition(supe
rvising_frame, box, isInside,
supervising_frame - 长方体
isInside - 超出/符合限制条
waitCondition()
启动/关闭力控模块保护
fcMonitor(enable)  enable - 打开|关闭
大速度
setJointMaxVel(velocity) velocity – 轴速度
0 操作成功完成 无
-3 机器人急停按钮被按下, 请先恢复 恢复急停状态
-16 该操作不允许在当前模式下执行 (手动 /自动 ),
-17 该操作不允许在当前上下电状态下执行 切换上下电状态
-18 该操作不允许在机器人当前运行状态下执行 机器人非空闲，可能处于拖动 /实时模式控制/辨识
-19 该操作不允许在当前控制模式 (位置/力控)下执
切换位置控制/力控
-20 机器人运动中 停止机器人运动
-34 逆解超出机器人软限位 检查软限位设置时候合适，传入限位内位姿
-38 配置数据 cfx 错误逆解无解 检查 conf data
-41 算法失效，无法计算逆解 可能由于控制器计算问题，请反馈技术支持人员
-257 通信协议解析失败 请反馈技术支持人员
-513 切换手动/自动操作模式失败 - 停止机器人运动
- 清除伺服报警
-515 打开/关闭拖动失败 , 请检查机器人是否处于下
机器人手动模式下电时打开拖动
-10005 标定中, 或标定时重置负载失败 - 等待标定完成
- 正确设置负载
-10030 未打开仿真模式或信号不存在 打开仿真模式后再设置 DI/AI
-10040 开始拖动失败,正确设置负载并标定力矩传感器 正确地设置工具负载质量和质心；设置完成后执行
力矩传感器标定
-10065 同步 NTP 时间失败 - 安装好 NTP 功能
-10079 力控模块处于错误状态 触发了力控保护，请检查力控模式下机器人状态是
-10141 负载质量超过了机器人额定负载 使用并设置额定负载范围内的负载
- 使用其它信号
- 用匹配的数据类型读取
- 或用匹配的数据类型写入
调用 moveReset 重置
-28688 切换运动控制模式失败 - 停止机器人运动
重启控制器
-28689 该频率不支持 状态数据发送频率支持 1kHZ, 500Hz, 250Hz, 125Hz
-28706 无法执行该操作， 可能由于机器人未处于空闲状
停止机器人运动
-28707 起始位置为奇异点 运动机器人到非奇异点
-41459 处于力控模式，不允许执行的操作 停止力控后再回放路径
-50001 控制器状态错误，无法生成轨迹 调用 moveReset()重置
- 用关节方式移动机器人
- 检查 confdata 配置
-50019 生成轨迹失败 重新调整目标点的位置、 姿态和臂角(仅 7 轴机器人
-50103 笛卡尔路径终点不符合给定的 ConfData - 调用 setDefaultConfOpt(false)不使用 confdata
- 改为 MoveJ 或 MoveAbsJ
- 更改目标点 confdata
-50104 关节力矩超限 - 检查负载数值是否符合实际负载情况
- 检查机器人摩擦力系数、电机过载系数、传动过
- 如果使用了 setAvoidSingularity(lock4axis)，请检
-50113 改变的姿态超过设定的阈值 - 请规避奇异点
- 重新设置奇异规避姿态改变的阈值
- 使用其他方式的奇异规避
- 手动将机器人各轴移动到正常的工作范围内
- 更换 Jog 方式，尝试轴空间 Jog
- 将笛卡尔空间运动指令改为关节空间运动指令
-50118 改变姿态后求解的终点与所需要终点不一致 - 请规避奇异点
-50120 奇异规避下搜索路径终点角度失败 - 请规避奇异点
-50121 奇异规避下搜索路径终点角度失败 - 请规避奇异点
- 尝试更改指令形式，例如 MoveL 改为 MoveJ
-50208 内部轨迹错误 - 请调用 moveReset()重置运动指令缓存
-50401 检测到碰撞 - 请检查机器人运行环境， 确认人员、 设备安全后，
-60511 路径不存在 使用已保存的回放路径
-60702 当前四轴角度不为 0, 不允许切换到四轴固定模
请检查第四轴当前角度是否为 0°或 180°
-60704 不满足牺牲姿态奇异规避的开启条件 请检查当前状态是否满足牺牲姿态奇异规避开启
255 未初始化连接机器人 一般不会发生，正常构造 Robot 类实例即可
264 重复操作 碰撞检测已打开，需要先关闭
265 通过 UDP 端口接收数据失败，请检查网络及防
火墙配置
- 检查防火墙设置，是否允许 UDP 连接
266 客户端校验失败， 请检查控制器版本， 授权状态
和机器人型号
- 按照手册或 README 将控制器升级到匹配版本
- 创建类型匹配的机器人实例
273 点位距离过近，坐标系标定失败 参考《xCore 控制系统使用手册》工具工件标定方
513 设置了不支持的字段, 或总长度超出限制 支持的字段见 RtSupportedFields，总长度限制为
768 没有可执行的运动指令 先调用 moveAppend 下发运动指令，再开始运动
769 机器人停止中或当前状态无法暂停 可能由于调用 stop()前刚刚手动模式下电，或者按
下急停，控制器正在响应停止中，请等待
目前如果使用 xCore SDK 控制机器人，并不会限制通过 RobotAssist 的控制。机器人的一些状态，通过 xCore SDK
更改后也会体现在 Robot Assist 界面上；一些工程运行，运动控制则是分离的。大致总结如下：
会同步更新的组件 ⚫ 底部状态栏：手自动，机器人状态，上下电；
RobotAssist 修改会
⚫ 下发的运动指令无法通过点击开始按钮让机器人开始执行；
⚫ 所有机器人设置界面显示的功能打开状态和设定值等；
建议的控制方式是单一控制源，避免混淆。对于运动指令，推荐在每次使用 SDK 下发指令之前调用 moveReset()
61.     '''获取操作模式'''
62.     print_separator("get_operatemode",length=80)
63.     operate_mode = robot.operateMode(ec)
64.     print_log("operateMode",ec,f"operateMode={operate_mode}")
66. def set_operatemode(robot,ec):
67.     '''设置操作模式'''
68.     print_separator("set_operatemode",length=80)
79.     '''获取操作状态'''
80.     print_separator("get_operationState",length=80)
81.     operation_state = robot.operationState(ec)
82.     print_log("operationState",ec,f"operation_state={operation_state}")
84. def get_posture(robot,ec):
86.     print_separator("get_posture",length=80)
list[int]  confData 轴配置数据，元素个数应和机器人轴数一致
list[float]  external 外部关节角度, 单位:弧度
CartesianPositionOffsetType type 类型: Offs/RelTool
Frame frame 偏移坐标
list[float] joints 关节角度值, 单位:弧度
list[float] external 外部关节角度值, 单位:弧度
list[float] tau 期望关节扭矩，单位: Nm
double  mass 负载质量, 单位:千克
List[float]  cog 质心 [x, y, z], 单位:米
List[float]  inertia 惯量 [ix, iy, iz], 单位:千克·平方米
根据一对工具工件的坐标、负载、机器人手持设置计算得出。
Load  load 机器人末端手持负载
Frame  end 机器人末端坐标系相对法兰坐标系转换
Frame  ref 机器人参考坐标系相对世界坐标系转换
Frame frame 标定结果
List[float]  errors 样本点与 TCP 标定值的偏差, 依次为最小值,平均值,最
string name 工程名称
List[string] taskList 任务名称列表
string  name 名称
string  alias  别名, 暂未使用
bool  robotHeld 是否机器人手持
Frame  pos 位姿。工件的坐标系已相对其用户坐标系变换
Load  load 负载
JointPosition  target 目标关节点位
int  speed 末端线速度, 单位 mm/s, 关节速度根据末端线速度大小
划分几个区间，详见 setDefaultSpeed()
double jointSpeed 关节速度百分比
string customInfo 自定义信息，可在运动信息反馈中返回出来
CartesianPosition  target 目标笛卡尔点位
int  speed 末端线速度, 单位 mm/s, 关节速度根据末端线速度大小
划分几个区间，详见 setDefaultSpeed()
double jointSpeed 关节速度百分比
CartesianPosition::Offset offset 偏移量
string customInfo 自定义信息，可在运动信息反馈中返回出来
CartesianPosition  target 目标笛卡尔点位
int  speed 速率
double rotSpeed 空间旋转速度
CartesianPosition ::Offset offset 偏移量
string customInfo 自定义信息，可在运动信息反馈中返回出来
CartesianPosition  target 目标笛卡尔点位
CartesianPosition  aux 辅助点位
int  speed 速率
double rotSpeed 空间旋转速度
CartesianPositionOffset targetOffset 目标点偏移量
CartesianPositionOffset auxOffset 辅助点偏移量
string customInfo 自定义信息，可在运动信息反馈中返回出来
CartesianPosition  target 目标笛卡尔点位
CartesianPosition  aux 辅助点位
int  speed 速率
double rotSpeed 空间旋转速度
double angle 全圆执行角度, 单位: 弧度
CartesianPosition ::Offset targetOffset 目标点偏移量
CartesianPosition ::Offset auxOffset 辅助点偏移量
RotType rotType 全圆姿态旋转模式
string customInfo 自定义信息，可在运动信息反馈中返回出来
CartesianPosition  target 终点笛卡尔点位
CartesianPositionOffset targetOffset 偏移选项
double radius 初始半径, 单位: 米
double radius_step 每旋转单位角度，半径的变化，单位: 米/弧度
double angle 合计旋转角度, 单位: 弧度
bool direction 旋转方向, true - 顺时针 | false - 逆时针
string customInfo 自定义信息，可在运动信息反馈中返回出来
duration_ 停留时长, 最小有效时长 1ms
string  timestamp 日期及时间
string  content 日志内容
string  repair 修复办法
bool key1_state CR1 号
bool key2_state CR2 号
bool key3_state CR3 号
bool key4_state CR4 号
bool key5_state CR5 号
bool key6_state CR6 号
bool key7_state CR7 号
def connectToRobot(self, ec: dict)
查询机器人当前操作模式
注解 此工具工件组仅为 SDK 运动控制使用, 不与 RL 工程相关.
注解 此工具工件组仅为 SDK 运动控制使用 , 不与 RL 工程相关 . 除此接口外 , 如果通过
RobotAssist 更改默认工具工件(右上角的选项), 该工具工件组也会相应更改.
手动同步一次时间，远端 IP 是通过 configNtp 配置的。耗时几秒钟，阻塞等待同步完成，接口预设的
设置是否使用轴配置数据(confData)计算逆解。初始值为 false
误; false - 不使用，逆解时会选取机械臂当前轴角度的最近解
setMaxCacheSize()
def setMaxCacheSize(self, number: int, ec: dict)
设置最大缓存指令个数，指发送到控制器待规划的路径点个数，允许的范围[1,300]，初始值为 30。
注解 如果轨迹多为短轨迹， 可以调大这个数值， 避免因指令发送不及时导致机器人停止运动
(停止后如果有未执行的指令，可 moveStart()继续;
时间较长的操作;
2) Event::safety 则每次独立线程回调, 没有执行时间的限制
queryEventInfo()
queryEventInfo(self, eventType: Event, ec: dict) -> dict
开始 jog 机器人，需要切换到手动操作模式。
来结束 jog 操作，否则机器人会一直处于 jog 的运行状态。
1) 工具/工件坐标系使用原则同 setToolset();
2) 工 业 六 轴 机 型 和 xMateCR/SR 六 轴 机 型 支 持 两 种 奇 异 规 避 方 式 Jog ：
Space::singularityAvoidMode, Space::baseParallelMode
3) CR5 轴机型支持平行基座模式 Jog：Space::baseParallelMode
[in] rate 速率, 范围 0.01 - 1
[in] step 步长。单位: 笛卡尔空间-毫米 | 轴空间-度。步长大于 0 即可，不设置上限，
如果机器人机器人无法继续 jog 会自行停止运动。
in] num 一次连续操作寄存器的个数  0-3，类型为 int16/uint16 时，最大为 3；类型为
[in/out] data_array 发送或接收数据的数组，非 const，功能码为 0x06 时，只使用此数组
in] if_crc_reverse 是否改变 CRC 校验高低位，默认 false，少数厂家末端工具需要反转
XPRWModbusRTUCoil()
def XPRWModbusRTUCoil(self, slave_addr: int, fun_cmd: int, coil_addr: int, num: int, data_array: list[bool],
if_crc_reverse: bool, ec: dict)
通过 xPanel 末端读写 modbus 线圈或离散输入
[in/out] data_array 发送或接收数据的数组，非 const，功能码为 0x05 时，只使用此数组
[in] if_crc_reverse 是否改变 CRC 校验高低位，默认 false，少数厂家末端工具需要反转
XPRS485SendData()
def XPRWModbusRTUReg(self, slave_addr: int, fun_cmd: int, reg_addr: int, data_type: str, num: int,
data_array: list[int], if_crc_reverse: bool, ec: dict)
通过 xPanel 末端直接传输 RTU 协议裸数据
返回 末端按键的状态。 末端按键编号见 《xCore 机器人控制系统使用手册》 末端把手的图示。
projectsInfo()
def projectsInfo(self, ec: dict) -> list[RLProjectInfo]
设置力控模块使用的负载信息，fcStart()之后可调用。

### API接口

xCore SDK (Python)
xCore SDK(Python)
V1.6 2022.10 Rokae SDK 初版，适配 xCore 版本 v1.6.1；
V1.7 2023.02 Rokae SDK 正式版本，适配 xCore 版本 v1.7；
V2.0 2023.05 添加部分运动接口
V2.1 2023.11 xCore SDK(v0.1.8)：适配焊接相关接口
V2.2 2024.03 xCore SDK(v0.1.11)：完善焊接相关接口
V2.2 2024.08 xCore SDK(v0.4.1)：新增力控相关接口，移除焊接相关接口
V3.0 2024.12 xCore SDK(v0.5.0)：新增导轨相关接口
xCore SDK 编程接口库是协作机器人厂商H机器人提供给客户用于二次开发的软件产品，通过编程接口库，客户可以对 配套了
⚫ 机器人型号：支持控制所有机型，根据协作和工业机器人支持的功能不同，可调用的接口有所差别。
SDK 无需其他额外的硬件设置。
无需通过 RobotAssist 进行任何设置，用户可直接用 xCore SDK 控制机器人。
librokae
下表是各语言版本接口支持情况概览。
模块 API 功能 C++ Python Android
根据机器人构型和轴数不同，Python 版本的 SDK 提供了下列几个可供实例化的 Robot 类，初始化时会检查所选构
型是否和连接的机器人匹配：
类名 适用机型
xMateRobot 协作 6 轴
xMateErProRobot 协作 7 轴
xMateCr5Robot 协作 CR5 轴
StandardRobot 工业 6 轴
PCB4Robot 工业 4 轴
PCB3Robot 工业 3 轴
查询 SDK 版本号 sdkVersion()  版本号
非实时模式运动控制相关接口。
设置接收事件的回调函数  setEventWatcher(eventTyp
e, callback)
eventType – 事件类型
callback – 处理事件的回
函数
执行运动指令 executeCommand(comma
command - 一条或多条
MoveL/MoveJ/MoveAbsJ/
MoveC/MoveCF/MoveSP
读取当前加速度 getAcceleration(acc, jerk)  acc – 加速度
jerk – 加加速度
设置运动加速度  adjustAcceleration(acc,  acc – 加速度
jerk)  jerk – 加加速度
setAvoidSingularity(metho
d, enable, threshold)
enable – 打开/关闭
checkPath(start, start_joint,
target)
start - 起始点
start_joint - 起始轴角
target - 目标点
校验多个直线轨迹 checkPath(start_joint,
points,
target_joint_calculated)
start_joint -起始轴角，单
points - 笛卡尔点位，至
target_joint_calculated - 若
若校验失败，返回 points
checkPath(start, start_joint,
aux, target, angle, rot_type)
start - 起始点
start_joint - 起始轴角
aux - 辅助点
target - 目标点
angle - 全圆执行角度，不
rot_type - 全圆旋转类型
if_rs485 - 接口工作模
式，是否打开末端 485
通信
通过 xPanel 末端读写
modbus 寄存器
XPRWModbusRTUReg(slave_addr,
fun_cmd, reg_addr, data_type, num,
data_array, if_crc_reverse)
data_type - 支持的数据
类型
非实时接口的调用结果通过错误码反馈， 每个接口都会传入一个错误码ec， 可通过message(ec)， 或者ec[“message”]
实时模式下发送运动指令、周期调度、读取状态数据等接口在调用过程中会抛出异常。
数值 错误信息 原因及处理方法
-258 未找到匹配的数据名称 可能由于控制器和 SDK 版本不适配
-259 未找到匹配的指令名称 可能由于控制器和 SDK 版本不适配
-260 数据值错误, 可能是通信协议不匹配 可能由于控制器和 SDK 版本不适配
-272 未找到要查询的数据名称 可能由于控制器和 SDK 版本不适配
-273 数据不可读 可能由于控制器和 SDK 版本不适配
-288 数据不可写 可能由于控制器和 SDK 版本不适配
-338 录制的路径中存在超过关节软限位的情况。 请重
-339 录制的路径中存在关节速度过快的情况 , 请重
-340 未从机器人静止状态开始录制路径 机器人静止时再开始录制
-341 停止录制路径时机器人未停止运动 机器人静止时再停止录制
-342 机器人处于下电状态, 保存路径失败 机器人上电
-353 保存路径到磁盘失败 重新录制拖动轨迹，或重启机器人
- 实例类型错误或 SDK 未授权，连接被拒绝
257 无法解析机器人消息, 可能由于 SDK 版本与控
可能由于控制器和 SDK 版本不适配
- 联系技术支持人员授权 SDK 功能
272 事件未监听 先调用 setEventWatcher 开始监听数据
接口来重置运动缓存。
1. import xCoreSDK_python
2. from log import print_log,print_separator
4. def base_op(robot,ec):
5.     print_separator("base_op",length=110)
6.     disconnect(robot,ec)
8.     get_sdk_version(robot)
9.     get_powerstate(robot,ec)
10.     set_powerstate(robot,ec)
11.     get_operatemode(robot,ec)
12.     set_operatemode(robot,ec)
13.     get_robotinfo(robot,ec)
14.     get_operationState(robot,ec)
15.     get_posture(robot,ec)
16.     get_cart_posture(robot,ec)
17.     get_joint_pos(robot,ec)
18.     get_joint_vel(robot,ec)
19.     get_joint_torque(robot,ec)
20.     get_baseframe(robot,ec)
21.     set_baseframe(robot,ec)
22.     get_toolset(robot,ec)
23.     set_toolset(robot,ec)
24.     set_toolset_by_name(robot,ec)
25.     clear_servo_alarm(robot,ec)
26.     calcFk(robot,ec)
27.     calcIk(robot,ec)
28.     get_soft_limit(robot,ec)
29.     set_soft_limit(robot,ec)
30.     restore_soft_limit(robot,ec)
32. def disconnect(robot,ec):
33.     '''断开连接机器人'''
34.     print_separator("disconnect",length=80)
35.     robot.disconnectFromRobot(ec)
36.     print_log("disconnectFromRobot",ec)
39.     '''连接机器人'''
42. def get_sdk_version(robot):
43.     '''获取 sdk 版本'''
44.     print_separator("get_sdk_version",length=80)
45.     sdk_version = robot.sdkVersion()
46.     print(f"sdkVersion={sdk_version}")
48. def get_powerstate(robot,ec):
50.     print_separator("get_powerstate",length=80)
51.     power_state =  robot.powerState(ec)
52.     print_log("powerState",ec,f"powerState={power_state}")
54. def set_powerstate(robot,ec):
55.     '''设置机器人上下电状态，true：上电，false：下电'''
56.     print_separator("set_powerstate",length=80)
57.     robot.setPowerState(True,ec)
58.     print_log("setPowerState",ec)
60. def get_operatemode(robot,ec):
69.     robot.setOperateMode(xCoreSDK_python.OperateMode.automatic,ec)
70.     print_log("setOperateMode",ec)
72. def get_robotinfo(robot,ec):
73.     '''获取机器人信息'''
74.     print_separator("get_robotinfo",length=80)
print_log("robotInfo",ec,f"{robot_info.id,robot_info.version,robot_info.type,robot_info.joint_num}")
78. def get_operationState(robot,ec):
87.     pos = robot.posture(xCoreSDK_python.CoordinateType.endInRef, ec)
88.     print_log("posture",ec,', '.join(map(str, pos)))
90. def get_cart_posture(robot,ec):
92.     print_separator("get_cart_posture",length=80)
93.     cart_posture = robot.cartPosture(xCoreSDK_python.CoordinateType.endInRef, ec)
94.     print_log("cartPosture",ec)
95.     print(f"elbow,{cart_posture.elbow}")
96.     print(f"hasElbow,{cart_posture.hasElbow}")
97.     print(f"confData,f{','.join(map(str,cart_posture.confData))}")
98.     print(f"external size,{len(cart_posture.external)}")
99.     print(f"trans,{','.join(map(str,cart_posture.trans))}")
100.     print(f"rpy,{','.join(map(str,cart_posture.rpy))}")
101.     print(f"pos,{','.join(map(str,cart_posture.pos))}")
103. def get_joint_pos(robot,ec):
104.     '''获取关节位置'''
105.     print_separator("get_joint_pos",length=80)
106.     joint_pos = robot.jointPos(ec)
107.     print_log("jointPos",ec,','.join(map(str,joint_pos)))
109. def get_joint_vel(robot,ec):
110.     '''获取关节速度'''
111.     print_separator("get_joint_vel",length=80)
112.     joint_vel = robot.jointVel(ec)
113.     print_log("jointVel",ec,','.join(map(str,joint_vel)))
115. def get_joint_torque(robot,ec):
116.     '''获取当前关节力矩'''
117.     print_separator("get_joint_torque",length=80)
119.     print_log("jointTorque",ec,','.join(map(str,joint_torque)))
121. def get_baseframe(robot,ec):
123.     print_separator("get_baseframe",length=80)
124.     baseframe = robot.baseFrame(ec)
125.     print_log("baseFrame",ec,','.join(map(str,baseframe)))
127. def set_baseframe(robot,ec):
129.     print_separator("set_baseframe",length=80)
130.     frame= xCoreSDK_python.Frame()
131.     robot.setBaseFrame(frame,ec)
132.     print_log("setBaseFrame",ec)
134. def get_toolset(robot,ec):
136.     print_separator("get_toolset",length=80)
137.     toolset = robot.toolset(ec)
138.     print_log("toolset",ec)
140.           load mass: {toolset.load.mass}
141.           load cog: {', '.join(map(str, toolset.load.cog))}
142.           load inertia:{','.join(map(str,toolset.load.inertia))}
143.           end trans:{','.join(map(str,toolset.end.trans))}
144.           end rpy:{','.join(map(str,toolset.end.rpy))}
145.           end pos:{','.join(map(str,toolset.end.pos))}
146.           ref trans:{','.join(map(str,toolset.ref.trans))}
147.           ref rpy:{','.join(map(str,toolset.ref.rpy))}
148.           ref pos:{','.join(map(str,toolset.ref.pos))}
151. def set_toolset(robot,ec):
153.     print_separator("set_toolset",length=80)
154.     toolset = xCoreSDK_python.Toolset()
201.     cart_pos = xCoreSDK_python.CartesianPosition([0.614711,0.136,0.416211, -1.57,0,-1.57])
#s4 拖拽位姿
203.     joint_pos = robot_model.calcIk(cart_pos,ec)
204.     print_log("calcIk",ec,','.join(map(str,joint_pos)))
206. def get_soft_limit(robot,ec):
208.     print_separator("get_soft_limit",length=80)
209.     soft_limits = xCoreSDK_python.PyTypeVectorArrayDouble2()
210.     robot.getSoftLimit(soft_limits, ec)
211.     limits_content = soft_limits.content()
212.     print_log("soft_limit",ec,limits_content)
214. def set_soft_limit(robot,ec):
216.     print_separator("set_soft_limit",length=80)
218.     robot.setPowerState(False, ec)
219.     print_log("setPowerState",ec)
220.     robot.setOperateMode(xCoreSDK_python.OperateMode.manual, ec)
221.     print_log("setOperateMode",ec)
222.     robot.setSoftLimit(False, ec) # 关闭软限位
223.     print_log("setSoftLimit",ec)
226.     soft_limits = [[ -2.0543261909900767, 2.0543261909900767], [ -1.356194490192345,
227.     robot.setSoftLimit(True, ec,soft_limits)
228.     print_log("setSoftLimit",ec)
230. def restore_soft_limit(robot,ec):
232.     print_separator("restore_soft_limit",length=80)
234.     robot.setPowerState(False, ec)
235.     print_log("setPowerState",ec)
236.     robot.setOperateMode(xCoreSDK_python.OperateMode.manual, ec)
237.     print_log("setOperateMode",ec)
238.     robot.setSoftLimit(False, ec) # 关闭软限位
239.     print_log("setSoftLimit",ec)
242.     sr4_default_limit = [[ -6.283185307179586, 6.283185307179586], [ -2.356194490192345,
6.283185307179586]] # sr4 默认软限位
243.     soft_limits = sr4_default_limit
244.     robot.setSoftLimit(True, ec,soft_limits)
245.     print_log("setSoftLimit",ec)
248. if __name__ == "__main__":
250.         # 连接机器人
251.         # 不同的机器人对应不同的类型
252.         ip = "10.0.40.129"
253.         robot = xCoreSDK_python.xMateRobot(ip)
255.         base_op(robot,ec)
256.     except Exception as e:
257.         print(f"An error occurred: {e}")
Idle = 0 机器人静止
Jog = 1 Jog 机器人中
rtControlling = 2 实时模式控制中
Drag = 3 拖动已开启
rlProgram = 4 RL 工程运行中
sdkVersion()
def sdkVersion() -> str
查询 RokaeSDK 版本
setRailParameter()
def setRailParameter(name, value, ec)
注解 在调用各运动控制接口之前, 须设置对应的控制模式。
注解 Robot 类在初始化时会调用一次运动重置。RL 程序和 SDK 运动指令切换控制，需要先
注解 目前支持 stop2 停止类型, 规划停止不断电, 参见 StopLevel。 调用此接口后, 已经下发
设置接收事件的回调函数
[in] callback 处理事件的回调函数。说明:
1) 对于 Event::moveExecution, 回调函数在同一个线程执行 , 请避免函数中有执行
查询事件信息。与 setEventWatcher()回调时的提供的信息相同，区别是这个接口是主动查询的方式
注解 调用此接口并且机器人开始运动后，无论机器人是否已经自行停止，都必须调用 stop()
def setAvoidSingularity(self, method: AvoidSingularityMethod, enable: bool, threshold: float, ec: dict)
1) 四轴锁定: 支持工业六轴，xMateCR 和 xMateSR 六轴机型；
2) 牺牲姿态: 支持所有六轴机型；
def getAvoidSingularity(self, method: AvoidSingularityMethod, ec: dict) -> bool
返回 True -开 | False -关 | None-该接口不存在
getDO()
def getDO(self, board: int, port: int, ec: dict) -> bool
返回 True -开 | False -关 | None-该接口不存在
setDO()
def setDO(self, board: int, port: int, state: bool, ec: dict)
[in] if_rs485 接口工作模式，是否打开末端 485 通信 t
XPRWModbusRTUReg()
def XPRWModbusRTUReg(self, slave_addr: int, fun_cmd: int, reg_addr: int, data_type: str, num: int,
data_array: list[int], if_crc_reverse: bool, ec: dict)
通过 xPanel 末端读写 modbus 寄存器
[in] data_type 支持的数据类型  int32、int16、uint32、uint16

### 示例代码

├── example: 示例程序
├── CHANGELOG.md: 版本变更记录
本章展示一些 Python 非实时控制示例程序，更多示例请见软件包中 examples。
dynamicIdentify = 6 动力学辨识中
loadIdentify = 8 负载辨识中
Moving = 9 机器人运动中
Jogging = 10 jog 运动中
Unknown = -1 未知
industrial 工业机器人
collaborative 协作机器人
manual 手动
automatic 自动
unknown 未知(发生异常)
Estop = 2 急停被按下
Gstop = 3  安全门打开
Unknown = -1 未知(发生异常)
flangeInBase 法兰相对于基坐标系
endInRef 末端相对于外部坐标系
NrtCommand 非实时模式执行运动指令
NrtRLTask 非实时模式运行 RL 工程
RtCommand 实时模式控制（暂不支持）
注：目前仅支持 stop2
stop0 快速停止机器人运动后断电
stop1 规划停止机器人运动后断电, 停在原始路径上
stop2 规划停止机器人运动后不断电, 停在原始路径上
suppleStop 柔顺停止，仅适用于协作机型
DragParameterSpace.jointSpace = 0 轴空间拖动
DragParameterSpace.cartesianSpace = 1 笛卡尔空间拖动
DragParameterType.translationOnly = 0 仅平移
DragParameterType.rotationOnly = 1 仅旋转
DragParameterType.freely = 2 自由拖拽
world 世界坐标系
base 基坐标系
flange 法兰坐标系
wobj 工件坐标系
path 路径坐标系, 力控任务坐标系需要跟踪轨迹变化的过程
rail 导轨基坐标系
world 世界坐标系
flange 法兰坐标系
baseFrame 基坐标系
toolFrame 工具坐标系
wobjFrame 工件坐标系
jointSpace 轴空间
singularityAvoidMode 奇异规避模式，适用于工业六轴, xMateCR 和 xMateSR
baseParallelMode 平行基座模式，适用于工业六轴, xMateCR 和 xMateSR
lockAxis4 四轴锁定
wrist 牺牲姿态
jointWay 轴空间短轨迹插补
constPose 不变姿态
rotAxis 动轴旋转
fixedAxis 定轴旋转
reserve 保留
supply12v 输出 12V
supply24v 输出 24V
moveExecution 非实时运动指令执行信息
safety 安全 (是否碰撞)
string  id 机器人 uid, 可用于区分连接的机器人
string  version 控制器版本
string  type 机器人机型名称
list[float] trans 平移量, [X, Y , Z], 单位:米
list[float] rpy XYZ 欧拉角, [A, B, C], 单位:弧度
list[float] pos 行优先变换矩阵
list[float] trans 平移量, [x, y, z], 单位:米
list[float] rpy XYZ 欧拉角, [A, B, C], 单位:弧度
double  elbow 臂角, 适用于 7 轴机器人, 单位：弧度
bool  hasElbow 是否有臂角

---
